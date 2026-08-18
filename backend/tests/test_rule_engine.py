"""
Unit tests for the rule-based scam detection engine.
"""

import pytest
from services.rule_engine import analyze_text, get_trust_level, _is_negated


def test_fee_request_detection():
    text = "Congratulations! You are selected. Please pay ₹999 registration fee to confirm your seat."
    res = analyze_text(text)
    assert res["rule_score"] > 30
    categories = [rf["category"] for rf in res["risk_factors"]]
    assert "fee_request" in categories


def test_negation_handling():
    # "no registration fee" should NOT trigger a fee_request risk factor
    text = "Join our campus recruitment drive. There is no registration fee and no hidden charges."
    res = analyze_text(text)
    fee_factors = [rf for rf in res["risk_factors"] if rf["category"] == "fee_request"]
    assert len(fee_factors) == 0
    assert res["rule_score"] < 25


def test_is_negated_helper():
    text = "we have no registration fee for candidates"
    match_start = text.find("registration fee")
    assert _is_negated(text, match_start) is True

    text_pos = "please pay the registration fee today"
    match_start_pos = text_pos.find("registration fee")
    assert _is_negated(text_pos, match_start_pos) is False


def test_urgency_and_guarantee_detection():
    text = "URGENT: Limited seats available, offer expires in 2 hours! 100% placement guarantee with no interview required."
    res = analyze_text(text)
    categories = [rf["category"] for rf in res["risk_factors"]]
    assert "urgency_language" in categories
    assert "guaranteed_outcomes" in categories
    assert res["rule_score"] >= 30


def test_legit_indicators_reduce_score():
    text = (
        "We are hiring a Senior Software Engineer. Requirements: 5+ years of experience in Python and AWS. "
        "Our hiring process involves a technical interview, coding test, and HR discussion. "
        "Equal opportunity employer. Apply online on our careers page. We do not charge any fees."
    )
    res = analyze_text(text)
    assert res["legit_indicator_count"] >= 3
    assert res["rule_score"] == 0.0


def test_trust_levels():
    assert get_trust_level(10) == "Safe"
    assert get_trust_level(35) == "Likely Safe"
    assert get_trust_level(55) == "Suspicious"
    assert get_trust_level(70) == "High Risk"
    assert get_trust_level(85) == "Very High Risk"
