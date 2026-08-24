"""Publishing Engine: models."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class PublishingStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    published = "published"
    failed = "failed"
    rolled_back = "rolled_back"


class WordPressConnection(Base):
    """Stores WordPress connection details."""
    __tablename__ = "wordpress_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False)
    site_url: Mapped[str] = mapped_column(String(512), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    app_password: Mapped[str] = mapped_column(String(512), nullable=False)  # encrypted in production
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    last_test_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class PublishAction(Base):
    """Records each publish/rollback action."""
    __tablename__ = "publish_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False)
    connection_id: Mapped[str] = mapped_column(String(36), ForeignKey("wordpress_connections.id"), nullable=True)

    action: Mapped[str] = mapped_column(String(50), nullable=False)  # publish, rollback, test
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # page, post
    resource_title: Mapped[str] = mapped_column(String(255), nullable=True)
    wordpress_page_id: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[PublishingStatus] = mapped_column(SAEnum(PublishingStatus), default=PublishingStatus.draft, nullable=False)
    content_snapshot: Mapped[str] = mapped_column(Text, nullable=True)  # backup of original content
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))