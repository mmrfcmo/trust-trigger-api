"""Trust Framework: configurable categories, standards, weights, and recommendations."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class TrustFramework(Base):
    """Top-level framework. An agency can have multiple frameworks."""
    __tablename__ = "trust_frameworks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    categories = relationship("TrustCategory", back_populates="framework", cascade="all, delete-orphan")


class TrustCategory(Base):
    """A pillar/category within a framework (e.g. Online Presence, Reputation)."""
    __tablename__ = "trust_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    framework_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_frameworks.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False, default=25)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    framework = relationship("TrustFramework", back_populates="categories")
    standards = relationship("TrustStandardDef", back_populates="category", cascade="all, delete-orphan")


class TrustStandardDef(Base):
    """A specific standard within a category (e.g. HTTPS, Contact Page)."""
    __tablename__ = "trust_standard_defs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_categories.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    max_points: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    detection_type: Mapped[str] = mapped_column(String(50), default="regex")  # regex, meta_tag, http_header, api_call
    detection_pattern: Mapped[str] = mapped_column(Text, nullable=True)  # regex pattern or config
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = relationship("TrustCategory", back_populates="standards")
    recommendations = relationship("StandardRecommendation", back_populates="standard", cascade="all, delete-orphan")


class StandardRecommendation(Base):
    """Improvement recommendation for a standard. Configurable per standard."""
    __tablename__ = "standard_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    standard_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_standard_defs.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    effort: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    impact: Mapped[str] = mapped_column(String(50), nullable=True)  # expected score improvement
    ai_prompt_reference: Mapped[str] = mapped_column(String(100), nullable=True)  # links to prompt template
    evidence_required: Mapped[str] = mapped_column(Text, nullable=True)  # what proves this is done
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    standard = relationship("TrustStandardDef", back_populates="recommendations")