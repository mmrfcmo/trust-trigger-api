"""AI Recommendation Engine: generates content using OpenAI."""
import uuid
import json
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from app.models import Lead
from app.models.trust_scan import TrustScan
from app.models.scoring import TrustScoreRecord
from app.models.recommendations import AIRecommendation, RecommendationType
from app.schemas.recommendations import RecommendationResponse
from app.core.config import settings
from app.services import _log_audit


# ─── Prompt Templates ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert AI visibility consultant. You help local businesses 
improve their trust signals so they appear in AI search results (ChatGPT, Google AI, Perplexity, etc.).
You write in clear, professional British English. Be specific, actionable, and data-driven."""


def _build_context(lead: Lead, score: Optional[TrustScoreRecord] = None, scan: Optional[TrustScan] = None) -> str:
    """Build context string from lead data, score, and scan results."""
    parts = [f"Business: {lead.business_name}"]
    if lead.website:
        parts.append(f"Website: {lead.website}")
    if lead.city:
        parts.append(f"Location: {lead.city}")
    if lead.google_rating:
        parts.append(f"Google Rating: {lead.google_rating} ({lead.google_reviews_count} reviews)")

    if score:
        parts.append(f"\nTrust Score: {score.overall_percentage}% (Grade: {score.grade.value})")
        parts.append(f"Pillars - Online Presence: {score.pillar_online_presence}/{score.pillar_online_presence_max}, "
                     f"Reputation: {score.pillar_reputation}/{score.pillar_reputation_max}, "
                     f"Engagement: {score.pillar_engagement}/{score.pillar_engagement_max}, "
                     f"Transparency: {score.pillar_transparency}/{score.pillar_transparency_max}, "
                     f"Technical: {score.pillar_technical}/{score.pillar_technical_max}")
        if score.priority_actions:
            parts.append("Priority Improvements:")
            for action in score.priority_actions[:3]:
                parts.append(f"- {action.get('action', '')}: {action.get('detail', '')}")

    if scan:
        ws = scan.website_results or {}
        gs = scan.google_results or {}
        if ws:
            parts.append(f"\nWebsite Scan: {ws.get('passed_count', 0)}/{ws.get('total_count', 9)} standards passed")
        if gs:
            parts.append(f"Google Business Scan: {gs.get('passed_count', 0)}/{gs.get('total_count', 5)} standards passed")

    return "\n".join(parts)


PROMPT_TEMPLATES = {
    RecommendationType.trust_snapshot: """Create a one-page Trust Snapshot for this business.
Format as a professional report section with:
- Executive Summary (2-3 sentences)
- Current Trust Score and Grade
- Key Strengths (top 3)
- Key Gaps (top 3)
- Recommended Next Step

Use markdown formatting. Be concise and actionable.""",

    RecommendationType.transformation_report: """Create a detailed Trust Transformation Report.
Include:
1. Executive Summary
2. Current State Assessment
3. Trust Score Breakdown by Pillar
4. Recommended Improvements (prioritised)
5. Implementation Timeline (4-week plan)
6. Expected Impact

Use markdown with headings and bullet points. Be thorough and specific.""",

    RecommendationType.homepage_rewrite: """Rewrite the homepage content for this business.
The homepage should:
- Clearly state what the business does in the first sentence
- Build trust immediately
- Include a clear call-to-action
- Be AI-friendly (clear structure, semantic HTML guidance)
- Be under 300 words

Output the rewritten homepage copy in markdown.""",

    RecommendationType.about_page: """Write an About Us page for this business.
Include:
- Company story and mission
- Team/credentials highlight
- Trust-building elements
- Call-to-action
Under 400 words. Output in markdown.""",

    RecommendationType.service_pages: """Write service page content for this business.
For each service:
- Clear service name and description
- Benefits to customer
- Trust indicators
- Call-to-action
Output in markdown with service sections.""",

    RecommendationType.faq: """Generate 5-7 frequently asked questions and answers for this business.
Questions should address common customer concerns about trust, reliability, and service quality.
Output in markdown Q&A format.""",

    RecommendationType.meta_titles: """Generate 5 meta title options for this business.
Each title should:
- Be under 60 characters
- Include primary keyword
- Include location if relevant
- Be clickable and trust-building
Output as a numbered list.""",

    RecommendationType.meta_descriptions: """Generate 5 meta description options for this business.
Each description should:
- Be under 160 characters
- Include primary keyword
- Include a call-to-action
- Build trust
Output as a numbered list.""",

    RecommendationType.google_business_improvements: """Suggest 5 specific improvements for this business's Google Business Profile.
Focus on:
- Profile completeness
- Review generation strategy
- Photo and post recommendations
- Category and attribute optimisation
- Q&A management
Output as numbered actions with rationale.""",

    RecommendationType.review_request_email: """Write a professional email template asking customers to leave a Google Review.
