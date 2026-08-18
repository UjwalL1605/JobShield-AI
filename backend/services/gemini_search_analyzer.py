"""
JobShield AI — Google Gemini AI Deep Search Analyzer

Uses Google Gemini with Google Search Grounding to perform real-time
web intelligence lookups, verify company legitimacy, and cross-reference
known scam reports on Reddit, Glassdoor, Quora, and official registries.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger("jobshield.gemini")

# Load environment variables from backend/.env explicitly
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

_client = None


def get_genai_client():
    """Get or initialize Google GenAI client if API key is present."""
    global _client
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return None

    if _client is None:
        try:
            from google import genai
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize Google GenAI Client: {e}")
            return None

    return _client


def analyze_with_gemini_search(text: str, source_type: Optional[str] = "job_posting") -> Dict:
    """
    Analyze job offer / message using Google Gemini with live Google Search Grounding.

    Returns structured JSON with scam verdict, company reputation, and live web sources.
    """
    client = get_genai_client()
    if client is None:
        return {
            "available": False,
            "message": "Google Gemini Search is not configured. Add GEMINI_API_KEY to backend/.env to enable live AI web search.",
        }

    prompt = f"""
Analyze this job message for scams using real-time Google search investigation.
MESSAGE ({source_type}):
\"\"\"
{text}
\"\"\"

TASKS (Search Google):
1. Search company name + "scam" / "fake job" / "reviews" / "Glassdoor" / "Reddit".
2. Check if the entity is registered or an impersonated brand.
3. Check for scam red flags (advance fee, unrealistic salary, WhatsApp recruitment).

Return ONLY a valid JSON object matching this exact schema:
{{
    "is_scam": true or false,
    "scam_score": 0 to 100,
    "trust_level": "Safe" | "Likely Safe" | "Suspicious" | "High Risk" | "Very High Risk",
    "verdict_summary": "1-2 sentence summary of search findings.",
    "company_reputation": "Brief summary of company web presence and legitimacy.",
    "scam_indicators_found": ["Key findings or evidence from search"],
    "recommended_action": "Actionable advice for the candidate."
}}
"""

    try:
        from google.genai import types

        # Call Gemini with Google Search Grounding, budget=0 for ultra-fast latency,
        # and an 8-second timeout so it never causes scanning lag.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                temperature=0.1,
                http_options=types.HttpOptions(timeout=8000),
            ),
        )

        response_text = response.text or ""

        # Extract JSON from response
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            result = {
                "is_scam": "scam" in response_text.lower() or "fraud" in response_text.lower(),
                "scam_score": 75.0 if "scam" in response_text.lower() else 15.0,
                "trust_level": "High Risk" if "scam" in response_text.lower() else "Safe",
                "verdict_summary": response_text[:200],
                "company_reputation": "Analyzed via Google Search",
                "scam_indicators_found": [],
                "recommended_action": "Exercise caution.",
            }

        # Extract Grounding Web Sources from metadata if available
        web_sources = []
        try:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                grounding_meta = getattr(candidate, "grounding_metadata", None)
                if grounding_meta:
                    chunks = getattr(grounding_meta, "grounding_chunks", [])
                    for chunk in chunks:
                        web = getattr(chunk, "web", None)
                        if web:
                            web_sources.append({
                                "title": getattr(web, "title", "Web Source"),
                                "url": getattr(web, "uri", "#"),
                            })
        except Exception:
            pass

        return {
            "available": True,
            "is_scam": bool(result.get("is_scam", False)),
            "scam_score": float(result.get("scam_score", 50.0)),
            "trust_level": str(result.get("trust_level", "Suspicious")),
            "verdict_summary": str(result.get("verdict_summary", "")),
            "company_reputation": str(result.get("company_reputation", "")),
            "scam_indicators_found": list(result.get("scam_indicators_found", [])),
            "recommended_action": str(result.get("recommended_action", "")),
            "web_sources": web_sources[:5],
            "model_used": "Gemini 2.5 Flash with Google Search Grounding",
        }

    except Exception as e:
        err_str = str(e)
        if "API_KEY" in err_str.upper() or "INVALID" in err_str.upper() or "PERMISSION" in err_str.upper():
            logger.warning("Gemini API key is invalid or expired. Update GEMINI_API_KEY in backend/.env")
        else:
            logger.warning(f"Gemini Search Analysis failed: {e}")
        return {
            "available": False,
            "error": err_str,
            "message": "AI Web search analysis could not be completed.",
        }


def extract_text_from_image_gemini(image_bytes: bytes, mime_type: str = "image/png") -> Dict:
    """
    Extract text from a screenshot using Gemini Vision (multimodal).
    Falls back gracefully if Gemini is not configured.
    """
    client = get_genai_client()
    if client is None:
        return {
            "success": False,
            "extracted_text": "",
            "confidence": 0.0,
            "error": "Gemini Vision not configured.",
            "engine": "gemini_vision",
        }

    try:
        from google.genai import types

        prompt = """Extract ALL visible text from this image exactly as it appears.
- Preserve paragraph structure with newlines.
- Include all text: headers, body, signatures, addresses, emails, phone numbers, links.
- Do NOT summarize or interpret — output raw extracted text only.
- If no text is visible, output: [NO TEXT FOUND]"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                temperature=0.0,
                http_options=types.HttpOptions(timeout=10000),
            ),
        )

        extracted = (response.text or "").strip()

        if not extracted or extracted == "[NO TEXT FOUND]":
            return {
                "success": True,
                "extracted_text": "",
                "confidence": 0.0,
                "line_count": 0,
                "engine": "gemini_vision",
                "warning": "No text detected in image.",
            }

        lines = [ln for ln in extracted.splitlines() if ln.strip()]
        return {
            "success": True,
            "extracted_text": extracted,
            "confidence": 0.97,          # Gemini Vision is highly accurate
            "line_count": len(lines),
            "char_count": len(extracted),
            "engine": "gemini_vision",
        }

    except Exception as e:
        logger.warning(f"Gemini Vision OCR failed: {e}")
        return {
            "success": False,
            "extracted_text": "",
            "confidence": 0.0,
            "error": str(e),
            "engine": "gemini_vision",
        }
