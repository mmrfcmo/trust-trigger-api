"""Public API routes for Trust Snapshot lead capture (no auth required)."""
import uuid, smtplib, os, json, httpx
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
        return TrustSnapshotResponse(
            success=True,
            message="Your Trust Snapshot is ready.",
            report_url="/api/v1/public/report-view/" + str(lead.id),
            lead_id=str(lead.id),
            score=int(overall_pct),
            grade=grade_label,
            issues_found=len(issues_data),
            standards_passed=score_response.overall_score,
            standards_total=score_response.overall_max,
            pillars=pillars_data, standards=standards_data,
            issues=issues_data, actions=actions_data
        )
    else:
        await db.commit()
        return TrustSnapshotResponse(
            success=True, message="Your Trust Snapshot is being generated.",
            report_url="", lead_id=str(lead.id),
            score=0, grade="", issues_found=0, standards_passed=0, standards_total=9,
            pillars=[], standards=[], issues=[], actions=[]
        )

@router.get("/report-view/{lead_id}")
async def view_report(lead_id: str, db = Depends(get_db)):
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if not lead:
        return HTMLResponse(content="<h1>Report not found</h1>", status_code=404)
    score_result = await db.execute(
        select(TrustScoreRecord).where(TrustScoreRecord.lead_id == lead_id)
        .order_by(TrustScoreRecord.created_at.desc()).limit(1)
    )
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
    gs = {
        "Excellent Trust": "Your website is a strong trust engine. Visitors feel confident reaching out.",
        "Good Trust": "You're building trust well, but there are clear opportunities to convert more visitors.",
        "Average Trust": "Your website is losing potential customers. The gaps below are costing you enquiries.",
        "Weak Trust": "Significant trust gaps found. Most visitors are likely leaving without contacting you.",
        "At Risk": "Critical trust issues detected. Your website is actively repelling potential customers.",
    }.get(grade_label, "Assessment complete. Review the findings below.")
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
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Trust Snapshot — {business_name} | Trust Trigger Agency</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body{{font-family:"Inter",system-ui,sans-serif;-webkit-font-smoothing:antialiased;}}.bg-gradient{{background:linear-gradient(135deg,#0f172a,#1e293b);}}</style>
</head>
<body class="bg-stone-50 text-zinc-900">
  <div class="bg-gradient text-white py-14 px-6 text-center">
    <p class="text-xs font-semibold uppercase tracking-wider text-amber-400 mb-2">Trust Trigger Agency™</p>
    <h1 class="text-2xl sm:text-3xl font-bold">Trust Snapshot Report</h1>
    <p class="text-zinc-400 text-sm mt-1">Powered by The Trust Trigger Transformation Method™</p>
  </div>
  <div class="max-w-3xl mx-auto px-6 -mt-8">
    <div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 sm:p-8 mb-6">
      <div class="flex flex-col sm:flex-row items-center gap-6 mb-6">
        <div class="relative w-32 h-32 flex items-center justify-center shrink-0">
          <svg class="w-32 h-32 -rotate-90" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/><circle cx="60" cy="60" r="52" fill="none" stroke="#047857" stroke-width="8" stroke-linecap="round" stroke-dasharray="326.7" stroke-dashoffset="{326.7 - (score/100)*326.7}"/></svg>
          <div class="absolute text-center"><span class="text-5xl font-extrabold text-zinc-900">{score}</span><span class="text-sm font-semibold text-zinc-500">/100</span></div>
        </div>
        <div class="text-center sm:text-left">
          <h2 class="text-2xl font-bold mb-1 {gc}">{grade_label}</h2>
          <p class="text-lg font-medium text-zinc-900">{business_name}</p>
          <p class="text-sm text-zinc-400 break-all">{website}</p>
          <p class="text-sm text-zinc-500 mt-3 max-w-md">{gs}</p>
        </div>
      </div>
      <div class="border-t border-zinc-100 pt-4 flex flex-wrap gap-4 text-sm text-zinc-500">
        <span>📅 {datetime.now(timezone.utc).strftime("%d %B %Y")}</span>
        <span>📊 {len(pillars)} pillars assessed</span>
        <span>🔍 {len(issues)} issues found</span>
      </div>
    </div>'''
    if pillars:
        html += f'<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">Your Trust Breakdown</h3><div class="grid sm:grid-cols-2 gap-4">{ph}</div></div>'
    if issues:
        html += f'<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">3 Biggest Opportunities</h3><div class="space-y-3">{ih}</div></div>'
    if actions:
        html += f'<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6"><h3 class="font-semibold text-zinc-900 mb-4">What We Would Fix</h3><div class="space-y-3">{ah}</div></div>'
    html += f'''
    <div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 mb-6">
      <h3 class="font-semibold text-zinc-900 mb-3">What This Score Means</h3>
      <p class="text-sm text-zinc-600 leading-relaxed">Your Trust Snapshot measures your website against industry trust standards. Most local service businesses score under 50. A score of <strong>{score}/100</strong> puts you in a strong position, but the gaps above are likely costing you real enquiries every week.</p>
    </div>
    <div class="text-center rounded-2xl border-2 border-emerald-700 bg-white shadow-sm p-8 mb-6">
      <h3 class="text-xl font-bold mb-2">Want us to fix these for you?</h3>
      <p class="text-zinc-600 mb-6 max-w-md mx-auto">In a 20-minute Trust Review call, we will walk through your results and show you exactly what a Trust Transformation would deliver.</p>
      <a href="/extensive-report" class="inline-flex items-center gap-2 rounded-lg bg-emerald-700 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-emerald-800 transition">Book Your Free Trust Review →</a>
      <p class="text-xs text-zinc-400 mt-2">No obligation. 20 minutes.</p>
    </div>
    <div class="text-center pb-10"><p class="text-xs text-zinc-400">Trust Trigger Agency™ · Measure. Transform. Prove. Maintain.</p></div>
  </div>
</body>
</html>'''
    return HTMLResponse(content=html)

@router.get("/find-competitors")
async def find_competitors(
    industry: str,
    website: str = "",
    business_name: str = "",
):
    """Find 2 competitor websites for a given business using Google Places API."""
    api_key = settings.google_places_api_key
    if not api_key:
        return {"competitors": []}

    domain = website.replace("https://", "").replace("http://", "").split("/")[0]
    search_query = f"{industry} businesses"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {"query": search_query, "key": api_key, "maxresults": 5}
            response = await client.get(url, params=params)
            data = response.json()

            competitors = []
            if data.get("results"):
                for place in data["results"]:
                    place_id = place.get("place_id")
                    if place_id:
                        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                        details_params = {"place_id": place_id, "fields": "name,website,formatted_address", "key": api_key}
                        details_resp = await client.get(details_url, params=details_params)
                        details = details_resp.json()
                        result = details.get("result", {})
                        comp_website = result.get("website", "")
                        comp_name = result.get("name", place.get("name", ""))
                        if comp_website and domain not in comp_website:
                            comp_website_clean = comp_website.replace("https://", "").replace("http://", "").split("/")[0]
                            competitors.append({"name": comp_name, "website": comp_website_clean})
                            if len(competitors) >= 2:
                                break

            return {"competitors": competitors}
    except Exception:
        return {"competitors": []}

Commit ✅ then Manual Deploy on Render.

Also make sure httpx is in your requirements.txt. Let me check

03:42 PM
httpx is already in requirements. Now just:

✅ Commit the updated competitor_insights_page.py (I'll paste the latest version)

✅ Commit the updated public_routes.py (with the /find-competitors endpoint)

🔄 Manual Deploy on Render
Let me give you the updated competitor_insights_page.py that calls the new endpoint. Open this link, click the pencil ✏️, delete everything, and paste:

https://github.com/mmrfcmo/trust-trigger-api/blob/main/app/api/v1/competitor_insights_page.py

"""Competitor Trust Insights — served by the API with full JS support."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/competitor-insights", tags=["Public - Competitor Insights"])

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Competitor Trust Insights | Trust Trigger Agency</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body{font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased;background:#f8fafc;color:#1e293b;}.reveal{opacity:0;transform:translateY(20px);transition:opacity .6s ease-out,transform .6s ease-out;}.reveal.in-view{opacity:1;transform:none;}.gradient-header{background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);}@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.4}}.pulse-dot{animation:pulse-dot 1.5s ease-in-out infinite}</style>
</head>
<body class="antialiased">
<nav class="gradient-header border-b border-white/10 fixed top-0 left-0 right-0 z-50 h-16 flex items-center px-6"><div class="max-w-6xl mx-auto w-full flex items-center justify-between"><a href="#" class="flex items-center gap-2 text-white font-semibold text-sm"><span class="text-xl">&#x1F6E1;&#xFE0F;</span> Trust Trigger Agency</a><a href="/extensive-report" class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-medium text-white shadow-sm hover:bg-emerald-500 transition">Extensive Report &#8594;</a></div></nav>
<div class="h-16"></div>
<div class="max-w-6xl mx-auto px-6 py-12 sm:py-16">
<div class="text-center mb-12 reveal"><p class="text-sm font-semibold uppercase tracking-wider text-emerald-700 mb-3">Competitor Analysis</p><h1 class="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight mb-4 text-zinc-900">Competitor Trust Insights</h1><p class="text-zinc-600 max-w-2xl mx-auto text-lg leading-relaxed">Enter your website URL and industry. We'll find <strong>2 of your real competitors</strong> and compare trust scores side by side.</p></div>
<div id="inputSection" class="max-w-lg mx-auto reveal"><div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 sm:p-8"><div class="space-y-5">
<div><label class="block text-sm font-medium text-zinc-700 mb-1.5">Your Business Name</label><input id="businessName" type="text" placeholder="e.g. Ivy Dentistry Aesthetics" class="w-full rounded-xl border border-zinc-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"></div>
<div><label class="block text-sm font-medium text-zinc-700 mb-1.5">Your Website URL</label><input id="website" type="text" placeholder="e.g. ivydentistryaesthetics.co.uk" class="w-full rounded-xl border border-zinc-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"></div>
<div><label class="block text-sm font-medium text-zinc-700 mb-1.5">What does your business do?</label><input id="industry" type="text" placeholder="e.g. dentist, plumber, roofer" class="w-full rounded-xl border border-zinc-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition"><p class="text-xs text-zinc-400 mt-1.5">Just a keyword like "dentist" or "roofing".</p></div>
<button onclick="startCompare()" class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-700 px-5 py-3.5 text-sm font-semibold text-white shadow-sm hover:bg-emerald-800 transition">Compare My Score &#8594;</button><p class="text-xs text-center text-zinc-400">Free. No card. Takes ~1 minute.</p>
</div></div></div>
<div id="loadingSection" class="hidden max-w-2xl mx-auto reveal"><div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-8 sm:p-10 text-center"><h2 class="text-xl font-bold text-zinc-900 mb-6">Analysing Your Competitors</h2><div class="max-w-md mx-auto space-y-4 text-left">
<div class="flex items-center gap-4"><span id="cs1" class="w-6 h-6 rounded-full bg-zinc-200 flex items-center justify-center text-xs font-bold text-zinc-500 shrink-0">1</span><div class="flex-1"><p class="text-sm font-medium text-zinc-700">Scanning your website</p><p class="text-xs text-zinc-400">Running Trust Snapshot</p></div><span id="cd1" class="text-zinc-400 text-sm font-medium">&#x23F3;</span></div>
<div class="flex items-center gap-4"><span id="cs2" class="w-6 h-6 rounded-full bg-zinc-200 flex items-center justify-center text-xs font-bold text-zinc-500 shrink-0">2</span><div class="flex-1"><p class="text-sm font-medium text-zinc-700">Finding competitors</p><p class="text-xs text-zinc-400">Searching Google Places</p></div><span id="cd2" class="text-zinc-400 text-sm font-medium">&#x23F3;</span></div>
<div class="flex items-center gap-4"><span id="cs3" class="w-6 h-6 rounded-full bg-zinc-200 flex items-center justify-center text-xs font-bold text-zinc-500 shrink-0">3</span><div class="flex-1"><p class="text-sm font-medium text-zinc-700">Scanning competitor #1</p><p class="text-xs text-zinc-400" id="comp1Name">Waiting...</p></div><span id="cd3" class="text-zinc-400 text-sm font-medium">&#x23F3;</span></div>
<div class="flex items-center gap-4"><span id="cs4" class="w-6 h-6 rounded-full bg-zinc-200 flex items-center justify-center text-xs font-bold text-zinc-500 shrink-0">4</span><div class="flex-1"><p class="text-sm font-medium text-zinc-700">Scanning competitor #2</p><p class="text-xs text-zinc-400" id="comp2Name">Waiting...</p></div><span id="cd4" class="text-zinc-400 text-sm font-medium">&#x23F3;</span></div>
<div class="flex items-center gap-4"><span id="cs5" class="w-6 h-6 rounded-full bg-zinc-200 flex items-center justify-center text-xs font-bold text-zinc-500 shrink-0">5</span><div class="flex-1"><p class="text-sm font-medium text-zinc-700">Building comparison</p><p class="text-xs text-zinc-400">Analysing scores side by side</p></div><span id="cd5" class="text-zinc-400 text-sm font-medium">&#x23F3;</span></div>
</div><p id="compLoadingStatus" class="text-sm text-emerald-700 font-medium mt-8 pulse-dot">Scanning your website...</p></div></div>
<div id="resultsSection" class="hidden">
<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 sm:p-8 mb-8 reveal"><p class="text-xs font-semibold uppercase tracking-wider text-emerald-700 mb-1">Competitor Trust Comparison</p><h2 class="text-2xl sm:text-3xl font-bold text-zinc-900 mb-6">Your Business vs The Competition</h2><div class="overflow-x-auto"><table class="w-full text-left"><thead><tr class="border-b border-zinc-200"><th class="pb-3 pr-4 text-sm font-semibold text-zinc-500 uppercase tracking-wider">Metric</th><th id="hdrYou" class="pb-3 px-4 text-sm font-semibold text-emerald-700 uppercase tracking-wider"></th><th id="hdrC1" class="pb-3 px-4 text-sm font-semibold text-zinc-700 uppercase tracking-wider"></th><th id="hdrC2" class="pb-3 px-4 text-sm font-semibold text-zinc-700 uppercase tracking-wider"></th></tr></thead><tbody id="comparisonBody"></tbody></table></div></div>
<div class="grid sm:grid-cols-3 gap-4 mb-8 reveal">
<div class="rounded-2xl border-2 border-emerald-200 bg-emerald-50/50 shadow-sm p-6 text-center"><p class="text-xs font-semibold uppercase tracking-wider text-emerald-700 mb-2" id="yourLabel">Your Business</p><div class="text-5xl font-extrabold text-zinc-900 mb-1" id="yourScore">0</div><p class="text-sm text-zinc-500">Trust Score</p><div class="mt-3 w-full h-2 bg-zinc-200 rounded-full overflow-hidden"><div id="yourBar" class="h-full rounded-full bg-emerald-500" style="width:0%"></div></div></div>
<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 text-center"><p class="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2" id="c1Label">Competitor 1</p><div class="text-5xl font-extrabold text-zinc-900 mb-1" id="c1Score">0</div><p class="text-sm text-zinc-500">Trust Score</p><div class="mt-3 w-full h-2 bg-zinc-200 rounded-full overflow-hidden"><div id="c1Bar" class="h-full rounded-full bg-amber-500" style="width:0%"></div></div></div>
<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 text-center"><p class="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-2" id="c2Label">Competitor 2</p><div class="text-5xl font-extrabold text-zinc-900 mb-1" id="c2Score">0</div><p class="text-sm text-zinc-500">Trust Score</p><div class="mt-3 w-full h-2 bg-zinc-200 rounded-full overflow-hidden"><div id="c2Bar" class="h-full rounded-full bg-amber-500" style="width:0%"></div></div></div>
</div>
<div class="rounded-2xl border border-zinc-200 bg-white shadow-sm p-6 sm:p-8 mb-8 reveal"><h3 class="font-semibold text-zinc-900 mb-4">&#x1F4A1; Key Insights</h3><div id="insightsList" class="space-y-3"></div></div>
<div class="text-center rounded-2xl border-2 border-emerald-700 bg-white shadow-sm p-8 sm:p-12 mb-8 reveal"><span class="text-4xl mb-4 block">&#x1F6E1;&#xFE0F;</span><h3 class="text-2xl sm:text-3xl font-bold text-zinc-900 mb-3">Want to overtake your competition?</h3><p class="text-zinc-600 mb-6 max-w-lg mx-auto">Book a free 20-minute Trust Review and we'll show you exactly how to outperform every competitor in your area.</p><a href="/extensive-report" class="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-8 py-4 text-base font-semibold text-white shadow-sm hover:bg-emerald-800 transition">Start Your Full Trust Report &#8594;</a><p class="text-xs text-zinc-400 mt-3">Free. No obligation.</p></div>
</div>
<div id="errorSection" class="hidden max-w-lg mx-auto reveal"><div class="text-center rounded-2xl border border-red-200 bg-red-50 p-8"><span class="text-4xl mb-4 block">&#x26A0;&#xFE0F;</span><h2 class="text-xl font-bold text-zinc-900 mb-2">Something went wrong</h2><p id="compErrorMsg" class="text-zinc-600 mb-6"></p><button onclick="resetComp()" class="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-5 py-3 text-sm font-medium text-white shadow-sm hover:bg-emerald-800 transition">Try again &#8594;</button></div></div>
</div>
<footer class="gradient-header border-t border-white/10 py-12 px-6"><div class="max-w-5xl mx-auto text-center"><div class="flex items-center justify-center gap-2 text-white/80 text-sm mb-4"><span class="text-xl">&#x1F6E1;&#xFE0F;</span><span class="font-semibold">Trust Trigger Agency</span></div><p class="text-xs text-zinc-500 max-w-xl mx-auto leading-relaxed">The Trust Trigger Method&#8482; &#8212; Measure. Transform. Prove. Maintain.</p><p class="text-xs text-zinc-600 mt-4">&copy; 2026 Trust Trigger Agency&#8482;</p></div></footer>
<script>
var API='';function $(i){return document.getElementById(i);}function h(e){e.classList.add('hidden');}function s(e){e.classList.remove('hidden');}
function acs(s){var st=['cs1','cs2','cs3','cs4','cs5'],d=['cd1','cd2','cd3','cd4','cd5'];for(var i=0;i<st.length;i++){var el=$(st[i]),dt=$(d[i]);if(i<s){el.className='w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold shrink-0';el.textContent='\u2713';dt.textContent='\u2713';dt.className='text-emerald-600 text-sm font-medium';}else if(i===s){el.className='w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shrink-0 pulse-dot';dt.innerHTML='<span class=\"pulse-dot\">\u23F3</span>';dt.className='text-emerald-600 text-sm font-medium';}}}
function rs(n,u,e){return fetch('/api/v1/public/trust-snapshot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({full_name:n,website:u,email:e})}).then(function(r){return r.json();});}
function fc(i,w,b){return fetch('/api/v1/public/find-competitors?industry='+encodeURIComponent(i)+'&website='+encodeURIComponent(w)+'&business_name='+encodeURIComponent(b)).then(function(r){return r.json();}).catch(function(){return{competitors:[]};});}
function startCompare(){var n=$('businessName').value.trim(),u=$('website').value.trim(),i=$('industry').value.trim();if(!n||!u||!i){alert('Fill in all fields.');return;}h($('inputSection'));h($('errorSection'));h($('resultsSection'));s($('loadingSection'));acs(0);$('compLoadingStatus').textContent='Scanning your website...';var e='c'+Date.now()+'@temp.com';rs(n,u,e).then(function(you){acs(1);$('compLoadingStatus').textContent='Finding competitors...';return fc(i,u,n).then(function(r){var comps=r.competitors||[];acs(2);if(comps.length>0){var c1=comps[0];$('comp1Name').textContent=c1.website;$('compLoadingStatus').textContent='Scanning competitor #1...';return rs(c1.name||'Competitor 1','https://'+c1.website,'c1'+Date.now()+'@temp.com').then(function(c1r){var c2=comps.length>1?comps[1]:comps[0];$('comp2Name').textContent=c2.website;$('compLoadingStatus').textContent='Scanning competitor #2...';return rs(c2.name||'Competitor 2','https://'+c2.website,'c2'+Date.now()+'@temp.com').then(function(c2r){acs(4);$('compLoadingStatus').textContent='Building comparison...';setTimeout(function(){showComp(you,c1r,c2r,n,u,c1.name||'Competitor 1',c1.website,c2.name||'Competitor 2',c2.website);},500);}).catch(function(){acs(4);showComp(you,c1r,null,n,u,c1.name||'Competitor 1',c1.website,'Competitor 2','unknown');});}).catch(function(){acs(4);showComp(you,null,null,n,u,'Competitor 1','unknown','Competitor 2','unknown');});}else{acs(4);$('compLoadingStatus').textContent='No competitors found.';setTimeout(function(){showComp(you,null,null,n,u,'Not found','','Not found','');},500);}});}).catch(function(){h($('loadingSection'));$('compErrorMsg').textContent='Unable to scan your website.';s($('errorSection'));});}
function showComp(you,c1,c2,n,u,c1n,c1u,c2n,c2u){h($('loadingSection'));s($('resultsSection'));var ys=you.score||0,cs1=c1?(c1.score||0):'-',cs2=c2?(c2.score||0):'-';$('hdrYou').textContent=n+' (You)';$('hdrC1').textContent=c1n;$('hdrC2').textContent=c2n;$('yourLabel').textContent=n;$('yourScore').textContent=ys;setTimeout(function(){$('yourBar').style.width=ys+'%';},200);if(c1){$('c1Label').textContent=c1n;$('c1Score').textContent=cs1;setTimeout(function(){$('c1Bar').style.width=cs1+'%';},400);}else{$('c1Score').textContent='-';$('c1Label').textContent=c1n||'Not found';}if(c2){$('c2Label').textContent=c2n;$('c2Score').textContent=cs2;setTimeout(function(){$('c2Bar').style.width=cs2+'%';},600);}else{$('c2Score').textContent='-';$('c2Label').textContent=c2n||'Not found';}var tb=$('comparisonBody');tb.innerHTML='';function ar(l,y,c1v,c2v){var tr=document.createElement('tr');tr.className='border-b border-zinc-100';tr.innerHTML='<td class="py-3 pr-4 text-sm font-medium text-zinc-700">'+l+'</td><td class="py-3 px-4 text-sm font-semibold text-emerald-700">'+(y||'-')+'</td><td class="py-3 px-4 text-sm text-zinc-600">'+(c1v||'-')+'</td><td class="py-3 px-4 text-sm text-zinc-600">'+(c2v||'-')+'</td>';tb.appendChild(tr);}
ar('Trust Score',ys,cs1,cs2);ar('Grade',you.grade||'Unknown',c1?c1.grade||'Unknown':'-',c2?c2.grade||'Unknown':'-');if(you.pillars&&you.pillars.length){you.pillars.forEach(function(p){var c1p='-',c2p='-';if(c1&&c1.pillars){var c1pf=c1.pillars.find(function(x){return x.name===p.name;});if(c1pf){c1p=Math.round(c1pf.percentage)+'%';}}if(c2&&c2.pillars){var c2pf=c2.pillars.find(function(x){return x.name===p.name;});if(c2pf){c2p=Math.round(c2pf.percentage)+'%';}}ar(p.label,Math.round(p.percentage)+'%',c1p,c2p);});}
ar('Issues Found',you.issues_found||0,c1?(c1.issues_found||0):'-',c2?(c2.issues_found||0):'-');var il=$('insightsList');il.innerHTML='';var ins=[];if(ys>cs1&&ys>cs2){ins.push('<strong>You have the highest Trust Score</strong> among competitors.');}else if(ys<cs1&&ys<cs2){ins.push('<strong>Your Trust Score is lower than both competitors.</strong>');}else if(ys<cs1||ys<cs2){ins.push('<strong>You are behind at least one competitor.</strong>');}else{ins.push('<strong>You are competitive.</strong>');}
if(you.issues&&you.issues.length>0){ins.push('<strong>Top issue: '+you.issues[0].title+'</strong>');}
ins.forEach(function(t){var dv=document.createElement('div');dv.className='flex items-start gap-3 p-4 rounded-xl border border-zinc-200 bg-white';dv.innerHTML='<div class="text-sm text-zinc-700 leading-relaxed">'+t+'</div>';il.appendChild(dv);});setTimeout(function(){$('resultsSection').scrollIntoView({behavior:'smooth',block:'start'});},300);}
function resetComp(){h($('errorSection'));h($('resultsSection'));h($('loadingSection'));s($('inputSection'));window.scrollTo({top:0,behavior:'smooth'});}
try{document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('reveal');});var io=new IntersectionObserver(function(entries){entries.forEach(function(e){if(e.isIntersecting)e.target.classList.add('in-view');});},{threshold:0.1,rootMargin:'0px 0px -50px 0px'});document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});}catch(e){}
</script>
</body>
</html>"""

@router.get("", response_class=HTMLResponse)
async def competitor_insights():
    return HTMLResponse(content=PAGE)

@router.get("/", response_class=HTMLResponse)
async def competitor_insights_root():
    return HTMLResponse(content=PAGE)
