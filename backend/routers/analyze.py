"""
JobShield AI — Analysis API Routes

Endpoints for text analysis and screenshot scanning.
Delegates heavy processing and score synthesis to the Orchestrator Service.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from limiter import limiter
from services.orchestrator import run_analysis_pipeline
from services.ocr_service import extract_text_from_image
from services.gemini_search_analyzer import extract_text_from_image_gemini

logger = logging.getLogger("jobshield.analyze")
router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

# Thread pool for OCR processing
_ocr_executor = ThreadPoolExecutor(max_workers=4)

MAX_TEXT_LENGTH = 50_000


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
@limiter.limit("30/minute")
async def analyze_text_endpoint(request: Request, body: TextAnalysisRequest):
    """
    Analyze pasted text (job description, email, chat message) for scam indicators.
    All heavy steps run concurrently via the Orchestrator.
    """
    text = body.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text too short for meaningful analysis")

    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text exceeds maximum allowed length of {MAX_TEXT_LENGTH} characters."
        )

    return await run_analysis_pipeline(text, body.source_type or "job_posting")


@router.post("/screenshot")
@limiter.limit("10/minute")
async def analyze_screenshot_endpoint(
    request: Request,
    file: UploadFile = File(...),
    source_type: str = Form("whatsapp"),
):
    """
    Upload a screenshot for OCR extraction and scam analysis.
    Supported formats: PNG, JPG, JPEG, WebP.
    Uses Gemini Vision as primary OCR engine, falling back to EasyOCR.
    """
    # Validate and normalise file type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    content_type = file.content_type or "image/png"
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Use PNG, JPG, or WebP."
        )
    mime_type = "image/jpeg" if content_type == "image/jpg" else content_type

    # Read file bytes
    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

    loop = asyncio.get_running_loop()

    # ── Step 1: OCR — try Gemini Vision first, fallback to EasyOCR ──
    ocr_result = await loop.run_in_executor(
        _ocr_executor,
        lambda: extract_text_from_image_gemini(image_bytes, mime_type),
    )

    if not ocr_result.get("success") or not ocr_result.get("extracted_text", "").strip():
        logger.info(f"Gemini Vision OCR unavailable/empty, falling back to EasyOCR. Reason: {ocr_result.get('error', 'empty result')}")
        try:
            ocr_result = await loop.run_in_executor(
                _ocr_executor,
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
    analysis = await run_analysis_pipeline(extracted_text, source_type)

    return {
        "ocr_result": {
            "extracted_text": extracted_text,
            "confidence": ocr_result.get("confidence", 0.0),
            "line_count": ocr_result.get("line_count", 0),
            "engine": ocr_result.get("engine", "easyocr"),
        },
        "analysis": analysis,
    }


# Backwards compatibility alias
_run_analysis_async = run_analysis_pipeline
