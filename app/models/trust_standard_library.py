"""Trust Standard Library: each standard as a rich, configurable object with methodology, evidence, and verification."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TrustStandardLibrary(Base):
    """Master library of all trust standards. This is the core IP of the platform."""
    __tablename__ = "trust_standard_library"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=True, index=True)

    # Identity
    standard_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # e.g. "testimonials_v1"
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "Client Testimonials"
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Classification
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # online_presence, reputation, engagement, transparency, technical
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)
    importance: Mapped[str] = mapped_column(String(20), default="medium")  # critical, high, medium, low

    # Scoring
    weight: Mapped[int] = mapped_column(Integer, default=5)  # 1-10 importance weight
    max_points: Mapped[int] = mapped_column(Integer, nullable=False)
    scoring_logic: Mapped[str] = mapped_column(Text, nullable=True)  # Description of how scoring works

    # Detection
    detection_type: Mapped[str] = mapped_column(String(50), nullable=False)  # regex, meta_tag, http_header, api_call, html_selector, ai_analysis
    detection_pattern: Mapped[str] = mapped_column(Text, nullable=True)  # regex pattern, CSS selector, API endpoint
    detection_notes: Mapped[str] = mapped_column(Text, nullable=True)  # Implementation guidance
    fallback_detection: Mapped[str] = mapped_column(Text, nullable=True)  # Alternative detection method

    # Evidence
    evidence_required: Mapped[str] = mapped_column(Text, nullable=True)  # What constitutes proof
    evidence_type: Mapped[str] = mapped_column(String(50), default="screenshot")  # screenshot, html_snapshot, api_response, manual_confirmation
    verification_method: Mapped[str] = mapped_column(Text, nullable=True)  # How to verify the improvement

    # Recommendations
    recommendation_action: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation_detail: Mapped[str] = mapped_column(Text, nullable=False)
    effort: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    estimated_time: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g. "30 mins", "2 hours"
    expected_impact: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g. "+4 points", "+15% trust"

    # AI
    prompt_reference: Mapped[str] = mapped_column(String(100), nullable=True)  # Links to prompt_library category
    ai_context_hint: Mapped[str] = mapped_column(Text, nullable=True)  # Extra context for AI generation

    # Methodology
    methodology_reference: Mapped[str] = mapped_column(Text, nullable=True)  # Internal methodology document link
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    created_by: Mapped[str] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EvidenceCapture(Base):
    """Evidence of trust improvements — before/after snapshots, HTML, screenshots."""
    __tablename__ = "evidence_captures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    standard_library_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_standard_library.id"), nullable=True)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_journeys.id"), nullable=True)

    # Phase
    phase: Mapped[str] = mapped_column(String(20), nullable=False)  # before, after

    # Content
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)  # screenshot, html_snapshot, api_response, manual_note
    content_url: Mapped[str] = mapped_column(String(512), nullable=True)  # URL to stored screenshot/image
    html_snapshot: Mapped[str] = mapped_column(Text, nullable=True)  # Full HTML backup
    text_content: Mapped[str] = mapped_column(Text, nullable=True)  # Extracted text
    notes: Mapped[str] = mapped_column(Text, nullable=True)  # Human notes

    # Verification
    verified_by: Mapped[str] = mapped_column(String(36), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, verified, rejected

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TrustDelta(Base):
    """The measurable improvement between before and after for a specific standard."""
    __tablename__ = "trust_deltas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    standard_library_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_standard_library.id"), nullable=True)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_journeys.id"), nullable=True)

    standard_name: Mapped[str] = mapped_column(String(255), nullable=False)
    before_score: Mapped[int] = mapped_column(Integer, default=0)
    after_score: Mapped[int] = mapped_column(Integer, default=0)
    delta: Mapped[int] = mapped_column(Integer, default=0)  # after - before
    before_evidence_id: Mapped[str] = mapped_column(String(36), nullable=True)
    after_evidence_id: Mapped[str] = mapped_column(String(36), nullable=True)
    action_taken: Mapped[str] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))