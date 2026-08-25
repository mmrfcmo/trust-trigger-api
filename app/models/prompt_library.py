"""Prompt Library: versioned, editable prompts stored in the database."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class PromptCategory(str, enum.Enum):
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
    proposal_generation = "proposal_generation"
    trust_journey_summary = "trust_journey_summary"
    custom = "custom"


class PromptTemplate(Base):
    """Versioned, editable prompt templates stored in the database."""
    __tablename__ = "prompt_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=True, index=True)
    category: Mapped[PromptCategory] = mapped_column(SAEnum(PromptCategory), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.7)
    max_tokens: Mapped[int] = mapped_column(default=2000)
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini")
    variables: Mapped[list] = mapped_column(JSON, default=list)  # expected context variables
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class PromptVersionHistory(Base):
    """Audit trail for prompt changes."""
    __tablename__ = "prompt_version_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id: Mapped[str] = mapped_column(String(36), ForeignKey("prompt_templates.id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.7)
    max_tokens: Mapped[int] = mapped_column(default=2000)
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini")
    change_notes: Mapped[str] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))