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


