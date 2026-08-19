"""
JobShield AI — Report API Routes

Endpoints for submitting and querying scam reports.
All database I/O is dispatched via asyncio.to_thread for non-blocking concurrency.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Literal

from limiter import limiter
from database.db import add_report, check_identifier, get_recent_reports, get_stats

router = APIRouter(prefix="/api/report", tags=["Reports"])


# ─── Request Models ──────────────────────────────────────────────────────────────

class ScamReport(BaseModel):
    report_type: Literal["email", "phone", "website", "upi", "company"]
    identifier: str = Field(..., min_length=1)
    company_name: Optional[str] = None
    description: Optional[str] = None
    source_platform: Optional[str] = None


class CheckRequest(BaseModel):
    identifier: str = Field(..., min_length=1)


# ─── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/submit")
@limiter.limit("20/minute")
async def submit_report(request: Request, body: ScamReport):
    """Submit a new scam report."""
    if not body.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier cannot be empty")

    result = await asyncio.to_thread(
        add_report,
        report_type=body.report_type,
        identifier=body.identifier,
        company_name=body.company_name,
        description=body.description,
        source_platform=body.source_platform,
    )
    return result


@router.post("/check")
@limiter.limit("60/minute")
async def check_report(request: Request, body: CheckRequest):
    """Check if an identifier has been reported as a scam."""
    if not body.identifier.strip():
        raise HTTPException(status_code=400, detail="Identifier cannot be empty")

    return await asyncio.to_thread(check_identifier, body.identifier)


@router.get("/recent")
async def recent_reports(request: Request, limit: int = 20):
    """Get recent scam reports (for community feed)."""
    if limit > 100:
        limit = 100
    return await asyncio.to_thread(get_recent_reports, limit)


@router.get("/stats")
async def report_stats(request: Request):
    """Get scam report statistics."""
    return await asyncio.to_thread(get_stats)
