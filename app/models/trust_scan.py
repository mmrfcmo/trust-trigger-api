"""Trust Intelligence Engine: scanner models and database."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class ScanStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class ScanType(str, enum.Enum):
    website = "website"
    google_business = "google_business"
    full = "full"


class TrustScan(Base):
    __tablename__ = "trust_scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    scan_type: Mapped[ScanType] = mapped_column(SAEnum(ScanType), default=ScanType.full, nullable=False)
    status: Mapped[ScanStatus] = mapped_column(SAEnum(ScanStatus), default=ScanStatus.pending, nullable=False)
    target_url: Mapped[str] = mapped_column(String(512), nullable=True)
    google_place_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Results stored as JSON
    website_results: Mapped[dict] = mapped_column(JSON, default=dict)
    google_results: Mapped[dict] = mapped_column(JSON, default=dict)

    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    organisation = relationship("Organisation")
    lead = relationship("Lead")


class TrustStandard(Base):
    """Individual trust standard result from a scan."""
    __tablename__ = "trust_standards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trust_scans.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. website, google_business
    standard_name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. https, contact_page, rating
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)  # 0 or max_points for this standard
    max_points: Mapped[int] = mapped_column(Integer, default=0)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    scan = relationship("TrustScan")