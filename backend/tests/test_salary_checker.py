"""
Unit tests for the salary checker service.
"""

import pytest
from services.salary_checker import extract_salary_amounts, check_salary, _determine_context


def test_extract_salary_amounts():
    text = "Offering ₹50,000/month or 12 LPA CTC for experienced candidates."
    amounts = extract_salary_amounts(text)
    assert len(amounts) >= 2
    currencies = [a["currency"] for a in amounts]
    assert "INR" in currencies
    assert "LPA" in currencies


def test_context_determination():
    assert "no_experience" in _determine_context("fresher with no experience needed, 12th pass can apply")
    assert "data_entry" in _determine_context("simple data entry typing work from home")
    assert "experienced" in _determine_context("senior engineer role")


def test_unrealistic_salary_flagged():
    text = "Work from home data entry typing job. No experience needed. Earn ₹1,50,000 per month!"
    res = check_salary(text)
    assert res["salary_found"] is True
    assert res["risk_level"] == "high"
    assert len(res["reasons"]) > 0


def test_realistic_salary_pass():
    text = "Junior developer internship, stipend ₹15,000/month in Bangalore."
    res = check_salary(text)
    assert res["salary_found"] is True
    assert res["risk_level"] in ("low", "unknown")


def test_no_salary_mentioned():
    text = "We are looking for a Python developer with Django experience."
    res = check_salary(text)
    assert res["salary_found"] is False
    assert res["risk_level"] == "unknown"
