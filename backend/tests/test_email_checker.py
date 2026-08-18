"""
Unit tests for the email checker service.
"""

import pytest
from services.email_checker import extract_emails, check_email, analyze_emails_in_text


def test_extract_emails():
    text = "Send your resume to careers@google.com or hr.recruitment@gmail.com for details."
    emails = extract_emails(text)
    assert len(emails) == 2
    assert "careers@google.com" in emails
    assert "hr.recruitment@gmail.com" in emails


def test_corporate_email_legitimate():
    res = check_email("careers@google.com")
    assert res["is_free_provider"] is False
    assert res["risk_level"] == "low"


def test_free_email_basic():
    res = check_email("john.doe@gmail.com")
    assert res["is_free_provider"] is True
    assert res["risk_level"] == "medium"


def test_free_email_impersonation():
    # HR / Company name on free email
    res_google = check_email("google.recruitment@gmail.com")
    assert res_google["risk_level"] == "high"

    res_hr = check_email("hr_hiring_team@yahoo.com")
    assert res_hr["risk_level"] == "high"

    res_jpmorgan = check_email("jpmorgan.jobs@outlook.com")
    assert res_jpmorgan["risk_level"] == "high"


def test_analyze_emails_in_text_empty():
    res = analyze_emails_in_text("No emails here, just contact us on telegram.")
    assert res["emails_found"] == 0
    assert res["overall_risk"] == "unknown"


def test_analyze_emails_in_text_max_risk():
    text = "Contact john@gmail.com or official-recruitment-google@gmail.com"
    res = analyze_emails_in_text(text)
    assert res["emails_found"] == 2
    assert res["overall_risk"] == "high"
