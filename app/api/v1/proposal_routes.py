"""Proposal Engine: API routes."""
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.models.proposals import Proposal, ProposalStatus, DEFAULT_SCOPE_TEMPLATE, DEFAULT_DELIVERABLES
from app.services import _log_audit

router = APIRouter(prefix="/api/v1/proposals", tags=["Proposal Engine"])


from pydantic import BaseModel, Field
from uuid import UUID


class ProposalCreate(BaseModel):
    lead_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    project_scope: Optional[str] = None
    deliverables: Optional[List[dict]] = None
    timeline_weeks: int = 4
    price_amount: float = Field(..., gt=0)
    setup_fee: float = 0
    monthly_fee: float = 0
    payment_terms: Optional[str] = None


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    project_scope: Optional[str] = None
    deliverables: Optional[List[dict]] = None
    timeline_weeks: Optional[int] = None
    price_amount: Optional[float] = None
    setup_fee: Optional[float] = None
    monthly_fee: Optional[float] = None
    payment_terms: Optional[str] = None
    status: Optional[ProposalStatus] = None
    payment_link: Optional[str] = None


class ProposalResponse(BaseModel):
    id: UUID
    organisation_id: UUID
    lead_id: UUID
    created_by: UUID
    title: str
    status: ProposalStatus
    project_scope: Optional[str]
    deliverables: List
    timeline_weeks: int
    price_amount: float
    price_currency: str
    setup_fee: float
    monthly_fee: float
    payment_link: Optional[str]
    payment_terms: Optional[str]
    pdf_url: Optional[str]
    sent_at: Optional[datetime]
    viewed_at: Optional[datetime]
    accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProposalList(BaseModel):
    items: List[ProposalResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    data: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a proposal for a lead."""
    proposal = Proposal(
        organisation_id=current_user.organisation_id,
        lead_id=data.lead_id,
        created_by=current_user.id,
        title=data.title,
        project_scope=data.project_scope or DEFAULT_SCOPE_TEMPLATE,
        deliverables=data.deliverables or DEFAULT_DELIVERABLES,
        timeline_weeks=data.timeline_weeks,
        price_amount=data.price_amount,
        setup_fee=data.setup_fee,
        monthly_fee=data.monthly_fee,
        payment_terms=data.payment_terms,
    )
    db.add(proposal)
    await db.flush()
    await _log_audit(db, current_user.id, current_user.organisation_id, "proposal.create", "proposal", str(proposal.id),
                     {"lead_id": str(data.lead_id), "amount": data.price_amount})
    return ProposalResponse.model_validate(proposal)


@router.get("", response_model=ProposalList)
async def list_proposals(
    lead_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[ProposalStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Proposal).where(Proposal.organisation_id == current_user.organisation_id)
    count_query = select(func.count()).select_from(Proposal).where(Proposal.organisation_id == current_user.organisation_id)
    if lead_id:
        query = query.where(Proposal.lead_id == lead_id)
        count_query = count_query.where(Proposal.lead_id == lead_id)
    if status_filter:
        query = query.where(Proposal.status == status_filter)
        count_query = count_query.where(Proposal.status == status_filter)
    query = query.order_by(desc(Proposal.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return ProposalList(
        items=[ProposalResponse.model_validate(p) for p in result.scalars().all()],
        total=total or 0,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.organisation_id == current_user.organisation_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return ProposalResponse.model_validate(proposal)


@router.patch("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: uuid.UUID,
    data: ProposalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.organisation_id == current_user.organisation_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(proposal, key, value)
    await db.flush()
    await _log_audit(db, current_user.id, current_user.organisation_id, "proposal.update", "proposal", str(proposal.id), update_data)
    return ProposalResponse.model_validate(proposal)


@router.post("/{proposal_id}/send", response_model=ProposalResponse)
async def send_proposal(
    proposal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id, Proposal.organisation_id == current_user.organisation_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    proposal.status = ProposalStatus.sent
    proposal.sent_at = datetime.now(timezone.utc)
    await db.flush()
    await _log_audit(db, current_user.id, current_user.organisation_id, "proposal.send", "proposal", str(proposal.id), {})
    return ProposalResponse.model_validate(proposal)