"""Workflow Engine - SQLAlchemy models for persistence."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum
class ProjectDBStatus(str, enum.Enum):
    new = "new"
    active = "active"
    paused = "paused"
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
    service_pages = "service_pages"
    about_page = "about_page"
    faq_generation = "faq_generation"
    email_sequence = "email_sequence"
    google_business_posts = "google_business_posts"
    social_media_posts = "social_media_posts"
    wordpress_publish = "wordpress_publish"
    trust_snapshot_report = "trust_snapshot_report"
    before_after_report = "before_after_report"
    monthly_monitoring_report = "monthly_monitoring_report"
    proposal_generation = "proposal_generation"
    client_notification = "client_notification"
    qa_review = "qa_review"

class ProjectDB(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str] = mapped_column(String(512), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ProjectDBStatus] = mapped_column(SAEnum(ProjectDBStatus), default=ProjectDBStatus.new, nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), default="trust_transformation")
    price: Mapped[float] = mapped_column(Float, default=995.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    tasks = relationship("TaskDB", back_populates="project", cascade="all, delete-orphan")

class TaskDB(Base):
    __tablename__ = "workflow_tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    type: Mapped[TaskDBType] = mapped_column(SAEnum(TaskDBType), nullable=False)
    status: Mapped[TaskDBStatus] = mapped_column(SAEnum(TaskDBStatus), default=TaskDBStatus.pending, nullable=False)
    depends_on: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[list] = mapped_column(JSON, default=list)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    output: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewed_by: Mapped[str] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)
    project = relationship("ProjectDB", back_populates="tasks")