The email should:
- Be polite and appreciative
- Include a direct link to Google review page
- Be under 200 words
- Include subject line
Output the full email template.""",

    RecommendationType.improvement_recommendations: """Based on the trust score data, provide detailed improvement recommendations.
For each recommendation include:
1. What to fix
2. Why it matters for AI visibility
3. How to implement it (step-by-step)
4. Expected impact on trust score

Output as a structured action plan with 5-7 recommendations.""",
}


# ─── AI Generation ──────────────────────────────────────────────────────────

async def generate_recommendation(
    db: AsyncSession,
    lead_id: uuid.UUID,
    recommendation_type: RecommendationType,
    organisation_id: uuid.UUID,
    user_id: uuid.UUID,
    custom_instructions: Optional[str] = None,
) -> AIRecommendation:
    """Generate an AI recommendation for a lead."""
    # Get lead
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.organisation_id == organisation_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise ValueError("Lead not found")

    # Get latest score and scan
    score_result = await db.execute(
        select(TrustScoreRecord)
        .where(TrustScoreRecord.lead_id == lead_id)
        .order_by(desc(TrustScoreRecord.created_at))
        .limit(1)
    )
    score = score_result.scalar_one_or_none()

    scan_result = await db.execute(
        select(TrustScan)
        .where(TrustScan.lead_id == lead_id)
        .order_by(desc(TrustScan.created_at))
        .limit(1)
    )
    scan = scan_result.scalar_one_or_none()

    # Build prompt
    context = _build_context(lead, score, scan)
    prompt = PROMPT_TEMPLATES.get(recommendation_type, "")
    if custom_instructions:
        prompt += f"\n\nAdditional instructions: {custom_instructions}"

    full_prompt = f"""Context:
{context}

Task:
{prompt}

Generate the recommendation now."""

    # Call OpenAI
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    content = response.choices[0].message.content or ""
    model_used = response.model
    tokens_used = response.usage.total_tokens if response.usage else 0

    # Determine title
    title_map = {
        RecommendationType.trust_snapshot: f"Trust Snapshot — {lead.business_name}",
        RecommendationType.transformation_report: f"Trust Transformation Report — {lead.business_name}",
        RecommendationType.homepage_rewrite: f"Homepage Rewrite — {lead.business_name}",
        RecommendationType.about_page: f"About Page — {lead.business_name}",
        RecommendationType.service_pages: f"Service Pages — {lead.business_name}",
        RecommendationType.faq: f"FAQs — {lead.business_name}",
        RecommendationType.meta_titles: f"Meta Titles — {lead.business_name}",
        RecommendationType.meta_descriptions: f"Meta Descriptions — {lead.business_name}",
        RecommendationType.google_business_improvements: f"Google Business Improvements — {lead.business_name}",
        RecommendationType.review_request_email: f"Review Request Email — {lead.business_name}",
        RecommendationType.improvement_recommendations: f"Improvement Recommendations — {lead.business_name}",
    }

    recommendation = AIRecommendation(
        organisation_id=organisation_id,
        lead_id=lead_id,
        score_id=score.id if score else None,
        recommendation_type=recommendation_type,
        title=title_map.get(recommendation_type, f"Recommendation — {lead.business_name}"),
        content=content,
        model_used=model_used,
        tokens_used=tokens_used,
    )
    db.add(recommendation)
    await db.flush()

    await _log_audit(db, user_id, organisation_id, "recommendation.generate", "ai_recommendation",
                     str(recommendation.id), {
                         "lead_id": str(lead_id),
                         "type": recommendation_type.value,
                         "tokens": tokens_used,
                     })

    return recommendation


async def get_recommendation(db: AsyncSession, rec_id: uuid.UUID, organisation_id: uuid.UUID) -> Optional[AIRecommendation]:
    result = await db.execute(
        select(AIRecommendation).where(
            AIRecommendation.id == rec_id,
            AIRecommendation.organisation_id == organisation_id,
        )
    )
    return result.scalar_one_or_none()


async def get_recommendations(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    lead_id: Optional[uuid.UUID] = None,
    rec_type: Optional[RecommendationType] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[AIRecommendation], int]:
    query = select(AIRecommendation).where(AIRecommendation.organisation_id == organisation_id)
    count_query = select(func.count()).select_from(AIRecommendation).where(AIRecommendation.organisation_id == organisation_id)
    if lead_id:
        query = query.where(AIRecommendation.lead_id == lead_id)
        count_query = count_query.where(AIRecommendation.lead_id == lead_id)
    if rec_type:
        query = query.where(AIRecommendation.recommendation_type == rec_type)
        count_query = count_query.where(AIRecommendation.recommendation_type == rec_type)
    query = query.order_by(desc(AIRecommendation.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0