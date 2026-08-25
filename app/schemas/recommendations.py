"""AI Recommendation Engine schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.recommendations import RecommendationType


class GenerateRecommendationRequest(BaseModel):
    lead_id: UUID
    recommendation_type: RecommendationType
    custom_instructions: Optional[str] = None


class RecommendationResponse(BaseModel):
    id: UUID
    organisation_id: UUID
    lead_id: UUID
    score_id: Optional[UUID]
    recommendation_type: RecommendationType
    title: str
    content: str
    model_used: Optional[str]
    tokens_used: Optional[int]
    is_approved: bool
    created_at: datetime

    class Config:
        orm_mode = True


class RecommendationList(BaseModel):
    items: List[RecommendationResponse]
    total: int
    page: int
    page_size: int


class FeedbackCreate(BaseModel):
    recommendation_id: UUID
    status: str = Field(..., pattern=r"^(approved|rejected|needs_changes)$")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: UUID
    recommendation_id: UUID
    client_id: UUID
    status: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True