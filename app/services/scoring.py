"""Trust Scoring Engine: deterministic scoring logic."""
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Lead
from app.models.trust_scan import TrustScan, TrustStandard
from app.models.scoring import (
    TrustScoreRecord, TrustGrade,
    PILLAR_MAPPING, GRADE_THRESHOLDS, IMPROVEMENT_SUGGESTIONS,
)
from app.schemas.scoring import PillarScore, ImprovementAction, TrustScoreResponse
from app.services import _log_audit


def calculate_grade(percentage: float) -> TrustGrade:
    """Determine trust grade from percentage score."""
    for threshold, grade, _ in GRADE_THRESHOLDS:
        if percentage >= threshold:
            return grade
    return TrustGrade.critical


def get_grade_description(grade: TrustGrade) -> str:
    for threshold, g, desc in GRADE_THRESHOLDS:
        if g == grade:
            return desc
    return ""


def calculate_pillar_scores(website_results: dict, google_results: dict) -> dict:
    """Calculate five pillar scores from scan results.

    Each pillar is computed by summing the scores of its mapped standards
    and capping at the pillar max.
    """
    pillar_scores = {}

    for pillar_key, pillar_config in PILLAR_MAPPING.items():
        total_score = 0
        pillar_max = pillar_config["max"]

        for category, standards in pillar_config["standards"].items():
            results = website_results if category == "website" else google_results
            if not results:
                continue
            for std_name in standards:
                std = results.get(std_name)
                if std:
                    total_score += std.get("score", 0)

        # Cap at pillar max
        total_score = min(total_score, pillar_max)
        pillar_scores[pillar_key] = total_score

    return pillar_scores


def generate_improvements(website_results: dict, google_results: dict) -> List[ImprovementAction]:
    """Generate improvement suggestions for failed standards."""
    improvements = []

    all_standards = {}

    if website_results:
        for std_name in ["https", "contact_page", "about_page", "cta",
                          "testimonials", "faq", "service_pages",
                          "privacy_policy", "mobile_responsive"]:
            std = website_results.get(std_name)
            if std:
                all_standards[std_name] = std

    if google_results:
        for std_name in ["rating", "reviews", "photos", "description", "categories"]:
            std = google_results.get(std_name)
            if std:
                all_standards[std_name] = std

    for std_name, std_data in all_standards.items():
        passed = std_data.get("passed", False)
        suggestion = IMPROVEMENT_SUGGESTIONS.get(std_name)
        if suggestion:
            improvements.append(ImprovementAction(
                standard=std_name,
                action=suggestion["action"],
                detail=suggestion["detail"],
                effort=suggestion["effort"],
                passed=passed,
            ))
        else:
            improvements.append(ImprovementAction(
                standard=std_name,
                action=f"Fix {std_name.replace('_', ' ')}",
                detail="Address this trust signal gap.",
                effort="medium",
                passed=passed,
            ))

    return improvements


def get_priority_actions(improvements: List[ImprovementAction]) -> List[ImprovementAction]:
    """Return top priority actions: failed items sorted by effort (low first)."""
    failed = [i for i in improvements if not i.passed]
    effort_order = {"low": 0, "medium": 1, "high": 2}
    failed.sort(key=lambda x: effort_order.get(x.effort, 99))
    return failed[:5]  # top 5


