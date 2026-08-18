"""
JobShield AI — Threat Database Seeder

Populates the SQLite scam_reports database with verified scam identifiers
(fake consultancies, fraudulent domains, scam recruiter contacts) from the
Indian Job Scam Dataset and common Indian cyber scam reports.
"""

import os
import sys
import re
import sqlite3
import pandas as pd
from datetime import datetime, timezone

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database.db import get_connection, init_db


def seed_database():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    data_path = os.path.join(BACKEND_DIR, "ml", "data", "Indian Job Scam Dataset.csv")
    if not os.path.exists(data_path):
        print(f"⚠️ Dataset not found at: {data_path}")
        return

    print("🌱 Seeding Threat Intelligence Database from Indian Job Scam Dataset...")
    df = pd.read_csv(data_path)

    scam_rows = df[df["source"].isin(["recruitment", "whatsapp"]) | (df["fraudulent"] == 1.0)]

    inserted_count = 0
    phone_pattern = r'(\+?91[-\s]?[6-9]\d{9}|\b[6-9]\d{9}\b)'
    url_pattern = r'(https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})|([a-zA-Z0-9-]+\.(?:site|online|xyz|top|info|work|live|club|uno|cc)))'
    company_pattern = r'(?:from\s+HR\s+at|recruitment\s+team\s+at|shortlisted\s+for)\s+([A-Z][a-zA-Z0-9&.,\s-]{2,30})'

    seen_identifiers = set()

    for _, row in scam_rows.iterrows():
        msg = str(row.get("message", ""))
        stype = str(row.get("scam_type", "Job Scam"))
        platform = str(row.get("source", "whatsapp"))

        # 1. Extract and seed phone numbers
        for match in re.finditer(phone_pattern, msg):
            p = match.group(0).strip().replace(" ", "").replace("-", "")
            if p not in seen_identifiers:
                seen_identifiers.add(p)
                cursor.execute("""
                    INSERT OR IGNORE INTO scam_reports (report_type, identifier, company_name, description, source_platform, reported_at, report_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("phone", p.lower(), None, f"Reported in {stype} recruitment fraud", platform, datetime.now(timezone.utc).isoformat(), 3))
                inserted_count += 1

        # 2. Extract and seed domains / URLs
        for match in re.finditer(url_pattern, msg):
            u = match.group(0).strip()
            if u not in seen_identifiers and not u.endswith(".com/"):
                seen_identifiers.add(u)
                cursor.execute("""
                    INSERT OR IGNORE INTO scam_reports (report_type, identifier, company_name, description, source_platform, reported_at, report_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("website", u.lower(), None, f"Phishing / Scam link reported in {stype}", platform, datetime.now(timezone.utc).isoformat(), 4))
                inserted_count += 1

        # 3. Extract fake HR company entities
        for match in re.finditer(company_pattern, msg):
            c = match.group(1).strip(" ,.-")
            if c and len(c) > 3 and c not in seen_identifiers and c.lower() not in ["amazon", "google", "microsoft", "ibm", "tcs"]:
                seen_identifiers.add(c)
                cursor.execute("""
                    INSERT OR IGNORE INTO scam_reports (report_type, identifier, company_name, description, source_platform, reported_at, report_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("company", c.lower(), c, f"Suspicious entity associated with {stype}", platform, datetime.now(timezone.utc).isoformat(), 2))
                inserted_count += 1

    conn.commit()
    cursor.execute("SELECT COUNT(*) as total FROM scam_reports")
    total = cursor.fetchone()["total"]
    conn.close()

    print(f"✅ Seeding Complete! Added {inserted_count} new threats. Total records in registry: {total}")


if __name__ == "__main__":
    seed_database()
