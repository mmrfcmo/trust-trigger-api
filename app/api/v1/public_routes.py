"""Public API routes for Trust Snapshot lead capture (no auth required)."""
import uuid, smtplib, os, json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Lead, Organisation, User, UserRole
from app.models.trust_scan import TrustScan, ScanType, ScanStatus
from app.models.scoring import TrustScoreRecord
from app.services.trust_scanner import run_scan as trigger_scan
from app.services.scoring import compute_trust_score, build_score_response
from app.core.security import hash_password
from pydantic import BaseModel, Field, EmailStr
from email.mime.text import MIMEText
router = APIRouter(prefix="/api/v1/public", tags=["Public - Trust Snapshot"])

class TrustSnapshotRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    website: str = Field(..., min_length=1, max_length=512)
    email: EmailStr

class TrustSnapshotResponse(BaseModel):
    success: bool
    message: str
    report_url: str = ""
    lead_id: str = ""
    score: int = 0
    grade: str = ""
    issues_found: int = 0
    standards_passed: int = 0
    standards_total: int = 9
    pillars: list = []
    standards: list = []
    issues: list = []
    actions: list = []
    error: str = ""

async def _get_or_create_default_org(db):
    result = await db.execute(select(Organisation).where(Organisation.slug == "trust-snapshot-leads"))
    org = result.scalar_one_or_none()
    if not org:
        org = Organisation(name="Trust Snapshot Leads", slug="trust-snapshot-leads", settings={"is_public_lead_capture": True})
        db.add(org)
        await db.flush()
    return org

async def _get_or_create_system_user(db, org_id):
    result = await db.execute(select(User).where(User.email == "system@trusttriggeragency.com", User.organisation_id == org_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(email="system@trusttriggeragency.com", password_hash=hash_password(str(uuid.uuid4())), full_name="Trust Trigger System", role=UserRole.admin, organisation_id=org_id, is_active=True, is_verified=True)
        db.add(user)
        await db.flush()
    return user

@router.post("/trust-snapshot", response_model=TrustSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def submit_trust_snapshot(req: TrustSnapshotRequest, request: Request, db = Depends(get_db)):
    org = await _get_or_create_default_org(db)
    user = await _get_or_create_system_user(db, org.id)
    website = req.website.strip()
    if not website.startswith(("http://", "https://")):
        website = "https://" + website
    lead = Lead(organisation_id=org.id, business_name=req.full_name, website=website, email=req.email, source="trust_snapshot_landing")
    db.add(lead)
    await db.flush()
    scan = None
    try:
        scan = await trigger_scan(db, lead.id, org.id, user.id, ScanType.full)
    except Exception:
        scan = None
    score_response = None
    try:
        if scan and scan.status == ScanStatus.completed:
            score_record = await compute_trust_score(db, scan.id, org.id, lead.id, user.id)
            score_response = build_score_response(score_record)
    except Exception:
        score_response = None
    if score_response:
        pillars_data = []
        for p in score_response.pillars:
            pillars_data.append({"name": p.name, "label": p.label, "score": p.score, "max_score": p.max_score, "percentage": p.percentage})
        standards_data = []
        issues_data = []
        actions_data = []
        for imp in score_response.improvements:
            std_name = imp.standard.replace("_", " ").title()
            standards_data.append({"name": std_name, "passed": imp.passed})
            if not imp.passed:
                issues_data.append({"title": imp.action, "detail": imp.detail})
        for act in score_response.priority_actions:
            actions_data.append({"title": act.action, "detail": act.detail, "effort": act.effort})
        overall_pct = score_response.overall_percentage
        grade_label = score_response.grade.value if hasattr(score_response.grade, 'value') else str(score_response.grade)
        await db.commit()
        return TrustSnapshotResponse(success=True, message="Your Trust Snapshot is ready.", report_url="/api/v1/public/report-view/" + str(lead.id), lead_id=str(lead.id), score=int(overall_pct), grade=grade_label, issues_found=len(issues_data), standards_passed=score_response.overall_score, standards_total=score_response.overall_max, pillars=pillars_data, standards=standards_data, issues=issues_data, actions=actions_data)
    else:
        await db.commit()
        return TrustSnapshotResponse(success=True, message="Your Trust Snapshot is being generated.", report_url="", lead_id=str(lead.id), score=0, grade="", issues_found=0, standards_passed=0, standards_total=9, pillars=[], standards=[], issues=[], actions=[])

@router.get("/report-view/{lead_id}")
async def view_report(lead_id: str, db = Depends(get_db)):
    from app.models.recommendations import AIRecommendation
    result = await db.execute(select(AIRecommendation).where(AIRecommendation.lead_id == lead_id))
    report = result.scalar_one_or_none()
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if not lead:
        return HTMLResponse(content="<h1>Report not found</h1>", status_code=404)
    business_name = lead.business_name or "Your Business"
    website = lead.website or ""
    score = 0
    grade = "Unknown"
    if report:
        score = int(report.score) if report.score else 0
        grade = report.grade or "Unknown"
    html = "<html><body style='font-family:Inter,sans-serif;background:#f8fafc;padding:2rem'>"
    html += "<h1 style='color:#0f172a'>Trust Snapshot Report</h1>"
    html += "<p><strong>Business:</strong> " + business_name + "</p>"
    html += "<p><strong>Website:</strong> " + website + "</p>"
    html += "<p><strong>Trust Score:</strong> " + str(score) + "/100 (" + grade + ")</p>"
    if report and report.content:
        html += "<hr><div>" + report.content + "</div>"
    html += "</body></html>"
    return HTMLResponse(content=html)
