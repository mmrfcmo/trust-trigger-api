"""Public API routes for Trust Snapshot lead capture (no auth required)."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Lead, Organisation, User, UserRole
from app.models.trust_scan import TrustScan, ScanType, ScanStatus
from app.models.scoring import TrustScoreRecord
from app.services.lead_intelligence import calculate_opportunity_score
from app.services.trust_scanner import run_scan as trigger_scan
from app.services.scoring import compute_trust_score, build_score_response
from app.core.security import hash_password
from pydantic import BaseModel, Field, EmailStr
import smtplib
import os
from email.mime.multipart import MIMEMultipart
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

async def _get_or_create_default_org(db: AsyncSession) -> Organisation:
    result = await db.execute(select(Organisation).where(Organisation.slug == "trust-snapshot-leads"))
    org = result.scalar_one_or_none()
    if not org:
        org = Organisation(name="Trust Snapshot Leads", slug="trust-snapshot-leads", settings={"is_public_lead_capture": True})
        db.add(org)
        await db.flush()
    return org

async def _get_or_create_system_user(db: AsyncSession, org_id: uuid.UUID) -> User:
    result = await db.execute(select(User).where(User.email == "system@trusttriggeragency.com", User.organisation_id == org_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(email="system@trusttriggeragency.com", password_hash=hash_password(str(uuid.uuid4())), full_name="Trust Trigger System", role=UserRole.admin, organisation_id=org_id, is_active=True, is_verified=True)
        db.add(user)
        await db.flush()
    return user

def _build_report_html(business_name, lead_email, website, score, grade, issues, actions, pillars, lead_id):
    pillars_html = ""
    for p in pillars:
        color = "red" if p.get("percentage", 0) < 40 else "amber" if p.get("percentage", 0) < 70 else "green"
        pillars_html += f"""{p.get('label', '')}{p.get('score', 0)}/{p.get('max_score', 0)}{p.get('percentage', 0)}%"""
    issues_html = ""
    for iss in issues[:5]:
        issues_html += f"""
⚠️
{iss.get('title', '')}
{iss.get('detail', '')}
"""
    actions_html = ""
    effort_colors = {"low": "background:#dcfce7;color:#166534", "medium": "background:#fef3c7;color:#92400e", "high": "background:#fee2e2;color:#991b1b"}
    for i, act in enumerate(actions[:5]):
        ec = effort_colors.get(act.get('effort', 'medium'), "background:#f1f5f9;color:#475569")
        actions_html += f"""
#{i+1}
{act.get('title', '')}
{act.get('effort', 'medium').title()}
"""
    return f"""
🛡️
Trust Snapshot Report
Prepared for {business_name}

Business	{business_name}
Website	{website}
Email	{lead_email}
Trust Score	{score}/100 ({grade})
Score Breakdown
{pillars_html}
Pillar	Score	%
Top Issues
{issues_html}
Priority Actions
{actions_html}
Trust Trigger Agency™ — London, UK

"""

def _send_owner_notification(business_name, lead_email, website, score, grade, issues, actions, pillars, lead_id):
    owner_email = os.environ.get("OWNER_EMAIL", "mmr1979@hotmail.co.uk")
    gmail_user = os.environ.get("GMAIL_EMAIL", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_password:
        return
    report_html = _build_report_html(business_name, lead_email, website, score, grade, issues, actions, pillars, lead_id)
    body_html = f"""
🛡️
New Trust Snapshot Lead
A prospect has requested their Trust Snapshot

Business	{business_name}
Website	{website}
Email	{lead_email}
Trust Score	{score}/100 ({grade})
Available Options
Trust Snapshot (Free)
What they just received. Score: {score}/100 ({grade}).

Trust Transformation (£995)
20-min call + full report walkthrough + fix implementation.

Trust Monitor (£99/mo)
Ongoing monitoring and quarterly re-scans.

Lead ID: {lead_id}

A full report is attached to this email.

"""
    msg = MIMEMultipart('mixed')
    msg["Subject"] = f"New Trust Snapshot: {business_name} - Score: {score}/100 ({grade})"
    msg["From"] = gmail_user
    msg["To"] = owner_email
    msg.attach(MIMEText(body_html, "html"))
    report_attachment = MIMEText(report_html, "html")
    report_attachment.add_header('Content-Disposition', 'attachment', filename=f'Trust-Snapshot-{business_name.replace(" ", "-")}.html')
    msg.attach(report_attachment)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
    except Exception:
        pass

def _send_prospect_email(prospect_email, business_name, score, grade):
    gmail_user = os.environ.get("GMAIL_EMAIL", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_password:
        return
    html = f"""
🛡️
Thanks, {business_name}!
Your Trust Snapshot is ready

{score}
/100
{grade}
Your digital trust score is {score}/100
The best way to understand what this score means and how to improve it is a quick 20-minute no-obligation screen-share with a Trust Analyst. We will walk through your results together, explain exactly what is affecting your score, and show you what you can fix right away.

On your call, you will get:

✅
Your full score breakdown explained in plain English
✅
Specific issues found on your website and how to fix them
✅
Quick wins you can implement immediately
✅
No obligation honest advice no hard sell
Book Your Free 20-Min Call
"""
    msg = MIMEText(html, "html")
    msg["Subject"] = f"Your Trust Snapshot is ready - Score: {score}/100"
    msg["From"] = gmail_user
    msg["To"] = prospect_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
    except Exception:
        pass

@router.post("/trust-snapshot", response_model=TrustSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def submit_trust_snapshot(req: TrustSnapshotRequest, request: Request, db: AsyncSession = Depends(get_db)):
    org = await _get_or_create_default_org(db)
    user = await _get_or_create_system_user(db, org.id)
    website = req.website.strip()
    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"
    lead = Lead(organisation_id=org.id, business_name=req.full_name, website=website, email=req.email, source="trust_snapshot_landing")
    db.add(lead)
    await db.flush()
    scan = None
    try:
        scan = await trigger_scan(db, lead.id, org.id, user.id, ScanType.full)
    except Exception as e:
        scan = None
    score_response = None
    try:
        if scan and scan.status == ScanStatus.completed:
            score_record = await compute_trust_score(db, scan.id, org.id, lead.id, user.id)
            score_response = build_score_response(score_record)
    except Exception as e:
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
        try:
            _send_owner_notification(business_name=req.full_name, lead_email=req.email, website=website, score=int(overall_pct), grade=grade_label, issues=issues_data, actions=actions_data, pillars=pillars_data, lead_id=str(lead.id))
        except Exception:
            pass
        try:
            _send_prospect_email(prospect_email=req.email, business_name=req.full_name, score=int(overall_pct), grade=grade_label)
        except Exception:
            pass
        await db.commit()
        return TrustSnapshotResponse(success=True, message="Your Trust Snapshot is ready.", report_url="", lead_id=str(lead.id), score=int(overall_pct), grade=grade_label, issues_found=len(issues_data), standards_passed=score_response.overall_score, standards_total=score_response.overall_max, pillars=pillars_data, standards=standards_data, issues=issues_data, actions=actions_data)
    else:
        await db.commit()
        return TrustSnapshotResponse(success=True, message="Your Trust Snapshot is being generated.", report_url="", lead_id=str(lead.id), score=0, grade="", issues_found=0, standards_passed=0, standards_total=9, pillars=[], standards=[], issues=[], actions=[])