async def compute_trust_score(
    db: AsyncSession,
    scan_id: uuid.UUID,
    organisation_id: uuid.UUID,
    lead_id: uuid.UUID,
    user_id: uuid.UUID,
) -> TrustScoreRecord:
    """Compute a trust score from a completed scan.

    This is the deterministic scoring engine. Same inputs always produce
    the same score.
    """
    # Get scan
    result = await db.execute(
        select(TrustScan).where(TrustScan.id == scan_id, TrustScan.organisation_id == organisation_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise ValueError("Scan not found")
    if scan.status != "completed":
        raise ValueError("Scan must be completed before scoring")

    ws = scan.website_results or {}
    gs = scan.google_results or {}

    # Calculate overall
    overall_score = ws.get("overall_score", 0) + gs.get("overall_score", 0)
    overall_max = ws.get("overall_max", 0) + gs.get("overall_max", 0)
    if overall_max == 0:
        overall_max = 200  # default
    overall_percentage = round((overall_score / overall_max) * 100, 1)
    grade = calculate_grade(overall_percentage)

    # Pillar scores
    pillar_scores = calculate_pillar_scores(ws, gs)

    # Improvements
    improvements = generate_improvements(ws, gs)
    priority_actions = get_priority_actions(improvements)

    # Create record
    record = TrustScoreRecord(
        organisation_id=organisation_id,
        lead_id=lead_id,
        scan_id=scan_id,
        overall_score=overall_score,
        overall_max=overall_max,
        overall_percentage=overall_percentage,
        grade=grade,
        pillar_online_presence=pillar_scores.get("online_presence", 0),
        pillar_reputation=pillar_scores.get("reputation", 0),
        pillar_engagement=pillar_scores.get("engagement", 0),
        pillar_transparency=pillar_scores.get("transparency", 0),
        pillar_technical=pillar_scores.get("technical", 0),
        improvements=[i.dict() for i in improvements],
        priority_actions=[i.dict() for i in priority_actions],
    )
    db.add(record)
    await db.flush()

    # Update lead trust score
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if lead:
        lead.trust_score = int(overall_percentage)

    await _log_audit(db, user_id, organisation_id, "score.computed", "trust_score", str(record.id),
                     {"lead_id": str(lead_id), "score": overall_percentage, "grade": grade.value})

    return record


async def get_trust_score(db: AsyncSession, score_id: uuid.UUID, organisation_id: uuid.UUID) -> Optional[TrustScoreRecord]:
    result = await db.execute(
        select(TrustScoreRecord).where(
            TrustScoreRecord.id == score_id,
            TrustScoreRecord.organisation_id == organisation_id,
        )
    )
    return result.scalar_one_or_none()


async def get_trust_scores(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    lead_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[TrustScoreRecord], int]:
    query = select(TrustScoreRecord).where(TrustScoreRecord.organisation_id == organisation_id)
    count_query = select(func.count()).select_from(TrustScoreRecord).where(TrustScoreRecord.organisation_id == organisation_id)
    if lead_id:
        query = query.where(TrustScoreRecord.lead_id == lead_id)
        count_query = count_query.where(TrustScoreRecord.lead_id == lead_id)
    query = query.order_by(desc(TrustScoreRecord.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0


async def get_latest_trust_score(db: AsyncSession, lead_id: uuid.UUID, organisation_id: uuid.UUID) -> Optional[TrustScoreRecord]:
    result = await db.execute(
        select(TrustScoreRecord)
        .where(TrustScoreRecord.lead_id == lead_id, TrustScoreRecord.organisation_id == organisation_id)
        .order_by(desc(TrustScoreRecord.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


def build_score_response(record: TrustScoreRecord) -> TrustScoreResponse:
    """Convert a DB record into the full response with pillar breakdown."""
    pillars = [
        PillarScore(name="online_presence", label="Online Presence",
                     score=record.pillar_online_presence, max_score=record.pillar_online_presence_max,
                     percentage=round((record.pillar_online_presence / record.pillar_online_presence_max) * 100, 1) if record.pillar_online_presence_max > 0 else 0),
        PillarScore(name="reputation", label="Reputation",
                     score=record.pillar_reputation, max_score=record.pillar_reputation_max,
                     percentage=round((record.pillar_reputation / record.pillar_reputation_max) * 100, 1) if record.pillar_reputation_max > 0 else 0),
        PillarScore(name="engagement", label="Engagement",
                     score=record.pillar_engagement, max_score=record.pillar_engagement_max,
                     percentage=round((record.pillar_engagement / record.pillar_engagement_max) * 100, 1) if record.pillar_engagement_max > 0 else 0),
        PillarScore(name="transparency", label="Transparency",
                     score=record.pillar_transparency, max_score=record.pillar_transparency_max,
                     percentage=round((record.pillar_transparency / record.pillar_transparency_max) * 100, 1) if record.pillar_transparency_max > 0 else 0),
        PillarScore(name="technical", label="Technical Health",
                     score=record.pillar_technical, max_score=record.pillar_technical_max,
                     percentage=round((record.pillar_technical / record.pillar_technical_max) * 100, 1) if record.pillar_technical_max > 0 else 0),
    ]

    improvements = [ImprovementAction(**i) for i in (record.improvements or [])]
    priority_actions = [ImprovementAction(**i) for i in (record.priority_actions or [])]

    return TrustScoreResponse(
        id=record.id,
        organisation_id=record.organisation_id,
        lead_id=record.lead_id,
        scan_id=record.scan_id,
        overall_score=record.overall_score,
        overall_max=record.overall_max,
        overall_percentage=record.overall_percentage,
        grade=record.grade,
        pillar_online_presence=record.pillar_online_presence,
        pillar_reputation=record.pillar_reputation,
        pillar_engagement=record.pillar_engagement,
        pillar_transparency=record.pillar_transparency,
        pillar_technical=record.pillar_technical,
        pillars=pillars,
        improvements=improvements,
        priority_actions=priority_actions,
        created_at=record.created_at,
    )