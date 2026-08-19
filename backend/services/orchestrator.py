"""
JobShield AI — Scam Analysis Pipeline Orchestrator Service

Decoupled orchestration layer that coordinates multi-tier scam analysis:
1. Local ML & Heuristics (NLP Analyzer, Rule Engine, Email Checker, Salary Checker, Threat DB, Web Intelligence)
2. External AI & Threat Intelligence (Google Gemini Web Search Analyzer)
3. Ensemble Score Synthesis & Threat Classification
4. Thread-safe Bounded In-Memory Cache with TTL Expiration
"""

import asyncio
import hashlib
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Tuple

from services.nlp_analyzer import get_analyzer
from services.rule_engine import analyze_text as rule_analyze, get_trust_level
from services.email_checker import analyze_emails_in_text
from services.salary_checker import check_salary
from services.web_verifier import analyze_web_intelligence
from services.gemini_search_analyzer import analyze_with_gemini_search
from database.db import check_text_for_known_scams

logger = logging.getLogger("jobshield.orchestrator")

# Dedicated thread-pool for CPU-bound / blocking operations
_executor = ThreadPoolExecutor(max_workers=4)

# ─── Thread-Safe Bounded TTL Cache ───────────────────────────────────────────────

class TimedLRUCache:
    """Thread-safe bounded in-memory cache with TTL expiration."""

    def __init__(self, max_size: int = 300, default_ttl_seconds: int = 3600):
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds
        self._cache: Dict[str, Tuple[float, dict]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[dict]:
        with self._lock:
            if key not in self._cache:
                return None
            expiry, value = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        ttl_seconds = ttl if ttl is not None else self._default_ttl
        expiry = time.time() + ttl_seconds
        with self._lock:
            # Purge expired items if at capacity
            if len(self._cache) >= self._max_size:
                now = time.time()
                expired_keys = [k for k, (exp, _) in self._cache.items() if now > exp]
                for k in expired_keys:
                    del self._cache[k]

            # If still at capacity, pop oldest entry (FIFO)
            if len(self._cache) >= self._max_size:
                self._cache.pop(next(iter(self._cache)))

            self._cache[key] = (expiry, value)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


_analysis_cache = TimedLRUCache(max_size=300, default_ttl_seconds=3600)


# ─── Core Pipeline Orchestration ────────────────────────────────────────────────

async def run_analysis_pipeline(text: str, source_type: str = "job_posting") -> dict:
    """
    Execute the multi-tier scam analysis pipeline with concurrent execution and caching.

    Args:
        text: Normalized job posting, message, or email body.
        source_type: 'job_posting', 'whatsapp', 'email', 'linkedin', etc.

    Returns:
        Structured dictionary matching AnalysisResponse schema.
    """
    text_hash = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]
    cache_key = f"{source_type}:{text_hash}"

    cached_result = _analysis_cache.get(cache_key)
    if cached_result is not None:
        logger.debug(f"Analysis cache hit for key: {cache_key}")
        return cached_result

    loop = asyncio.get_running_loop()

    # ── Group 1: Local CPU/IO Work (ML inference, regex rules, DB lookups) ──────
    def _local_bundle():
        analyzer       = get_analyzer()
        ml_result      = analyzer.predict(text)
        rule_result    = rule_analyze(text)
        email_result   = analyze_emails_in_text(text)
        salary_result  = check_salary(text)
        known_warnings = check_text_for_known_scams(text)
        web_intel      = analyze_web_intelligence(text, source_type)
        return ml_result, rule_result, email_result, salary_result, known_warnings, web_intel

    # ── Group 2: External Gemini AI Search (Network I/O) ────────────────────────
    def _gemini_bundle():
        try:
            return analyze_with_gemini_search(text, source_type)
        except Exception as e:
            logger.warning(f"Gemini Search Analysis exception: {e}")
            return {
                "available": False,
                "error": str(e),
                "message": "AI web search could not be completed.",
            }

    # Run local and external analysis concurrently
    (
        (ml_result, rule_result, email_result, salary_result, known_warnings, web_intel),
        gemini_result,
    ) = await asyncio.gather(
        loop.run_in_executor(_executor, _local_bundle),
        loop.run_in_executor(_executor, _gemini_bundle),
    )

    # ── Score Synthesis & Ensemble Blending ─────────────────────────────────────
    ml_score   = ml_result.get("ml_score", 50.0)
    rule_score = rule_result.get("rule_score", 0.0)

    if gemini_result.get("available") and "scam_score" in gemini_result:
        gemini_score   = gemini_result["scam_score"]
        combined_score = (gemini_score * 0.40) + (ml_score * 0.35) + (rule_score * 0.25)
    else:
        weighted = (ml_score * 0.55) + (rule_score * 0.45)
        # Protect against ML diluting explicit keyword/rule detections
        if rule_score >= 35:
            floor = rule_score * 0.85
        else:
            floor = max(ml_score, rule_score) * 0.70
        combined_score = max(weighted, floor)

    # Boost when independent signals converge
    if ml_score >= 70 and rule_score >= 30:
        combined_score = min(100.0, combined_score + 8)
    if ml_score >= 85 and rule_score >= 50:
        combined_score = min(100.0, combined_score + 5)

    # Boost for web intelligence signals (brand impersonation, high-risk TLDs)
    if web_intel.get("risk_boost"):
        combined_score += web_intel["risk_boost"]

    # Boost if known scam identifiers found in threat registry
    if known_warnings:
        combined_score += 20

    # Boost for email/salary red flags
    if email_result.get("overall_risk") == "high":
        combined_score += 10
    if salary_result.get("risk_level") == "high":
        combined_score += 8

    # Append web intelligence risk signals to itemized risk factors
    combined_risk_factors = list(rule_result.get("risk_factors", []))
    for sig in web_intel.get("risk_signals", []):
        combined_risk_factors.append({
            "category":    sig.get("type", "web_intel"),
            "severity":    sig.get("severity", "medium"),
            "description": sig.get("title", "Threat Signal"),
            "matches":     [sig.get("detail", "")],
        })

    combined_score = min(100.0, max(0.0, combined_score))
    trust_level    = get_trust_level(combined_score)

    result = {
        "scam_probability":    round(combined_score, 1),
        "trust_level":         trust_level,
        "ml_score":            ml_score,
        "rule_score":          round(rule_score, 1),
        "risk_factors":        combined_risk_factors,
        "scam_keywords":       rule_result.get("scam_keywords", []),
        "email_analysis":      email_result,
        "salary_analysis":     salary_result,
        "known_scam_warnings": known_warnings,
        "ml_top_features":     ml_result.get("top_features", []),
        "web_intelligence":    web_intel,
        "gemini_analysis":     gemini_result,
        "original_text":       text,
        "source_type":         source_type,
    }

    _analysis_cache.set(cache_key, result)
    return result
