"""
Unit tests for the SQLite database layer.
"""

import pytest
from database.db import (
    init_db,
    add_report,
    check_identifier,
    check_text_for_known_scams,
    get_recent_reports,
    get_stats,
)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_add_and_check_report():
    test_id = "test_scam_recruiter_9999@fakejob.com"
    # 1. Add new report
    res_add = add_report(
        report_type="email",
        identifier=test_id,
        company_name="Fake Corp",
        description="Asked for 2000 registration fee",
        source_platform="email",
    )
    assert res_add["status"] in ("created", "updated")
    assert res_add["report_count"] >= 1

    # 2. Check identifier
    res_check = check_identifier(test_id)
    assert res_check["found"] is True
    assert res_check["total_reports"] >= 1

    # 3. Add duplicate report — should increment count
    res_add2 = add_report(
        report_type="email",
        identifier=test_id,
    )
    assert res_add2["status"] == "updated"
    assert res_add2["report_count"] >= 2


def test_check_nonexistent_identifier():
    res = check_identifier("absolutely_legit_never_reported_email_12345@domain.com")
    assert res["found"] is False
    assert res["reports"] == []


def test_check_text_for_known_scams():
    test_id = "scammer_threat_test@gmail.com"
    add_report(report_type="email", identifier=test_id)

    text = f"Please contact our recruiter at {test_id} for your offer letter."
    warnings = check_text_for_known_scams(text)
    assert len(warnings) >= 1
    assert any(w["identifier"] == test_id for w in warnings)


def test_get_stats_and_recent():
    stats = get_stats()
    assert "total_reports" in stats
    assert "by_type" in stats
    assert isinstance(stats["total_reports"], int)

    recent = get_recent_reports(limit=5)
    assert isinstance(recent, list)
    assert len(recent) <= 5
