"""Trust Scoring Engine schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.scoring import TrustGrade


class PillarScore(BaseModel):
    name: str
    label: str
    score: int
    max_score: int
    percentage: float


class ImprovementAction(BaseModel):
    standard: str
    action: str
    detail: str
    effort: str  # low, medium, high
    passed: bool


class TrustScoreResponse(BaseModel):
    id: UUID
    organisation_id: UUID
    lead_id: UUID
    scan_id: Optional[UUID]

    overall_score: int
    overall_max: int
    overall_percentage: float
    grade: TrustGrade

    pillar_online_presence: int
    pillar_reputation: int
    pillar_engagement: int
    pillar_transparency: int
    pillar_technical: int

    pillars: List[PillarScore]
    improvements: List[ImprovementAction]
    priority_actions: List[ImprovementAction]
    created_at: datetime

    class Config:
        orm_mode = True


class ScoreHistoryPoint(BaseModel):
    date: datetime
    score: int
    grade: TrustGrade


class TrustScoreList(BaseModel):
    items: list[TrustScoreResponse]
    total: int
    page: int
    page_size: int