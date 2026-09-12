"""Public API routes for Trust Snapshot lead capture (no auth required)."""
import uuid, smtplib, os, json, httpx, re
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
from app.core.config import settings
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
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if not lead:
        return HTMLResponse(content="<h1>Report not found</h1>", status_code=404)
    score_result = await db.execute(select(TrustScoreRecord).where(TrustScoreRecord.lead_id == lead_id).order_by(TrustScoreRecord.created_at.desc()).limit(1))
    score_record = score_result.scalar_one_or_none()
    business_name = lead.business_name or "Your Business"
    website = lead.website or ""
    score = 0
    grade_label = "Unknown"
    pillars = []
    issues = []
    actions = []
    if score_record:
        try:
            sr = build_score_response(score_record)
            score = int(sr.overall_percentage)
            grade_label = sr.grade.value if hasattr(sr.grade, 'value') else str(sr.grade)
            for p in sr.pillars:
                pillars.append({"name": p.name, "label": p.label, "score": p.score, "max_score": p.max_score, "percentage": p.percentage})
            for imp in sr.improvements:
                if not imp.passed:
                    issues.append({"title": imp.action, "detail": imp.detail})
            for act in sr.priority_actions:
                actions.append({"title": act.action, "detail": act.detail, "effort": act.effort})
        except Exception:
            pass
    gc = "text-red-600"
    if score >= 80: gc = "text-emerald-700"
    elif score >= 60: gc = "text-emerald-600"
    elif score >= 40: gc = "text-amber-600"
    gs = {"Excellent Trust": "Your website is a strong trust engine. Visitors feel confident reaching out.", "Good Trust": "You're building trust well, but there are clear opportunities to convert more visitors.", "Average Trust": "Your website is losing potential customers. The gaps below are costing you enquiries.", "Weak Trust": "Significant trust gaps found. Most visitors are likely leaving without contacting you.", "At Risk": "Critical trust issues detected. Your website is actively repelling potential customers."}.get(grade_label, "Assessment complete. Review the findings below.")
    ph = ""
    if pillars:
        for p in pillars:
            pct = p["percentage"]
            bc = "bg-emerald-500" if pct >= 80 else ("bg-amber-500" if pct >= 50 else "bg-red-500")
            tc = "text-emerald-700" if pct >= 80 else ("text-amber-700" if pct >= 50 else "text-red-700")
            ph += f'<div class="rounded-xl border border-zinc-200 bg-white p-4"><div class="flex items-center justify-between mb-2"><span class="text-sm font-medium text-zinc-700">{p["label"]}</span><span class="text-sm font-semibold {tc}">{round(pct)}%</span></div><div class="w-full h-2.5 bg-zinc-100 rounded-full overflow-hidden"><div class="h-full rounded-full {bc}" style="width:{pct}%"></div></div></div>'
    ih = ""
    if issues:
        for i, issue in enumerate(issues[:5]):
            ih += f'<div class="flex items-start gap-3 p-4 rounded-xl border border-zinc-200 bg-white"><span class="shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-xs font-bold">{i+1}</span><div><p class="text-sm font-medium text-zinc-900">{issue["title"]}</p><p class="text-sm text-zinc-500 mt-0.5">{issue["detail"]}</p></div></div>'
    ah = ""
    if actions:
        for i, a in enumerate(actions[:4]):
            b = "Quick win" if a["effort"] == "low" else ("Medium effort" if a["effort"] == "medium" else "Larger project")
            bc2 = "bg-green-100 text-green-700" if a["effort"] == "low" else ("bg-amber-100 text-amber-700" if a["effort"] == "medium" else "bg-red-100 text-red-700")
            ah += f'<div class="flex items-start gap-3 p-4 rounded-xl border border-zinc-200 bg-white"><span class="shrink-0 w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold">{i+1}</span><div class="flex-1"><div class="flex items-center justify-between gap-2"><p class="text-sm font-medium text-zinc-900">{a["title"]}</p><span class="text-xs font-medium px-2 py-0.5 rounded-full shrink-0 {bc2}">{b}</span></div><p class="text-sm text-zinc-500 mt-0.5">{a["detail"]}</p></div></div>'
    html = f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trust Snapshot - {business_name} | Trust Trigger Agency</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"><script src="https://cdn.tailwindcss.com"></script><style>body{{font-family:"Inter",system-ui,sans-serif;-webkit-font-smoothing:antialiased;}}.bg-gradient{{background:linear-gradient(135deg,#0f172a,#1e293b);}}</style></head><body class="bg-stone-50 text-zinc-900"><div class="bg-gradient text-white py-14 px-6 text-center"><p class="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-2">Trust Trigger Agency</p><h1 class="text-2xl sm:text-3xl font-bold">Trust Snapshot Report</h1></div><div class="max-w-3xl mx-auto px-6 -mt-8"><div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 sm:p-8 mb-6"><div class="flex flex-col sm:flex-row items-center gap-6 mb-6"><div class="relative w-32 h-32 flex items-center justify-center shrink-0"><svg class="w-32 h-32 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle cx="60" cy="60" r="52" fill="none" stroke="#047857" stroke-width="8" stroke-linecap="round" stroke-dasharray="326.7" stroke-dashoffset="' + str(326.7 - (score/100)*326.7) + '"/></svg><div class="absolute text-center"><span class="text-5xl font-extrabold text-zinc-900">' + str(score) + '</span><span class="text-sm font-semibold text-zinc-500">/100</span></div></div><div class="text-center sm:text-left"><h2 class="text-2xl font-bold mb-1 ' + gc + '">' + grade_label + '</h2><p class="text-lg font-medium text-zinc-900">' + business_name + '</p><p class="text-sm text-zinc-400 break-all">' + website + '</p><p class="text-sm text-zinc-500 mt-3 max-w-md">' + gs + '</p></div></div><div class="border-t border-zinc-100 pt-4 flex flex-wrap gap-4 text-sm text-zinc-500"><span>' + datetime.now(timezone.utc).strftime("%d %B %Y") + '</span><span>' + str(len(pillars)) + ' pillars assessed</span><span>' + str(len(issues)) + ' issues found</span></div></div>'
    if pillars:
        html += '<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">Your Trust Breakdown</h3><div class="grid sm:grid-cols-2 gap-4">' + ph + '</div></div>'
    if issues:
        html += '<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">3 Biggest Opportunities</h3><div class="space-y-3">' + ih + '</div></div>'
    if actions:
        html += '<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">What We Would Fix</h3><div class="space-y-3">' + ah + '</div></div>'
    html += '<div class="text-center rounded-2xl border-2 border-emerald-700 bg-white shadow-sm p-8 mb-6"><h3 class="text-xl font-bold mb-2">Want us to fix these for you?</h3><p class="text-zinc-600 mb-6 max-w-md mx-auto">In a 20-minute Trust Review call, we will walk through your results.</p><a href="/extensive-report" class="inline-flex items-center gap-2 rounded-lg bg-emerald-700 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-emerald-800 transition">Book Your Free Trust Review</a></div></div></body></html>'
    return HTMLResponse(content=html)

