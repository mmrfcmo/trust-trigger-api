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
from app.models.recommendations import AIRecommendation, RecommendationType
from app.models.trust_journey import TrustJourney, JourneyMilestone
from app.services.lead_intelligence import calculate_opportunity_score
from app.services.trust_scanner import run_scan as trigger_scan
from app.services.scoring import compute_trust_score, build_score_response
from app.services.recommendations import generate_recommendation
from app.core.security import hash_password
from pydantic import BaseModel, Field, EmailStr
import smtplib
import os
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
    result = await db.execute(
        select(Organisation).where(Organisation.slug == "trust-snapshot-leads")
    )
    org = result.scalar_one_or_none()
    if not org:
        org = Organisation(
            name="Trust Snapshot Leads",
            slug="trust-snapshot-leads",
            settings={"is_public_lead_capture": True},
        )
        db.add(org)
        await db.flush()
    return org

async def _get_or_create_system_user(db: AsyncSession, org_id: uuid.UUID) -> User:
    result = await db.execute(
        select(User).where(
            User.email == "system@trusttriggeragency.com",
            User.organisation_id == org_id,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email="system@trusttriggeragency.com",
            password_hash=hash_password(str(uuid.uuid4())),
            full_name="Trust Trigger System",
            role=UserRole.admin,
            organisation_id=org_id,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()
    return user

def _send_owner_notification(business_name, lead_email, website, score, grade, issues, actions, pillars, lead_id):
    owner_email = os.environ.get("OWNER_EMAIL", "mmr1979@hotmail.co.uk")
    gmail_user = os.environ.get("GMAIL_EMAIL", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_password:
        return
    pillars_html = ""
    for p in pillars:
        color = "red" if p.get("percentage", 0) < 40 else "amber" if p.get("percentage", 0) < 70 else "green"
        pillars_html += f"""<tr><td style="padding:8px 12px;color:#64748b;font-size:14px;border-bottom:1px solid #f1f5f9">{p.get('label', '')}</td><td style="padding:8px 12px;font-weight:600;text-align:right;border-bottom:1px solid #f1f5f9">{p.get('score', 0)}/{p.get('max_score', 0)}</td><td style="padding:8px 12px;text-align:right;border-bottom:1px solid #f1f5f9"><span style="color:{color};font-weight:600">{p.get('percentage', 0)}%</span></td></tr>"""
    issues_html = ""
    for iss in issues[:5]:
        issues_html += f"""<div style="display:flex;align-items:flex-start;gap:8px;padding:8px 12px;background:#fef2f2;border-radius:8px;margin-bottom:6px;font-size:13px"><span style="color:#ef4444;flex-shrink:0">⚠️</span><div><strong style="color:#1e293b">{iss.get('title', '')}</strong><br><span style="color:#64748b">{iss.get('detail', '')}</span></div></div>"""
    actions_html = ""
    effort_colors = {"low": "background:#dcfce7;color:#166534", "medium": "background:#fef3c7;color:#92400e", "high": "background:#fee2e2;color:#991b1b"}
    for i, act in enumerate(actions[:5]):
        ec = effort_colors.get(act.get('effort', 'medium'), "background:#f1f5f9;color:#475569")
        actions_html += f"""<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:#f8fafc;border-radius:8px;margin-bottom:4px;font-size:13px"><span style="font-weight:700;color:#f59e0b;font-size:12px">#{i+1}</span><span style="flex:1;color:#1e293b">{act.get('title', '')}</span><span style="font-size:11px;padding:2px 8px;border-radius:999px;{ec}">{act.get('effort', 'medium').title()}</span></div>"""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="font-family:Inter,sans-serif;background:#f8fafc;padding:2rem;margin:0"><div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.06)"><div style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:2rem;text-align:center"><div style="font-size:2.5rem;margin-bottom:.5rem">🛡️</div><h1 style="color:white;margin:0;font-size:1.5rem">New Trust Snapshot Lead</h1><p style="color:#94a3b8;margin:.5rem 0 0">A prospect has requested their Trust Snapshot</p></div><div style="padding:2rem"><div style="background:#f8fafc;border-radius:8px;padding:1.5rem;margin-bottom:1.5rem"><table style="width:100%;border-collapse:collapse"><tr><td style="padding:8px 12px;color:#64748b;font-size:14px;border-bottom:1px solid #f1f5f9">Business</td><td style="padding:8px 12px;font-weight:600;text-align:right;border-bottom:1px solid #f1f5f9">{business_name}</td></tr><tr><td style="padding:8px 12px;color:#64748b;font-size:14px;border-bottom:1px solid #f1f5f9">Website</td><td style="padding:8px 12px;font-weight:600;text-align:right;border-bottom:1px solid #f1f5f9;word-break:break-all">{website}</td></tr><tr><td style="padding:8px 12px;color:#64748b;font-size:14px;border-bottom:1px solid #f1f5f9">Email</td><td style="padding:8px 12px;font-weight:600;text-align:right;border-bottom:1px solid #f1f5f9">{lead_email}</td></tr><tr><td style="padding:8px 12px;color:#64748b;font-size:14px;border-bottom:1px solid #f1f5f9">Trust Score</td><td style="padding:8px 12px;font-weight:600;text-align:right;border-bottom:1px solid #f1f5f9">{score}/100 <span style="color:#f59e0b">({grade})</span></td></tr></table></div><h2 style="font-size:16px;color:#1e293b;margin:0 0 12px">Score Breakdown</h2><table style="width:100%;border-collapse:collapse;margin-bottom:24px"><tr style="background:#f8fafc"><th style="padding:8px 12px;text-align:left;font-size:12px;color:#64748b;text-transform:uppercase">Pillar</th><th style="padding:8px 12px;text-align:right;font-size:12px;color:#64748b;text-transform:uppercase">Score</th><th style="padding:8px 12px;text-align:right;font-size:12px;color:#64748b;text-transform:uppercase">%</th></tr>{pillars_html}</table><h2 style="font-size:16px;color:#1e293b;margin:0 0 12px">Top Issues</h2>{issues_html}<h2 style="font-size:16px;color:#1e293b;margin:24px 0 12px">Priority Actions</h2>{actions_html}<div style="text-align:center;margin-top:24px;padding-top:24px;border-top:1px solid #e2e8f0"><p style="color:#94a3b8;font-size:13px;margin:0 0 8px">Lead ID: {lead_id}</p><p style="color:#94a3b8;font-size:13px;margin:0">Follow up with this lead to book their 20-min call.</p></div></div><div style="background:#f8fafc;padding:1rem;text-align:center;border-top:1px solid #e2e8f0"><p style="color:#94a3b8;font-size:12px;margin:0">Trust Trigger Agency™</p></div></div></body></html>"""
    msg = MIMEText(html, "html")
    msg["Subject"] = f"New Trust Snapshot: {business_name} — Score: {score}/100 ({grade})"
    msg["From"] = gmail_user
    msg["To"] = owner_email
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
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="font-family:Inter,sans-serif;background:#f8fafc;padding:2rem;margin:0"><div style="max-width:560px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.06)"><div style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:2rem;text-align:center"><div style="font-size:2.5rem;margin-bottom:.5rem">🛡️</div><h1 style="color:white;margin:0;font-size:1.5rem">Thanks, {business_name}!</h1><p style="color:#94a3b8;margin:.5rem 0 0">Your Trust Snapshot is ready</p></div><div style="padding:2rem;text-align:center"><div style="display:inline-flex;align-items:baseline;gap:4px;background:#f8fafc;padding:16px 32px;border-radius:12px;margin-bottom:20px"><span style="font-size:48px;font-weight:800;color:#1e293b">{score}</span><span style="font-size:18px;color:#94a3b8">/100</span><span style="font-size:14px;font-weight:600;color:#f59e0b;background:#fef3c7;padding:4px 12px;border-radius:999px;margin-left:8px">{grade}</span></div><h2 style="font-size:18px;color:#1e293b;margin:0 0 12px">Your digital trust score is {score}/100</h2><p style="color:#64748b;font-size:15px;line-height:1.6;margin:0 0 20px">The best way to understand what this means and how to improve it is a quick <strong style="color:#1e293b">20-minute no-obligation screen-share</strong> with a Trust Analyst. We'll walk through your results together, explain exactly what's affecting your score, and show you what you can fix right away.</p><div style="background:#f8fafc;border-radius:12px;padding:20px;margin-bottom:24px;text-align:left"><p style="font-size:14px;font-weight:600;color:#1e293b;margin:0 0 12px">On your call, you'll get:</p><div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:14px;color:#475569"><span style="color:#22c55e">✅</span><span>Your full score breakdown explained in plain English</span></div><div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:14px;color:#475569"><span style="color:#22c55e">✅</span><span>Specific issues found on your website and how to fix them</span></div><div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:14px;color:#475569"><span style="color:#22c55e">✅</span><span>Quick wins you can implement immediately</span></div><div style="display:flex;align-items:flex-start;gap:8px;font-size:14px;color:#475569"><span style="color:#22c55e">✅</span><span>No obligation — honest advice, no hard sell</span></div></div><a href="YOUR_CALENDLY_LINK_HERE" style="display:inline-block;padding:16px 32px;background:#f59e0b;color:white;text-decoration:none;border-radius:12px;font-size:16px;font-weight:700;box-shadow:0 4px 12px rgba(245,158,11,0.3)">📅 Book Your Free 20-Min Call →</a><p style="color:#94a3b8;font-size:13px;margin:20px 0 0;line-height:1.5">Prefer to speak to someone directly?<br>Call us on <strong style="color:#1e293b">+44 208 591 1163</strong> or email <strong style="color:#1e293b">info@trusttriggeragency.com</strong></p></div><div style="background:#f8fafc;padding:1rem;text-align:center;border-top:1px solid #e2e8f0"><p style="color:#94a3b8;font-size:12px;margin:0">Trust Trigger Agency™ — London, UK</p></div></div></body></html>"""
    msg = MIMEText(html, "html")
    msg["Subject"] = f"Your Trust Snapshot is ready — Score: {score}/100"
    msg["From"] = gmail_user
    msg["To"] = prospect_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
    except Exception:
        pass

@router.post("/trust-snapshot", response_model=TrustSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def submit_trust_snapshot(
    req: TrustSnapshotRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    org = await _get_or_create_default_org(db)
    user = await _get_or_create_system_user(db, org.id)
    website = req.website.strip()
    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"
    lead = Lead(
        organisation_id=org.id,
        business_name=req.full_name,
        website=website,
        email=req.email,
        source="trust_snapshot_landing",
    )
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
        return TrustSnapshotResponse(
            success=True,
            message="Your Trust Snapshot is ready. Check your email for the full breakdown.",
            report_url="",
            lead_id=str(lead.id),
            score=int(overall_pct),
            grade=grade_label,
            issues_found=len(issues_data),
            standards_passed=score_response.overall_score,
            standards_total=score_response.overall_max,
            pillars=pillars_data,
            standards=standards_data,
            issues=issues_data,
            actions=actions_data,
        )
    else:
        await db.commit()
        return TrustSnapshotResponse(
            success=True,
            message="Your Trust Snapshot is being generated. We'll notify you when it's ready.",
            report_url="",
            lead_id=str(lead.id),
            score=0,
            grade="",
            issues_found=0,
            standards_passed=0,
            standards_total=9,
            pillars=[],
            standards=[],
            issues=[],
            actions=[],
        )
