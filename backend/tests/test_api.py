"""
Integration tests for FastAPI endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "JobShield AI"
    assert data["status"] == "running"


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ml_model_loaded" in data


def test_analyze_text_scam():
    payload = {
        "text": "Congratulations! You have been selected for Google internship. Pay ₹999 registration fee to confirm your seat immediately via WhatsApp: 9876543210.",
        "source_type": "whatsapp",
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scam_probability"] > 40.0
    assert data["trust_level"] in ("Suspicious", "High Risk", "Very High Risk")
    assert len(data["risk_factors"]) > 0


def test_analyze_text_legitimate():
    payload = {
        "text": "Infosys is hiring a Software Engineer in Bangalore. Requirements: 3+ years experience with Java, Spring Boot, and SQL. Competitive salary and comprehensive benefits. Apply online at careers.infosys.com. No fee required at any stage.",
        "source_type": "job_posting",
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scam_probability"] < 40.0
    assert data["trust_level"] in ("Safe", "Likely Safe")


def test_analyze_text_validation_errors():
    # Empty text
    res_empty = client.post("/api/analyze/text", json={"text": "   "})
    assert res_empty.status_code == 400

    # Too short text
    res_short = client.post("/api/analyze/text", json={"text": "short"})
    assert res_short.status_code == 400

    # Oversized text
    res_long = client.post("/api/analyze/text", json={"text": "a" * 60_000})
    assert res_long.status_code == 400


def test_report_submit_and_check():
    # Submit valid report
    payload = {
        "report_type": "upi",
        "identifier": "scam_recruitment@paytm",
        "company_name": "ScamCo",
        "description": "Asked for registration charge",
    }
    res_submit = client.post("/api/report/submit", json=payload)
    assert res_submit.status_code == 200
    assert res_submit.json()["status"] in ("created", "updated")

    # Invalid report_type (should fail Pydantic validation with 422)
    invalid_payload = {
        "report_type": "invalid_type",
        "identifier": "test@domain.com",
    }
    res_invalid = client.post("/api/report/submit", json=invalid_payload)
    assert res_invalid.status_code == 422

    # Check report
    res_check = client.post("/api/report/check", json={"identifier": "scam_recruitment@paytm"})
    assert res_check.status_code == 200
    assert res_check.json()["found"] is True


def test_report_recent_and_stats():
    res_recent = client.get("/api/report/recent")
    assert res_recent.status_code == 200
    assert isinstance(res_recent.json(), list)

    res_stats = client.get("/api/report/stats")
    assert res_stats.status_code == 200
    assert "total_reports" in res_stats.json()
