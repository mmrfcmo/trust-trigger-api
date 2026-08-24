"""Public API routes for Trust Snapshot lead capture (no auth required)."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Lead, Organisation, User, UserRole
from app.models.trust_scan import TrustScan, ScanType
from app.models.scoring import TrustScoreRecord
from app.models.recommendations import AIRecommendation, RecommendationType
from app.models.trust_journey import TrustJourney, JourneyMilestone
from app.services.lead_intelligence import calculate_opportunity_score
from app.services.trust_scanner import run_scan as trigger_scan
from app.services.scoring import compute_trust_score, build_score_response
from app.services.recommendations import generate_recommendation
from app.core.security import hash_password
from pydantic import BaseModel, Field, EmailStr

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


@router.post("/trust-snapshot", response_model=TrustSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def submit_trust_snapshot(
    req: TrustSnapshotRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive a Trust Snapshot request from the landing page.
    
    This creates a lead, runs a scan, computes a score, generates a report,
    and returns a URL to view the result. No authentication required.
    """
    # 1. Find or create a default organisation for public leads
    org = await _get_or_create_default_org(db)
    
    # 2. Find or create a default system user
    user = await _get_or_create_system_user(db, org.id)
    
    # 3. Normalise the website URL
    website = req.website.strip()
    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"
    
    # 4. Create the lead
    lead_data = {
        "business_name": req.full_name,
        "website": website,
        "email": req.email,
        "source": "trust_snapshot_landing",
    }
    score_val, reason = calculate_opportunity_score(lead_data)
    
    lead = Lead(
        organisation_id=org.id,
        business_name=req.full_name,
        website=website,
        email=req.email,
        source="trust_snapshot_landing",
        opportunity_score=score_val,
        opportunity_reason=reason,
    )
    db.add(lead)
    await db.flush()
    
    # 5. Run the trust scan
    try:
        scan = await trigger_scan(db, lead.id, org.id, user.id, ScanType.full)
    except Exception as e:
        scan = None
    
    # 6. Compute the trust score
    score_response = None
    if scan and scan.status == "completed":
        try:
            record = await compute_trust_score(db, scan.id, org.id, lead.id, user.id)
            score_response = build_score_response(record)
        except Exception:
            pass
    
    # 7. Generate the Trust Snapshot report
    report_content = None
    if score_response:
        try:
            rec = await generate_recommendation(
                db, lead.id, RecommendationType.trust_snapshot,
                org.id, user.id,
            )
            report_content = rec
        except Exception:
            pass
    
    # 8. Create a Trust Journey entry
    if score_response:
        journey = TrustJourney(
            organisation_id=org.id,
            lead_id=lead.id,
            baseline_score=int(score_response.overall_percentage),
            baseline_grade=score_response.grade.value,
            baseline_scanned_at=datetime.now(timezone.utc),
            current_score=int(score_response.overall_percentage),
            current_grade=score_response.grade.value,
            current_scanned_at=datetime.now(timezone.utc),
            status="active",
        )
        db.add(journey)
        await db.flush()
        
        # Add the first milestone
        milestone = JourneyMilestone(
            journey_id=journey.id,
            score_id=score_response.id if hasattr(score_response, 'id') else None,
            scan_id=scan.id if scan else None,
            score=int(score_response.overall_percentage),
            grade=score_response.grade.value,
            change_from_previous=0,
            summary=f"Initial Trust Snapshot completed. Score: {score_response.overall_percentage}%",
        )
        db.add(milestone)
    
    await db.commit()
    
    # Build response
    report_url = ""
    if report_content:
        report_url = f"/report/{report_content.id}"
    
    return TrustSnapshotResponse(
        success=True,
        message="Your Trust Snapshot is ready. We'll send it to your email shortly.",
        report_url=report_url,
        lead_id=str(lead.id),
    )


async def _get_or_create_default_org(db: AsyncSession) -> Organisation:
    """Get or create the default organisation for public signups."""
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
    """Get or create a system user for automated operations."""
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
            password_hash=hash_password(str(uuid.uuid4())),  # Random password, never used for login
            full_name="Trust Trigger System",
            role=UserRole.admin,
            organisation_id=org_id,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()
    return user