@router.get("/find-competitors")
async def find_competitors(industry: str, website: str = "", business_name: str = ""):
    domain = website.replace("https://", "").replace("http://", "").split("/")[0]
    competitors = []
    names = {
        "dentist": [{"name": "City Dental Clinic", "site": "citydentalclinic.co.uk"}, {"name": "Smile Care Dental", "site": "smilecaredental.co.uk"}],
        "plumber": [{"name": "Pro Plumbing Services", "site": "proplumbingservices.co.uk"}, {"name": "Drain Right Plumbers", "site": "drainrightplumbers.co.uk"}],
        "roofer": [{"name": "Peak Roofing Solutions", "site": "peakroofing.co.uk"}, {"name": "Apex Roof Repairs", "site": "apexroofrepairs.co.uk"}],
        "electrician": [{"name": "Spark Pro Electrical", "site": "sparkproelectrical.co.uk"}, {"name": "Volt Wise Electricians", "site": "voltwise.co.uk"}],
        "gardener": [{"name": "Green Leaf Gardening", "site": "greenleafgardening.co.uk"}, {"name": "Garden Care Pro", "site": "gardencarepro.co.uk"}],
        "solicitor": [{"name": "City Law Partners", "site": "citylawpartners.co.uk"}, {"name": "Trust Legal Solicitors", "site": "trustlegalsolicitors.co.uk"}],
        "mechanic": [{"name": "Auto Care Garage", "site": "autocaregarage.co.uk"}, {"name": "Motive Services", "site": "motiveservices.co.uk"}],
        "accountant": [{"name": "Clear Books Accounting", "site": "clearbooksac.co.uk"}, {"name": "Tax Wise Partners", "site": "taxwisepartners.co.uk"}],
        "builder": [{"name": "Premier Builders UK", "site": "premierbuildersuk.co.uk"}, {"name": "Solid Foundations Ltd", "site": "solidfoundations.co.uk"}],
        "hairdresser": [{"name": "Style Studio Hair", "site": "stylestudiohair.co.uk"}, {"name": "Cuts & Colour Salon", "site": "cutsandcolour.co.uk"}],
    }
    industry_key = industry.lower()
    if industry_key not in names:
        industry_key = "dentist"
    for comp in names[industry_key][:2]:
        if comp["site"] != domain:
            competitors.append(comp)
    return {"competitors": competitors}
