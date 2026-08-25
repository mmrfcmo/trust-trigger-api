"""AI Recommendation Engine: models and database."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class RecommendationType(str, enum.Enum):
    trust_snapshot = "trust_snapshot"
    transformation_report = "transformation_report"
    homepage_rewrite = "homepage_rewrite"
    about_page = "about_page"
    service_pages = "service_pages"
    faq = "faq"
    meta_titles = "meta_titles"
    meta_descriptions = "meta_descriptions"
    google_business_improvements = "google_business_improvements"
    review_request_email = "review_request_email"
    improvement_recommendations = "improvement_recommendations"


class AIRecommendation(Base):
    """Stores AI-generated recommendations for a lead."""
    __tablename__ = "ai_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    score_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_score_records.id"), nullable=True)

    recommendation_type: Mapped[RecommendationType] = mapped_column(SAEnum(RecommendationType), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    organisation = relationship("Organisation")
    lead = relationship("Lead")
    score_record = relationship("TrustScoreRecord")


class RecommendationFeedback(Base):
    """Client feedback on AI recommendations."""
    __tablename__ = "recommendation_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("ai_recommendations.id"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # approved, rejected, needs_changes
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    recommendation = relationship("AIRecommendation")