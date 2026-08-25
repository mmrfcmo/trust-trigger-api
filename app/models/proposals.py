"""Proposal Engine: models and database."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Enum as SAEnum, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class ProposalStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    viewed = "viewed"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(SAEnum(ProposalStatus), default=ProposalStatus.draft, nullable=False)

    # Scope & deliverables
    project_scope: Mapped[str] = mapped_column(Text, nullable=True)
    deliverables: Mapped[list] = mapped_column(JSON, default=list)
    timeline_weeks: Mapped[int] = mapped_column(Integer, default=4)

    # Pricing
    price_amount: Mapped[float] = mapped_column(Float, nullable=False)
    price_currency: Mapped[str] = mapped_column(String(3), default="GBP")
    setup_fee: Mapped[float] = mapped_column(Float, default=0)
    monthly_fee: Mapped[float] = mapped_column(Float, default=0)

    # Payment
    payment_link: Mapped[str] = mapped_column(String(512), nullable=True)
    payment_terms: Mapped[str] = mapped_column(Text, nullable=True)

    # PDF
    pdf_url: Mapped[str] = mapped_column(String(512), nullable=True)

    # Tracking
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    organisation = relationship("Organisation")
    lead = relationship("Lead")
    creator = relationship("User")


# ─── Default proposal templates ─────────────────────────────────────────────

DEFAULT_SCOPE_TEMPLATE = """## Project Scope

Based on the Trust Snapshot and recommendations, this engagement will:

1. **Trust Signal Fixes** — Address critical gaps identified in the scan
2. **Content Optimisation** — Rewrite key pages for AI visibility
3. **Google Business Optimisation** — Complete profile improvements
4. **Schema Markup** — Implement JSON-LD structured data
5. **Monitoring Setup** — Monthly trust score tracking"""

DEFAULT_DELIVERABLES = [
    {"name": "Trust Gap Analysis", "description": "Detailed breakdown of all trust signal gaps", "hours": 4},
    {"name": "Website Content Updates", "description": "Rewrite of up to 5 key pages", "hours": 12},
    {"name": "Google Business Optimisation", "description": "Full profile optimisation", "hours": 3},
    {"name": "Schema Implementation", "description": "JSON-LD structured data", "hours": 6},
    {"name": "Trust Score Baseline", "description": "Initial measurement and tracking setup", "hours": 2},
]