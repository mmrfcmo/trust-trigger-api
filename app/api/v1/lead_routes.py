"""Lead Intelligence Engine: API routes."""
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, UserRole, LeadStatus
from app.schemas import (
    LeadCreate, LeadUpdate, LeadResponse, LeadList,
    GooglePlacesSearchRequest, GooglePlacesSearchResponse,
    SearchHistoryResponse, SearchHistoryList,
    BulkStatusUpdate, BulkAssign,
)
from app.services.lead_intelligence import (
    search_google_places,
    create_lead_from_search,
    create_lead_manual,
    get_lead,
    get_leads,
    update_lead,
    delete_lead,
    bulk_update_status,
    bulk_assign,
    save_search_history,
    get_search_history,
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/leads", tags=["Lead Intelligence Engine"])


# ─── Search ─────────────────────────────────────────────────────────────────

@router.post("/search", response_model=GooglePlacesSearchResponse)
async def search_businesses(
    req: GooglePlacesSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for businesses via Google Places."""
    result = await search_google_places(
        query=req.query,
        location=req.location,
        radius_km=req.radius_km,
        api_key=settings.google_places_api_key,
    )
    # Save search history
    await save_search_history(
        db, current_user.id, current_user.organisation_id,
        req.query, req.location, req.radius_km, result.total,
    )
    return result


@router.get("/search-history", response_model=SearchHistoryList)
async def list_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List recent search history."""
    history = await get_search_history(db, current_user.organisation_id)
    return SearchHistoryList(
        items=[SearchHistoryResponse.model_validate(h) for h in history],
        total=len(history),
    )


# ─── Import from Search ─────────────────────────────────────────────────────

@router.post("/import-from-search", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def import_from_search(
    place_id: str = Query(..., description="Google Place ID to import"),
    query: str = Query(...),
    location: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import a business from search results into leads."""
    # Re-run search to get the specific result
    search_result = await search_google_places(query, location)
    match = None
    for r in search_result.results:
        if r.place_id == place_id:
            match = r
            break
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found in search results")

    # Check for duplicate
    existing = await db.execute(
        __import__("sqlalchemy").select(__import__("app.models", fromlist=["Lead"]).Lead)
        .where(__import__("app.models", fromlist=["Lead"]).Lead.google_place_id == place_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead already exists from this place")

    lead = await create_lead_from_search(db, match, current_user.organisation_id, current_user.id)
    return LeadResponse.model_validate(lead)


# ─── Lead CRUD ──────────────────────────────────────────────────────────────

@router.get("", response_model=LeadList)
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[LeadStatus] = Query(None),
    search: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    sort_by: str = Query("created_at"),
    sort_desc: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List leads with filtering and search."""
    leads, total = await get_leads(
        db, current_user.organisation_id, skip, limit,
        status, search, min_score, sort_by, sort_desc,
    )
    return LeadList(
        items=[LeadResponse.model_validate(l) for l in leads],
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a lead manually."""
    lead = await create_lead_manual(db, data, current_user.organisation_id, current_user.id)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead_by_id(
    lead_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single lead by ID."""
    lead = await get_lead(db, lead_id, current_user.organisation_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead_by_id(
    lead_id: uuid.UUID,
    data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a lead."""
    lead = await update_lead(db, lead_id, data, current_user.organisation_id, current_user.id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_lead(
    lead_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Archive a lead."""
    success = await delete_lead(db, lead_id, current_user.organisation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")


# ─── Bulk Operations ────────────────────────────────────────────────────────

@router.post("/bulk/status", status_code=status.HTTP_200_OK)
async def bulk_update_leads_status(
    data: BulkStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update status for multiple leads."""
    count = await bulk_update_status(db, data.lead_ids, data.status, current_user.organisation_id, current_user.id)
    return {"updated": count}


@router.post("/bulk/assign", status_code=status.HTTP_200_OK)
async def bulk_assign_leads(
    data: BulkAssign,
    current_user: User = Depends(require_role([UserRole.admin, UserRole.manager])),
    db: AsyncSession = Depends(get_db),
):
    """Assign multiple leads to a user."""
    count = await bulk_assign(db, data.lead_ids, data.assigned_to, current_user.organisation_id, current_user.id)
    return {"updated": count}


# Import for the bulk routes
from app.core.deps import require_role