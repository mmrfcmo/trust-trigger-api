"""AI Recommendation Engine: API routes."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.models.recommendations import RecommendationType
from app.schemas.recommendations import (
    GenerateRecommendationRequest, RecommendationResponse, RecommendationList,
)
from app.services.recommendations import (
    generate_recommendation,
    get_recommendation,
    get_recommendations,
)

router = APIRouter(prefix="/api/v1/recommendations", tags=["AI Recommendation Engine"])


@router.post("/generate", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    req: GenerateRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI recommendation for a lead."""
    try:
        rec = await generate_recommendation(
            db, req.lead_id, req.recommendation_type,
            current_user.organisation_id, current_user.id,
            req.custom_instructions,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return RecommendationResponse.model_validate(rec)


@router.get("", response_model=RecommendationList)
async def list_recommendations(
    lead_id: Optional[uuid.UUID] = Query(None),
    rec_type: Optional[RecommendationType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI recommendations."""
    recs, total = await get_recommendations(db, current_user.organisation_id, lead_id, rec_type, skip, limit)
    return RecommendationList(
        items=[RecommendationResponse.model_validate(r) for r in recs],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation_by_id(
    rec_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific AI recommendation."""
    rec = await get_recommendation(db, rec_id, current_user.organisation_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return RecommendationResponse.model_validate(rec)