"""Trust Journey: score progression timeline, certificates, before/after."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TrustJourney(Base):
    """A client's trust transformation journey over time."""
    __tablename__ = "trust_journeys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, unique=True, index=True)

    # Baseline
    baseline_score: Mapped[int] = mapped_column(Integer, nullable=True)
    baseline_grade: Mapped[str] = mapped_column(String(50), nullable=True)
    baseline_scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Current
    current_score: Mapped[int] = mapped_column(Integer, nullable=True)
    current_grade: Mapped[str] = mapped_column(String(50), nullable=True)
    current_scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Improvement
    total_improvement: Mapped[float] = mapped_column(Float, default=0.0)
    total_actions_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_actions: Mapped[int] = mapped_column(Integer, default=0)

    # Certificate
    certificate_url: Mapped[str] = mapped_column(String(512), nullable=True)
    certificate_issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, completed, paused
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    milestones = relationship("JourneyMilestone", back_populates="journey", cascade="all, delete-orphan", order_by="JourneyMilestone.recorded_at.desc()")


class JourneyMilestone(Base):
    """A point in the journey — scan result at a specific date."""
    __tablename__ = "journey_milestones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_journeys.id"), nullable=False, index=True)
    score_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_score_records.id"), nullable=True)
    scan_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_scans.id"), nullable=True)

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    change_from_previous: Mapped[int] = mapped_column(Integer, default=0)
    actions_completed_since_last: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    journey = relationship("TrustJourney", back_populates="milestones")


class BeforeAfterReport(Base):
    """Before/after comparison report for a client."""
    __tablename__ = "before_after_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_journeys.id"), nullable=True)

    before_score: Mapped[int] = mapped_column(Integer, nullable=False)
    after_score: Mapped[int] = mapped_column(Integer, nullable=False)
    improvement: Mapped[int] = mapped_column(Integer, nullable=False)
    before_scan_id: Mapped[str] = mapped_column(String(36), nullable=True)
    after_scan_id: Mapped[str] = mapped_column(String(36), nullable=True)

    # Pillar comparisons
    before_pillars: Mapped[dict] = mapped_column(JSON, default=dict)
    after_pillars: Mapped[dict] = mapped_column(JSON, default=dict)

    # Actions taken
    actions_taken: Mapped[list] = mapped_column(JSON, default=list)

    # PDF
    report_url: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))