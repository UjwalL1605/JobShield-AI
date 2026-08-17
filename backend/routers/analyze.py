"""
JobShield AI — Analysis API Routes

Endpoints for text analysis and screenshot scanning.
Optimized: independent pipeline steps run concurrently via asyncio.gather()
and CPU-bound work (OCR, ML) is offloaded to a thread-pool so the event loop never blocks.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.nlp_analyzer import get_analyzer
from services.rule_engine import analyze_text as rule_analyze, get_trust_level
from services.email_checker import analyze_emails_in_text
from services.salary_checker import check_salary
from services.ocr_service import extract_text_from_image
from services.web_verifier import analyze_web_intelligence
from services.gemini_search_analyzer import analyze_with_gemini_search, extract_text_from_image_gemini
from database.db import check_text_for_known_scams

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Shared thread-pool for CPU-bound / blocking I/O tasks (OCR, ML inference, Gemini HTTP)
_executor = ThreadPoolExecutor(max_workers=4)


# ─── Request / Response Models ───────────────────────────────────────────────────

class TextAnalysisRequest(BaseModel):
    text: str
    source_type: Optional[str] = "job_posting"  # job_posting, email, whatsapp, linkedin, other


class AnalysisResponse(BaseModel):
    scam_probability: float
    trust_level: str
    ml_score: float
    rule_score: float
    risk_factors: list
    scam_keywords: list
    email_analysis: dict
    salary_analysis: dict
    known_scam_warnings: list
    ml_top_features: list
    web_intelligence: dict
    gemini_analysis: Optional[dict] = None
    original_text: str
    source_type: str


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/text", response_model=AnalysisResponse)
async def analyze_text_endpoint(request: TextAnalysisRequest):
    """
    Analyze pasted text (job description, email, chat message) for scam indicators.
    All heavy steps run concurrently — typical response time reduced significantly.
    """
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text too short for meaningful analysis")

    return await _run_analysis_async(text, request.source_type)


@router.post("/screenshot")
async def analyze_screenshot_endpoint(
    file: UploadFile = File(...),
    source_type: str = Form("whatsapp"),
):
    """
    Upload a screenshot for OCR extraction and scam analysis.
    Supported formats: PNG, JPG, JPEG, WebP.
    Uses Gemini Vision (fast, ~5s) as primary OCR engine.
    Falls back to EasyOCR if Gemini is unavailable.
    """
    # Validate and normalise file type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    content_type = file.content_type or "image/png"
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Use PNG, JPG, or WebP."
        )
    # Normalise image/jpg → image/jpeg for Gemini
    mime_type = "image/jpeg" if content_type == "image/jpg" else content_type

    # Read file bytes
    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

    loop = asyncio.get_running_loop()

    # ── Step 1: OCR — try Gemini Vision first (fast ~3-8s), fallback to EasyOCR ──
    ocr_result = await loop.run_in_executor(
        _executor,
        lambda: extract_text_from_image_gemini(image_bytes, mime_type),
    )

    # If Gemini Vision failed or unavailable, fall back to EasyOCR
    if not ocr_result.get("success") or not ocr_result.get("extracted_text", "").strip():
        print(f"[INFO] Gemini Vision OCR unavailable/empty, falling back to EasyOCR. Reason: {ocr_result.get('error', 'empty result')}")
        try:
            ocr_result = await loop.run_in_executor(
                _executor,
                extract_text_from_image,
                image_bytes,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"OCR processing error: {exc}")

    if not ocr_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=ocr_result.get("error", "OCR failed — install easyocr or configure GEMINI_API_KEY."),
        )

    extracted_text = ocr_result.get("extracted_text", "")

    if not extracted_text or len(extracted_text) < 5:
        return {
            "ocr_result": ocr_result,
            "analysis": None,
            "message": "No meaningful text could be extracted from the image.",
        }

    # ── Step 2: Run full concurrent scam analysis on extracted text ──────────────
    analysis = await _run_analysis_async(extracted_text, source_type)

    return {
        "ocr_result": {
            "extracted_text": extracted_text,
            "confidence": ocr_result.get("confidence", 0.0),
            "line_count": ocr_result.get("line_count", 0),
            "engine": ocr_result.get("engine", "easyocr"),
        },
        "analysis": analysis,
    }


# In-memory LRU-like cache for ultra-fast repeated/preset queries (<1ms)
_analysis_cache = {}
_CACHE_MAX_SIZE = 200


# ─── Core Analysis Logic (Concurrent Async Pipeline) ────────────────────────────

async def _run_analysis_async(text: str, source_type: str) -> dict:
    """
    Run the complete scam analysis pipeline concurrently with in-memory caching.
    """
    cache_key = f"{source_type}:{hash(text.strip())}"
    if cache_key in _analysis_cache:
        return _analysis_cache[cache_key]

    loop = asyncio.get_running_loop()

    # ── Group 1: Fast local CPU/IO work — bundled in one thread-pool call ───────
    def _local_bundle():
        analyzer       = get_analyzer()
        ml_result      = analyzer.predict(text)
        rule_result    = rule_analyze(text)
        email_result   = analyze_emails_in_text(text)
        salary_result  = check_salary(text)
        known_warnings = check_text_for_known_scams(text)
        web_intel      = analyze_web_intelligence(text, source_type)
        return ml_result, rule_result, email_result, salary_result, known_warnings, web_intel

    # ── Group 2: Gemini AI — network I/O, run in a separate thread ───────────────
    def _gemini_bundle():
        try:
            return analyze_with_gemini_search(text, source_type)
        except Exception as e:
            # Never let a Gemini failure crash the whole pipeline
            return {
                "available": False,
                "error": str(e),
                "message": "AI web search could not be completed.",
            }

    # Run both groups concurrently — total time ≈ max(local, gemini), not sum
    (
        (ml_result, rule_result, email_result, salary_result, known_warnings, web_intel),
        gemini_result,
    ) = await asyncio.gather(
        loop.run_in_executor(_executor, _local_bundle),
        loop.run_in_executor(_executor, _gemini_bundle),
    )

    # ── Combine scores ────────────────────────────────────────────────────────────
    ml_score   = ml_result["ml_score"]
    rule_score = rule_result["rule_score"]

    if gemini_result.get("available") and "scam_score" in gemini_result:
        gemini_score   = gemini_result["scam_score"]
        combined_score = (gemini_score * 0.40) + (ml_score * 0.35) + (rule_score * 0.25)
    else:
        combined_score = (ml_score * 0.60) + (rule_score * 0.40)

    # Boost for web intelligence signals (brand impersonation, high-risk TLDs)
    if web_intel.get("risk_boost"):
        combined_score += web_intel["risk_boost"]

    # Boost if known scam identifiers found in threat registry
    if known_warnings:
        combined_score += 20  # Significant boost for known threat

    # Boost for email/salary red flags
    if email_result.get("overall_risk") == "high":
        combined_score += 10
    if salary_result.get("risk_level") == "high":
        combined_score += 8

    # Append web intelligence risk signals to itemized risk factors
    combined_risk_factors = list(rule_result["risk_factors"])
    for sig in web_intel.get("risk_signals", []):
        combined_risk_factors.append({
            "category":    sig["type"],
            "severity":    sig["severity"],
            "description": sig["title"],
            "matches":     [sig["detail"]],
        })

    combined_score = min(100.0, max(0.0, combined_score))
    trust_level    = get_trust_level(combined_score)

    res = {
        "scam_probability":    round(combined_score, 1),
        "trust_level":         trust_level,
        "ml_score":            ml_score,
        "rule_score":          round(rule_score, 1),
        "risk_factors":        combined_risk_factors,
        "scam_keywords":       rule_result["scam_keywords"],
        "email_analysis":      email_result,
        "salary_analysis":     salary_result,
        "known_scam_warnings": known_warnings,
        "ml_top_features":     ml_result.get("top_features", []),
        "web_intelligence":    web_intel,
        "gemini_analysis":     gemini_result,
        "original_text":       text,
        "source_type":         source_type,
    }

    # Store in memory cache
    if len(_analysis_cache) >= _CACHE_MAX_SIZE:
        _analysis_cache.pop(next(iter(_analysis_cache)))
    _analysis_cache[cache_key] = res

    return res
