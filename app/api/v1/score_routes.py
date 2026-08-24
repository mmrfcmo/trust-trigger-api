"""Trust Scoring Engine: API routes."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.scoring import TrustScoreResponse, TrustScoreList
from app.services.scoring import (
    compute_trust_score,
    get_trust_score,
    get_trust_scores,
    get_latest_trust_score,
    build_score_response,
)
from app.models.trust_scan import TrustScan

router = APIRouter(prefix="/api/v1/scores", tags=["Trust Scoring Engine"])


@router.post("/compute/{scan_id}", response_model=TrustScoreResponse, status_code=status.HTTP_201_CREATED)
async def compute_score(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compute a trust score from a completed scan."""
    # Get scan to find lead_id
    result = await db.execute(
        __import__("sqlalchemy").select(TrustScan).where(
            TrustScan.id == scan_id,
            TrustScan.organisation_id == current_user.organisation_id,
        )
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    if scan.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scan must be completed before scoring")

    try:
        record = await compute_trust_score(
            db, scan_id, current_user.organisation_id, scan.lead_id, current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return build_score_response(record)


@router.get("", response_model=TrustScoreList)
async def list_scores(
    lead_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List trust score records."""
    records, total = await get_trust_scores(db, current_user.organisation_id, lead_id, skip, limit)
    return TrustScoreList(
        items=[build_score_response(r) for r in records],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/latest/{lead_id}", response_model=TrustScoreResponse)
async def get_latest_score(
    lead_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest trust score for a lead."""
    record = await get_latest_trust_score(db, lead_id, current_user.organisation_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No score found for this lead")
    return build_score_response(record)


@router.get("/{score_id}", response_model=TrustScoreResponse)
async def get_score_by_id(
    score_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trust score record."""
    record = await get_trust_score(db, score_id, current_user.organisation_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found")
    return build_score_response(record)