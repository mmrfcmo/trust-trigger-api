"""Monitoring Engine: models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class MonitoringSchedule(Base):
    """Schedule for automatic monthly rescans."""
    __tablename__ = "monitoring_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, unique=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    interval_days: Mapped[int] = mapped_column(Integer, default=30)
    last_scan_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    next_scan_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    notify_on_improvement: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_decline: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ScoreHistory(Base):
    """Historical trust score data for trend tracking."""
    __tablename__ = "score_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    score_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_score_records.id"), nullable=True)

    overall_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    pillar_online_presence: Mapped[int] = mapped_column(Integer, default=0)
    pillar_reputation: Mapped[int] = mapped_column(Integer, default=0)
    pillar_engagement: Mapped[int] = mapped_column(Integer, default=0)
    pillar_transparency: Mapped[int] = mapped_column(Integer, default=0)
    pillar_technical: Mapped[int] = mapped_column(Integer, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class Alert(Base):
    """Alerts for score changes, renewal reminders, etc."""
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=True)

    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # score_improved, score_declined, renewal_due, scan_completed
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, critical
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))