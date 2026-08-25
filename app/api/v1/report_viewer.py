"""Public report viewing endpoint - no auth required."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.recommendations import AIRecommendation
from app.models import Lead
from app.models.scoring import TrustScoreRecord
from app.models.trust_scan import TrustScan
from app.services.scoring import build_score_response

router = APIRouter(prefix="/report", tags=["Public - Report Viewer"])


@router.get("/{report_id}", response_class=HTMLResponse)
async def view_trust_snapshot_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """View a Trust Snapshot report by ID. No auth required."""
    # Get the recommendation
    result = await db.execute(
        select(AIRecommendation).where(AIRecommendation.id == str(report_id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get the lead
    lead_result = await db.execute(select(Lead).where(Lead.id == str(report.lead_id)))
    lead = lead_result.scalar_one_or_none()
    
    # Get the score
    score_data = None
    if report.score_id:
        score_result = await db.execute(
            select(TrustScoreRecord).where(TrustScoreRecord.id == str(report.score_id))
        )
        score_record = score_result.scalar_one_or_none()
        if score_record:
            score_data = build_score_response(score_record)
    
    # Get the scan
    scan_result = await db.execute(
        select(TrustScan).where(TrustScan.lead_id == str(report.lead_id)).order_by(TrustScan.created_at.desc()).limit(1)
    )
    scan = scan_result.scalar_one_or_none()
    
    business_name = lead.business_name if lead else "Your Business"
    score = int(score_data.overall_percentage) if score_data else 0
    grade = score_data.grade.value if score_data else "Unknown"
    passed = scan.website_results.get("passed_count", 0) if scan and scan.website_results else 0
    total = scan.website_results.get("total_count", 9) if scan and scan.website_results else 9
    website = lead.website if lead else ""
    
    html_content = report.content or "No content available."
    
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trust Snapshot — {business_name} | Trust Trigger Agency</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"><style>body{{font-family:'Inter',sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6;padding:0;margin:0}}.header{{background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);color:white;padding:3rem 2rem;text-align:center}}.header h1{{font-size:2rem;margin:0 0 .5rem}}.header .score{{font-size:4rem;font-weight:800;color:#fbbf24;margin:.5rem 0}}.header .grade{{display:inline-block;padding:.25rem 1rem;border-radius:999px;font-size:.875rem;font-weight:600;background:rgba(251,191,36,.2);color:#fbbf24;border:1px solid rgba(251,191,36,.3)}}.content{{max-width:800px;margin:0 auto;padding:2rem;background:white;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.06);margin-top:-2rem;position:relative;z-index:10}}.content h2{{font-size:1.5rem;margin:1.5rem 0 .75rem;color:#0f172a;border-bottom:2px solid #fbbf24;padding-bottom:.5rem}}.content h3{{font-size:1.125rem;margin:1rem 0 .5rem;color:#334155}}.content ul{{padding-left:1.5rem;margin:.5rem 0}}.content li{{margin:.25rem 0;color:#475569}}.content p{{margin:.5rem 0;color:#475569}}.footer{{text-align:center;padding:2rem;color:#94a3b8;font-size:.875rem;max-width:800px;margin:0 auto}}.btn{{display:inline-block;padding:.75rem 2rem;background:#f59e0b;color:white;border-radius:8px;text-decoration:none;font-weight:600;margin:1rem 0}}.btn:hover{{background:#d97706}}.meta{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0;font-size:.875rem}}.meta-item{{background:#f8fafc;padding:.75rem 1rem;border-radius:8px;border:1px solid #e2e8f0}}.meta-label{{color:#64748b;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em}}.meta-value{{font-weight:600;color:#0f172a}}</style></head><body>
<div class="header"><p style="font-size:.875rem;opacity:.7;margin:0 0 1rem">Powered by The Trust Trigger Transformation Method™</p><h1>Trust Snapshot™</h1><p style="opacity:.8;margin:0 0 .5rem">{business_name}</p><div class="score">{score}<span style="font-size:1.25rem;opacity:.5">/100</span></div><div class="grade">{grade}</div><p style="margin-top:1rem;opacity:.7;font-size:.875rem">{website}</p></div>
<div class="content"><div class="meta"><div class="meta-item"><div class="meta-label">Trust Score</div><div class="meta-value">{score}/100</div></div><div class="meta-item"><div class="meta-label">Grade</div><div class="meta-value">{grade}</div></div><div class="meta-item"><div class="meta-label">Website Standards</div><div class="meta-value">{passed}/{total} passed</div></div><div class="meta-item"><div class="meta-label">Report Generated</div><div class="meta-value">{report.created_at.strftime('%d %B %Y') if report.created_at else 'Today'}</div></div></div>{html_content}
<p style="text-align:center;margin-top:2rem"><a href="#get-snapshot" class="btn" onclick="window.location.href='https://srv16.aisoftllc.com/agent_sites/4ab461110a3f.html'">Ready to improve your score? →</a></p>
</div>
<div class="footer"><p>Trust Trigger Agency™ — We help businesses earn and maintain trust online.</p><p style="font-size:.75rem;margin-top:.5rem">Powered by The Trust Trigger Transformation Method™</p></div>
</body></html>"""
    
    return HTMLResponse(content=html)