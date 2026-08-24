"""Analytics Engine: models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class AgencyMetrics(Base):
    """Aggregated agency-wide metrics (updated periodically)."""
    __tablename__ = "agency_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, unique=True)

    # Revenue
    total_revenue: Mapped[float] = mapped_column(Float, default=0)
    monthly_recurring_revenue: Mapped[float] = mapped_column(Float, default=0)
    average_deal_size: Mapped[float] = mapped_column(Float, default=0)

    # Pipeline
    total_leads: Mapped[int] = mapped_column(Integer, default=0)
    active_projects: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0)  # percentage

    # Scores
    average_trust_score: Mapped[float] = mapped_column(Float, default=0)
    average_improvement: Mapped[float] = mapped_column(Float, default=0)  # percentage improvement

    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RevenueRecord(Base):
    """Individual revenue transactions."""
    __tablename__ = "revenue_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=True)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id"), nullable=True)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="GBP")
    revenue_type: Mapped[str] = mapped_column(String(50), nullable=False)  # one_time, monthly, setup
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, paid, refunded
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))