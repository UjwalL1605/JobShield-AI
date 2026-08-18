"""
JobShield AI — SQLite Database for Scam Reports

Stores reported scam identifiers (emails, phones, websites, UPI IDs, company names).
Provides lookup functionality to warn future users.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


logger = logging.getLogger("jobshield.db")

DB_PATH = os.path.join(os.path.dirname(__file__), "scam_reports.db")


def get_connection():
    """Get SQLite connection with row factory (thread-safe)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS scam_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                company_name TEXT,
                description TEXT,
                source_platform TEXT,
                reported_at TEXT NOT NULL,
                report_count INTEGER DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_identifier ON scam_reports(identifier);
            CREATE INDEX IF NOT EXISTS idx_report_type ON scam_reports(report_type);
            CREATE INDEX IF NOT EXISTS idx_company ON scam_reports(company_name);
        """)

        conn.commit()
    finally:
        conn.close()
    logger.info("✅ Database initialized")


def add_report(
    report_type: str,
    identifier: str,
    company_name: Optional[str] = None,
    description: Optional[str] = None,
    source_platform: Optional[str] = None,
) -> Dict:
    """
    Add a scam report to the database.

    Args:
        report_type: One of 'email', 'phone', 'website', 'upi', 'company'
        identifier: The reported identifier (email address, phone number, etc.)
        company_name: Name of the company (if applicable)
        description: User's description of the scam
        source_platform: Where the scam was encountered

    Returns:
        Dict with report ID and status.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        identifier_clean = identifier.strip().lower()

        # Check if already reported
        cursor.execute(
            "SELECT id, report_count FROM scam_reports WHERE identifier = ? AND report_type = ?",
            (identifier_clean, report_type)
        )
        existing = cursor.fetchone()

        if existing:
            # Increment report count
            cursor.execute(
                "UPDATE scam_reports SET report_count = report_count + 1 WHERE id = ?",
                (existing["id"],)
            )
            conn.commit()
            return {
                "status": "updated",
                "id": existing["id"],
                "report_count": existing["report_count"] + 1,
                "message": f"This {report_type} has been reported {existing['report_count'] + 1} times.",
            }

        # Insert new report
        cursor.execute(
            """INSERT INTO scam_reports (report_type, identifier, company_name, description, source_platform, reported_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (report_type, identifier_clean, company_name, description, source_platform,
             datetime.now(timezone.utc).isoformat())
        )

        report_id = cursor.lastrowid
        conn.commit()

        return {
            "status": "created",
            "id": report_id,
            "report_count": 1,
            "message": f"Thank you! Your {report_type} report has been recorded.",
        }
    finally:
        conn.close()


def check_identifier(identifier: str) -> Dict:
    """
    Check if an identifier exists in the scam database.

    Returns:
        Dict with found status, report count, and details.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        identifier_clean = identifier.strip().lower()

        cursor.execute(
            """SELECT report_type, identifier, company_name, report_count, reported_at
               FROM scam_reports WHERE identifier = ?""",
            (identifier_clean,)
        )
        results = cursor.fetchall()
    finally:
        conn.close()

    if not results:
        return {
            "found": False,
            "identifier": identifier,
            "reports": [],
            "message": "No reports found for this identifier.",
        }

    reports = [dict(row) for row in results]
    total_reports = sum(r["report_count"] for r in reports)

    return {
        "found": True,
        "identifier": identifier,
        "total_reports": total_reports,
        "reports": reports,
        "message": f"⚠️ WARNING: This identifier has been reported {total_reports} time(s) as a scam!",
    }


def check_text_for_known_scams(text: str) -> List[Dict]:
    """
    Scan text for any known scam identifiers.

    Checks emails, phone numbers, URLs, and UPI IDs found in the text.
    """
    import re

    warnings = []

    # Extract identifiers from text
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phones = re.findall(r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}', text)
    upis = re.findall(r'[a-zA-Z0-9._]+@(?:paytm|gpay|phonepe|upi|okaxis|okhdfcbank|ybl)', text)
    urls = re.findall(r'https?://[^\s<>"\')\]]+', text)

    all_identifiers = (
        [(e, "email") for e in emails] +
        [(p.replace(" ", "").replace("-", ""), "phone") for p in phones] +
        [(u, "upi") for u in upis] +
        [(u, "website") for u in urls]
    )

    for identifier, id_type in all_identifiers:
        result = check_identifier(identifier)
        if result["found"]:
            warnings.append({
                "type": id_type,
                "identifier": identifier,
                "total_reports": result["total_reports"],
                "message": result["message"],
            })

    return warnings


def get_recent_reports(limit: int = 20) -> List[Dict]:
    """Get most recent scam reports."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """SELECT report_type, identifier, company_name, report_count, reported_at
               FROM scam_reports ORDER BY reported_at DESC LIMIT ?""",
            (limit,)
        )
        results = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
    return results


def get_stats() -> Dict:
    """Get database statistics."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM scam_reports")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT report_type, COUNT(*) as count FROM scam_reports GROUP BY report_type"
        )
        by_type = {row["report_type"]: row["count"] for row in cursor.fetchall()}
    finally:
        conn.close()

    return {
        "total_reports": total,
        "by_type": by_type,
    }
