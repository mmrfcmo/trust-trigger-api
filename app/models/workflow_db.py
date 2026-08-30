"""Workflow Engine - SQLAlchemy models for persistence."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum
class ProjectDBStatus(str, enum.Enum):
    new = "new"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    monitoring = "monitoring"

class TaskDBStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"
    approved = "approved"
    rejected = "rejected"
    awaiting_review = "awaiting_review"

class TaskDBType(str, enum.Enum):
    website_scan = "website_scan"
    google_business_scan = "google_business_scan"
    trust_score = "trust_score"
    evidence_capture = "evidence_capture"
    homepage_copy = "homepage_copy"
    email_sequence = "email_sequence"
    google_business_posts = "google_business_posts"
    social_media_posts = "social_media_posts"
    trust_snapshot_report = "trust_snapshot_report"

class ProjectDB(Base):
    __tablename__ = "projects"
    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id = mapped_column(String(36), ForeignKey("leads.id"), nullable=False)
    business_name = mapped_column(String(255), nullable=False)
    website = mapped_column(String(512), nullable=False)
    email = mapped_column(String(255), nullable=False)
    status = mapped_column(SAEnum(ProjectDBStatus), default=ProjectDBStatus.new, nullable=False)
    product_type = mapped_column(String(50), default="trust_transformation")
    price = mapped_column(Float, default=995.0)
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    tasks = relationship("TaskDB", back_populates="project", cascade="all, delete-orphan")

class TaskDB(Base):
    __tablename__ = "workflow_tasks"
    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    type = mapped_column(SAEnum(TaskDBType), nullable=False)
    status = mapped_column(SAEnum(TaskDBStatus), default=TaskDBStatus.pending, nullable=False)
    depends_on = mapped_column(JSON, default=list)
    created_at = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds = mapped_column(Float, nullable=True)
    max_retries = mapped_column(Integer, default=3)
    retry_count = mapped_column(Integer, default=0)
    attempts = mapped_column(JSON, default=list)
    config = mapped_column(JSON, default=dict)
    output = mapped_column(JSON, default=dict)
    reviewed_by = mapped_column(String(36), nullable=True)
    reviewed_at = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes = mapped_column(Text, nullable=True)
    project = relationship("ProjectDB", back_populates="tasks")
