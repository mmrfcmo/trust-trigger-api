"""Trust Scoring Engine: models, scoring logic, and schemas."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class TrustGrade(str, enum.Enum):
    excellent = "excellent"      # 90-100
    strong = "strong"            # 75-89
    good = "good"                # 60-74
    fair = "fair"                # 40-59
    poor = "poor"                # 20-39
    critical = "critical"        # 0-19


class TrustScoreRecord(Base):
    """Stores computed trust scores for a lead at a point in time."""
    __tablename__ = "trust_score_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[str] = mapped_column(String(36), ForeignKey("organisations.id"), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False, index=True)
    scan_id: Mapped[str] = mapped_column(String(36), ForeignKey("trust_scans.id"), nullable=True)

    # Overall
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_max: Mapped[int] = mapped_column(Integer, default=200)
    overall_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[TrustGrade] = mapped_column(SAEnum(TrustGrade), nullable=False)

    # Five Pillar Scores (each 0-100)
    pillar_online_presence: Mapped[int] = mapped_column(Integer, default=0)
    pillar_reputation: Mapped[int] = mapped_column(Integer, default=0)
    pillar_engagement: Mapped[int] = mapped_column(Integer, default=0)
    pillar_transparency: Mapped[int] = mapped_column(Integer, default=0)
    pillar_technical: Mapped[int] = mapped_column(Integer, default=0)

    # Pillar maxes
    pillar_online_presence_max: Mapped[int] = mapped_column(Integer, default=25)
    pillar_reputation_max: Mapped[int] = mapped_column(Integer, default=30)
    pillar_engagement_max: Mapped[int] = mapped_column(Integer, default=20)
    pillar_transparency_max: Mapped[int] = mapped_column(Integer, default=15)
    pillar_technical_max: Mapped[int] = mapped_column(Integer, default=10)

    # Improvement
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    priority_actions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    organisation = relationship("Organisation")
    lead = relationship("Lead")
    scan = relationship("TrustScan")


# ─── Scoring Configuration ──────────────────────────────────────────────────

# Pillar mapping: which standards map to which pillar
PILLAR_MAPPING = {
    "online_presence": {
        "label": "Online Presence",
        "max": 25,
        "standards": {
            "website": ["https"],  # has a website at all + HTTPS
            "google_business": ["categories", "description"],
        },
        "weight": 1.0,
    },
    "reputation": {
        "label": "Reputation",
        "max": 30,
        "standards": {
            "website": ["testimonials"],
            "google_business": ["rating", "reviews"],
        },
        "weight": 1.0,
    },
    "engagement": {
        "label": "Engagement",
        "max": 20,
        "standards": {
            "website": ["cta", "contact_page", "service_pages"],
            "google_business": ["photos"],
        },
        "weight": 1.0,
    },
    "transparency": {
        "label": "Transparency",
        "max": 15,
        "standards": {
            "website": ["about_page", "faq", "privacy_policy"],
            "google_business": [],
        },
        "weight": 1.0,
    },
    "technical": {
        "label": "Technical Health",
        "max": 10,
        "standards": {
            "website": ["mobile_responsive"],
            "google_business": [],
        },
        "weight": 1.0,
    },
}

# Grade thresholds
GRADE_THRESHOLDS = [
    (90, TrustGrade.excellent, "Outstanding trust signals across all areas"),
    (75, TrustGrade.strong, "Strong trust foundation with minor gaps"),
    (60, TrustGrade.good, "Good trust signals, room for improvement"),
    (40, TrustGrade.fair, "Several trust gaps that need attention"),
    (20, TrustGrade.poor, "Significant trust weaknesses"),
    (0, TrustGrade.critical, "Critical trust issues requiring immediate action"),
]

# Improvement suggestions keyed by standard
IMPROVEMENT_SUGGESTIONS = {
    "https": {
        "action": "Enable HTTPS",
        "detail": "Install an SSL certificate to secure your website. Visitors and AI trust HTTPS sites more.",
        "effort": "medium",
    },
    "contact_page": {
        "action": "Add a Contact Page",
        "detail": "Create a dedicated contact page with phone, email, address, and a contact form.",
        "effort": "low",
    },
    "about_page": {
        "action": "Add an About Page",
        "detail": "Tell your story, introduce your team, and explain what makes your business unique.",
        "effort": "low",
    },
    "cta": {
        "action": "Add Clear Calls-to-Action",
        "detail": "Include visible CTAs like 'Book Now', 'Get a Quote', or 'Contact Us' on key pages.",
        "effort": "low",
    },
    "testimonials": {
        "action": "Collect and Display Reviews",
        "detail": "Add a testimonials section and link to your Google Reviews or Trustpilot profile.",
        "effort": "medium",
    },
    "faq": {
        "action": "Add an FAQ Section",
        "detail": "Answer common customer questions to build trust and improve AI understanding.",
        "effort": "low",
    },
    "service_pages": {
        "action": "Detail Your Services",
        "detail": "Create dedicated pages for each service or product you offer.",
        "effort": "medium",
    },
    "privacy_policy": {
        "action": "Add a Privacy Policy",
        "detail": "Include a privacy policy page covering data handling and GDPR compliance.",
        "effort": "low",
    },
    "mobile_responsive": {
        "action": "Make Site Mobile-Responsive",
        "detail": "Ensure your website works well on mobile devices with a responsive design.",
        "effort": "medium",
    },
    "rating": {
        "action": "Improve Google Rating",
        "detail": "Encourage satisfied customers to leave positive Google reviews to boost your rating above 4.0.",
        "effort": "medium",
    },
    "reviews": {
        "action": "Increase Review Volume",
        "detail": "Ask customers to leave reviews on Google. More reviews build credibility with AI and users.",
        "effort": "low",
    },
    "photos": {
        "action": "Add Photos to Google Profile",
        "detail": "Upload photos of your business, team, and work to your Google Business profile.",
        "effort": "low",
    },
    "description": {
        "action": "Complete Business Description",
        "detail": "Write a detailed, keyword-rich description of your business on Google.",
        "effort": "low",
    },
    "categories": {
        "action": "Set Business Categories",
        "detail": "Select relevant categories on your Google Business profile so AI can classify you correctly.",
        "effort": "low",
    },
}