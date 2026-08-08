"""
JobShield AI — Report API Routes

Endpoints for submitting and querying scam reports.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from database.db import add_report, check_identifier, get_recent_reports, get_stats

router = APIRouter(prefix="/api/report", tags=["Reports"])


# ─── Request Models ──────────────────────────────────────────────────────────────

class ScamReport(BaseModel):
    report_type: str  # email, phone, website, upi, company
    identifier: str
    company_name: Optional[str] = None
    description: Optional[str] = None
    source_platform: Optional[str] = None


class CheckRequest(BaseModel):
    identifier: str


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/submit")
async def submit_report(report: ScamReport):
    """Submit a new scam report."""
    valid_types = {"email", "phone", "website", "upi", "company"}
    if report.report_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report_type. Must be one of: {', '.join(valid_types)}"
        )

    if not report.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier cannot be empty")

    result = add_report(
        report_type=report.report_type,
        identifier=report.identifier,
        company_name=report.company_name,
        description=report.description,
        source_platform=report.source_platform,
    )
    return result


@router.post("/check")
async def check_report(request: CheckRequest):
    """Check if an identifier has been reported as a scam."""
    if not request.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier cannot be empty")

    return check_identifier(request.identifier)


@router.get("/recent")
async def recent_reports(limit: int = 20):
    """Get recent scam reports (for community feed)."""
    if limit > 100:
        limit = 100
    return get_recent_reports(limit)


@router.get("/stats")
async def report_stats():
    """Get scam report statistics."""
    return get_stats()
