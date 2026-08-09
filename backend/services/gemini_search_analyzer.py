"""
JobShield AI — Google Gemini AI Deep Search Analyzer

Uses Google Gemini with Google Search Grounding to perform real-time
web intelligence lookups, verify company legitimacy, and cross-reference
known scam reports on Reddit, Glassdoor, Quora, and official registries.
"""

import os
import re
import json
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_client = None


def get_genai_client():
    """Get or initialize Google GenAI client if API key is present."""
    global _client
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None

    if _client is None:
        try:
            from google import genai
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"[WARN] Failed to initialize Google GenAI Client: {e}")
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
You are an elite cyber threat intelligence analyst and employment fraud investigator for JobShield AI.
Your mission is to perform a real-time Google Search investigation on this job offer / recruiter communication to determine if it is a SCAM or LEGITIMATE.

INPUT MESSAGE ({source_type}):
\"\"\"
{text}
\"\"\"

INVESTIGATION TASKS (Use Google Search):
1. Extract any Company Names, Recruiter Emails, Phone Numbers, Domains, or Telegram/UPI handles.
2. Search Google for the company name + "scam" / "fake job" / "reviews" / "Glassdoor" / "Reddit".
3. Check if the company is legitimate, registered, or an impersonated brand.
4. Check if the contact method (free Gmail, WhatsApp, Telegram) is inconsistent with genuine recruitment.
5. Provide a definitive scam probability (0-100), verdict, itemized evidence, and action recommendations.

CRITICAL REQUIREMENT: Return ONLY a valid JSON object matching this exact structure:
{{
    "is_scam": true or false,
    "scam_score": 0 to 100,
    "trust_level": "Safe" | "Likely Safe" | "Suspicious" | "High Risk" | "Very High Risk",
    "verdict_summary": "Concise 1-2 sentence executive summary of findings.",
    "company_reputation": "Summary of company legitimacy and web footprint found via Google.",
    "scam_indicators_found": ["List of specific red flags or legitimacy proofs identified"],
    "recommended_action": "Clear actionable safety advice for the candidate."
}}
"""

    try:
        from google.genai import types

        # Call Gemini with Google Search Grounding
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
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
        print(f"[WARN] Gemini Search Analysis failed: {e}")
        return {
            "available": False,
            "error": str(e),
            "message": "AI Web search analysis could not be completed.",
        }
