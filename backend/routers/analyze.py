"""
JobShield AI — Analysis API Routes

Endpoints for text analysis and screenshot scanning.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.nlp_analyzer import get_analyzer
from services.rule_engine import analyze_text as rule_analyze, get_trust_level
from services.email_checker import analyze_emails_in_text
from services.salary_checker import check_salary
from services.ocr_service import extract_text_from_image
from services.web_verifier import analyze_web_intelligence
from database.db import check_text_for_known_scams

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])


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
    original_text: str
    source_type: str


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/text", response_model=AnalysisResponse)
async def analyze_text_endpoint(request: TextAnalysisRequest):
    """
    Analyze pasted text (job description, email, chat message) for scam indicators.
    """
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text too short for meaningful analysis")

    return _run_analysis(text, request.source_type)


@router.post("/screenshot")
async def analyze_screenshot_endpoint(
    file: UploadFile = File(...),
    source_type: str = Form("whatsapp"),
):
    """
    Upload a screenshot for OCR extraction and scam analysis.
    Supported formats: PNG, JPG, JPEG, WebP
    """
    # Validate file type
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use PNG, JPG, or WebP."
        )

    # Read file
    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

    # Run OCR
    ocr_result = extract_text_from_image(image_bytes)

    if not ocr_result["success"]:
        raise HTTPException(status_code=500, detail=ocr_result.get("error", "OCR failed"))

    extracted_text = ocr_result["extracted_text"]

    if not extracted_text or len(extracted_text) < 5:
        return {
            "ocr_result": ocr_result,
            "analysis": None,
            "message": "No meaningful text could be extracted from the image.",
        }

    # Run scam analysis on extracted text
    analysis = _run_analysis(extracted_text, source_type)

    return {
        "ocr_result": {
            "extracted_text": extracted_text,
            "confidence": ocr_result["confidence"],
            "line_count": ocr_result.get("line_count", 0),
        },
        "analysis": analysis,
    }


# ─── Core Analysis Logic ────────────────────────────────────────────────────────

def _run_analysis(text: str, source_type: str) -> dict:
    """Run complete scam analysis pipeline on text with ML, rules, and web intelligence."""

    # 1. ML Model prediction
    analyzer = get_analyzer()
    ml_result = analyzer.predict(text)

    # 2. Rule-based analysis
    rule_result = rule_analyze(text)

    # 3. Email analysis
    email_result = analyze_emails_in_text(text)

    # 4. Salary analysis
    salary_result = check_salary(text)

    # 5. Check against known scam database
    known_warnings = check_text_for_known_scams(text)

    # 6. Web & Entity Intelligence (Google Search & Domain Reputation)
    web_intel = analyze_web_intelligence(text, source_type)

    # 7. Combine scores (weighted average + domain/threat intelligence)
    ml_score = ml_result["ml_score"]
    rule_score = rule_result["rule_score"]

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
            "category": sig["type"],
            "severity": sig["severity"],
            "description": sig["title"],
            "matches": [sig["detail"]],
        })

    combined_score = min(100.0, max(0.0, combined_score))
    trust_level = get_trust_level(combined_score)

    return {
        "scam_probability": round(combined_score, 1),
        "trust_level": trust_level,
        "ml_score": ml_score,
        "rule_score": round(rule_score, 1),
        "risk_factors": combined_risk_factors,
        "scam_keywords": rule_result["scam_keywords"],
        "email_analysis": email_result,
        "salary_analysis": salary_result,
        "known_scam_warnings": known_warnings,
        "ml_top_features": ml_result.get("top_features", []),
        "web_intelligence": web_intel,
        "original_text": text,
        "source_type": source_type,
    }
