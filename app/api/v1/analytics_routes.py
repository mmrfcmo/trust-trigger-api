"""Analytics Engine: API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, Lead
from app.models.analytics import AgencyMetrics
from app.models.monitoring import ScoreHistory
from app.models.proposals import Proposal, ProposalStatus

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics Engine"])


from pydantic import BaseModel
from typing import Optional


class DashboardResponse(BaseModel):
    total_revenue: float = 0
    monthly_recurring_revenue: float = 0
    average_deal_size: float = 0
    total_leads: int = 0
    active_projects: int = 0
    conversion_rate: float = 0
    average_trust_score: float = 0
    average_improvement: float = 0


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get agency dashboard metrics."""
    org_id = current_user.organisation_id

    # Total leads
    total_leads_result = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.organisation_id == org_id, Lead.is_active.is_(True))
    )
    total_leads = total_leads_result.scalar() or 0

    # Won leads (proposals)
    won_result = await db.execute(
        select(func.count()).select_from(Proposal).where(
            Proposal.organisation_id == org_id,
            Proposal.status == ProposalStatus.accepted,
        )
    )
    won = won_result.scalar() or 0

    conversion_rate = round((won / total_leads * 100), 1) if total_leads > 0 else 0

    # Active projects (proposals sent+)
    active_result = await db.execute(
        select(func.count()).select_from(Proposal).where(
            Proposal.organisation_id == org_id,
            Proposal.status.in_([ProposalStatus.sent, ProposalStatus.viewed, ProposalStatus.accepted]),
        )
    )
    active_projects = active_result.scalar() or 0

    # Average trust score from latest score per lead
    avg_score = 0
    try:
        avg_result = await db.execute(
            select(func.avg(ScoreHistory.overall_percentage))
            .where(ScoreHistory.organisation_id == org_id)
        )
        avg = avg_result.scalar()
        if avg:
            avg_score = round(float(avg), 1)
    except Exception:
        pass

    # Try to get from AgencyMetrics
    metrics_result = await db.execute(
        select(AgencyMetrics).where(AgencyMetrics.organisation_id == org_id)
    )
    metrics = metrics_result.scalar_one_or_none()

    return DashboardResponse(
        total_revenue=metrics.total_revenue if metrics else 0,
        monthly_recurring_revenue=metrics.monthly_recurring_revenue if metrics else 0,
        average_deal_size=metrics.average_deal_size if metrics else 0,
        total_leads=total_leads,
        active_projects=active_projects,
        conversion_rate=conversion_rate,
        average_trust_score=avg_score or (metrics.average_trust_score if metrics else 0),
        average_improvement=metrics.average_improvement if metrics else 0,
    )