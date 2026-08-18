"""
Unit tests for the web intelligence and entity verifier service.
"""

import pytest
from services.web_verifier import extract_entities, analyze_web_intelligence


def test_extract_entities():
    text = (
        "Google HR is hiring! Contact hr-google@gmail.com or +919876543210. "
        "Apply at https://careers-google.xyz or wa.me/919876543210. Send fee to hr@paytm."
    )
    entities = extract_entities(text)
    assert "Google" in entities["companies"]
    assert "hr-google@gmail.com" in entities["emails"]
    assert len(entities["domains"]) > 0
    assert len(entities["phones"]) > 0
    assert len(entities["upi_ids"]) > 0


def test_brand_impersonation_detection():
    text = "TCS is hiring freshers for immediate joining! Send your resume to tcs.careers@gmail.com"
    res = analyze_web_intelligence(text)
    assert res["impersonation_detected"] is True
    assert res["risk_boost"] > 0
    types = [sig["type"] for sig in res["risk_signals"]]
    assert "brand_impersonation" in types


def test_high_risk_domain_detection():
    text = "Check your application status on http://infosys-careers.xyz or http://tcs-jobs.top"
    res = analyze_web_intelligence(text)
    types = [sig["type"] for sig in res["risk_signals"]]
    assert "high_risk_domain" in types


def test_masked_url_shortener():
    text = "Click to apply: https://bit.ly/fakejoboffer"
    res = analyze_web_intelligence(text)
    types = [sig["type"] for sig in res["risk_signals"]]
    assert "masked_url_shortener" in types


def test_google_search_queries_generated():
    text = "Amazon recruitment drive via WhatsApp contact 9876543210"
    res = analyze_web_intelligence(text)
    assert len(res["google_search_queries"]) > 0
    query_types = [q["type"] for q in res["google_search_queries"]]
    assert "company_check" in query_types or "phone_check" in query_types or "official_portal" in query_types
