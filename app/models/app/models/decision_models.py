"""
Decision Models — Pure Pydantic Data Models for the Trust Trigger Methodology.
This file contains ONLY Pydantic models. No calculations, no helpers, no HTML,
no API calls, no OpenAI, no database code. Every class uses the domain language
frozen in the Trust Trigger brand blueprint.

Hierarchy:
    DecisionModel
    ├── ExecutiveSummary
    ├── FrameworkAssessment
    ├── SignalAssessment[]
    ├── PriorityAction[]
    ├── Opportunity
    ├── Outcome
    └── AssessmentConfidence

Relationships:
    DecisionModel contains one ExecutiveSummary, one FrameworkAssessment,
    one AssessmentConfidence, zero-to-many SignalAssessments,
    zero-to-many PriorityActions, zero-to-many Opportunities, and
    zero-to-many Outcomes.

Versioning:
    methodology_version and report_version are included now so that
    historical reports can be regenerated or compared as the methodology
    evolves in future sprints.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

─── Enums ──────────────────────────────────────────────────────────────────
class FrameworkStage(str, Enum):
    """The stage of the Trust Trigger Transformation Method a lead is in."""

    trust_snapshot = "trust_snapshot"
    discovery = "discovery"
    proposal = "proposal"
    trust_transformation = "trust_transformation"
    validation = "validation"
    digital_trust_index = "digital_trust_index"
    certificate = "certificate"
    trust_monitor = "trust_monitor"
    referral = "referral"

class TrustGrade(str, Enum):
    """Six-grade trust classification matching the Digital Trust Index."""

    excellent = "excellent"      # 90-100
    strong = "strong"            # 75-89
    good = "good"                # 60-74
    fair = "fair"                # 40-59
    poor = "poor"                # 20-39
    critical = "critical"        # 0-19

class SignalCategory(str, Enum):
    """Source category for a trust signal found during scanning."""

    website = "website"
    google_business = "google_business"
    social_proof = "social_proof"
    review_platform = "review_platform"
    contact = "contact"

class EffortLevel(str, Enum):
    """Estimated effort to implement a recommendation."""

    low = "low"
    medium = "medium"
    high = "high"

class ConfidenceLevel(str, Enum):
    """Confidence in the assessment based on available evidence."""

    high = "high"
    medium = "medium"
    low = "low"
    insufficient_data = "insufficient_data"

─── Value Models ──────────────────────────────────────────────────────────
class PillarScore(BaseModel):
    """Score for one of the five Digital Trust Index pillars."""

    name: str = Field(..., description="Pillar identifier (e.g. online_presence)")
    label: str = Field(..., description="Human-readable label (e.g. 'Online Presence')")
    score: int = Field(..., ge=0, description="Points earned in this pillar")
    max_score: int = Field(..., gt=0, description="Maximum possible points for this pillar")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage score (score / max_score * 100)")

class SignalAssessment(BaseModel):
    """Assessment of a single trust signal against a standard."""

    standard_id: str = Field(..., description="Identifier from the Trust Standard Library")
    standard_name: str = Field(..., description="Human-readable standard name (e.g. 'HTTPS')")
    category: SignalCategory = Field(..., description="Source category of the signal")
    passed: bool = Field(..., description="Whether the signal meets the standard")
    score: int = Field(..., ge=0, description="Points awarded for this signal")
    max_score: int = Field(..., gt=0, description="Maximum points available for this standard")
    detail: str = Field(default="", description="Human-readable detail about what was found")
    evidence: str = Field(default="", description="Evidence snippet or reference supporting the assessment")
    methodology_ref: str = Field(default="", description="Reference to the specific methodology rule applied")

class PriorityAction(BaseModel):
    """A recommended action prioritised by effort and impact."""

    standard_id: str = Field(..., description="The standard this action relates to")
    action: str = Field(..., description="Short action title (e.g. 'Enable HTTPS')")
    detail: str = Field(default="", description="Detailed explanation of what to do and why")
    effort: EffortLevel = Field(default="medium", description="Estimated implementation effort")
    order: int = Field(default=0, ge=0, description="Priority order (1-based, lower is higher priority)")
    methodology_ref: str = Field(default="", description="Reference to the methodology rule driving this action")

class Opportunity(BaseModel):
    """A commercial opportunity identified during assessment."""

    title: str = Field(..., description="Short opportunity title")
    description: str = Field(default="", description="What the opportunity entails")
    potential_value: str = Field(default="", description="Estimated value (e.g. '3-5 more enquiries per week')")
    recommended_product: str = Field(default="", description="Product that addresses this (e.g. 'Trust Transformation')")

class Outcome(BaseModel):
    """A measurable outcome projected or achieved from a transformation."""

    metric: str = Field(..., description="What is being measured (e.g. 'Trust Score')")
    from_value: str = Field(default="", description="Starting value before transformation")
    to_value: str = Field(default="", description="Target or achieved value after transformation")
    evidence_url: str = Field(default="", description="Link to evidence supporting this outcome")

─── Composite Models ──────────────────────────────────────────────────────
class ExecutiveSummary(BaseModel):
    """Concise executive summary of the trust assessment."""

    overall_score: int = Field(..., ge=0, le=100, description="Digital Trust Index overall score (0-100)")
    framework_stage: FrameworkStage = Field(..., description="Current stage in the Transformation Method")
    grade: TrustGrade = Field(..., description="Trust grade classification")
    confidence: ConfidenceLevel = Field(..., description="Confidence in this assessment")
    summary: str = Field(default="", max_length=2000, description="One-paragraph executive summary of findings")
    top_priorities: list[str] = Field(default_factory=list, max_length=5, description="Top 3-5 priority action titles")

class FrameworkAssessment(BaseModel):
    """Assessment against the Trust Framework."""

    pillars: list[PillarScore] = Field(default_factory=list, description="Scores for all five pillars")
    total_score: int = Field(..., ge=0, description="Sum of all pillar scores")
    total_max: int = Field(..., gt=0, description="Sum of all pillar max scores")
    signals_checked: int = Field(default=0, ge=0, description="Number of standards checked")
    signals_passed: int = Field(default=0, ge=0, description="Number of standards passed")

class AssessmentConfidence(BaseModel):
    """Confidence assessment for the overall evaluation."""

    level: ConfidenceLevel = Field(..., description="Overall confidence level")
    signals_analysed: int = Field(..., ge=0, description="How many signals were analysed")
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Fraction of expected data that was available")
    limiting_factors: list[str] = Field(default_factory=list, description="What limited the confidence (e.g. 'website unreachable')")

─── Root Model ────────────────────────────────────────────────────────────
class DecisionModel(BaseModel):
    """
    Root model for a complete Trust Trigger decision.

    This is the single source of truth for what a Trust Snapshot or
    Trust Transformation assessment produces. Every downstream component
    (analysis_engine, recommendation_engine, report_builder, fulfilment_pipeline)
    should build against this interface.
    """

    # Identity
    lead_id: str = Field(..., description="Lead or client identifier")
    organisation_id: str = Field(..., description="Organisation this belongs to")
    assessment_id: str = Field(default="", description="Unique assessment identifier (auto-generated if empty)")

    # Versioning — critical for methodology evolution over time
    methodology_version: str = Field(default="1.0", description="Version of the Trust Trigger Transformation Method used")
    report_version: str = Field(default="1.0", description="Version of the report format")

    # Core components
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary of findings")
    framework_assessment: FrameworkAssessment = Field(..., description="Full framework assessment with pillar scores")
    signals: list[SignalAssessment] = Field(default_factory=list, description="Individual signal assessments")
    priority_actions: list[PriorityAction] = Field(default_factory=list, description="Prioritised recommendations")
    opportunities: list[Opportunity] = Field(default_factory=list, description="Commercial opportunities identified")
    outcomes: list[Outcome] = Field(default_factory=list, description="Projected or achieved outcomes")
    confidence: AssessmentConfidence = Field(..., description="Confidence in this assessment")

    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow, description="When the assessment was performed")
    assessed_by: str = Field(default="system", description="Who or what performed the assessment")
