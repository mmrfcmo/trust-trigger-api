"""Lead Intelligence Engine: search, scoring, CRM services."""
import uuid
import math
from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Lead, SearchHistory, LeadStatus, LeadSource
from app.schemas import (
    LeadCreate, LeadUpdate,
    GooglePlacesResult, GooglePlacesSearchResponse,
)
from app.services import _log_audit


# ─── Opportunity Scoring ────────────────────────────────────────────────────

def calculate_opportunity_score(lead_data: dict) -> Tuple[int, str]:
    """Calculate opportunity score (0-100) based on trust signals.

    Scoring is deterministic and configurable:
    - Website presence: 20 points
    - Google rating ≥ 4.0: 20 points
    - Has reviews (≥10): 15 points
    - Has phone: 10 points
    - Has email: 10 points
    - Has photos: 10 points
    - Has categories: 5 points
    - Has address: 10 points
    """
    score = 0
    reasons = []

    if lead_data.get("website"):
        score += 20
        reasons.append("Website found")

    rating = lead_data.get("google_rating")
    if rating and rating >= 4.0:
        score += 20
        reasons.append(f"Strong rating ({rating})")
    elif rating and rating >= 3.0:
        score += 10
        reasons.append(f"Moderate rating ({rating})")

    reviews = lead_data.get("google_reviews_count") or 0
    if reviews >= 50:
        score += 15
        reasons.append(f"{reviews}+ reviews")
    elif reviews >= 10:
        score += 10
        reasons.append(f"{reviews} reviews")

    if lead_data.get("phone"):
        score += 10
        reasons.append("Phone listed")

    if lead_data.get("email"):
        score += 10
        reasons.append("Email listed")

    photos = lead_data.get("google_photos_count") or 0
    if photos >= 10:
        score += 10
        reasons.append(f"{photos} photos")
    elif photos > 0:
        score += 5

    categories = lead_data.get("google_categories") or []
    if len(categories) > 0:
        score += 5
        reasons.append("Categories found")

    if lead_data.get("address") or lead_data.get("city"):
        score += 10
        reasons.append("Address verified")

    # Cap at 100
    score = min(score, 100)
    reason_str = "; ".join(reasons) if reasons else "Insufficient data"

    return score, reason_str


# ─── Google Places Search (Mock for development) ────────────────────────────

async def search_google_places(
    query: str,
    location: Optional[str] = None,
    radius_km: int = 10,
    api_key: Optional[str] = None,
) -> GooglePlacesSearchResponse:
    """Search Google Places for businesses.

    In production, this calls the Google Places API.
    For development, returns mock data demonstrating the structure.
    """
    # TODO: Replace with actual Google Places API call
    # Places API: https://maps.googleapis.com/maps/api/place/textsearch/json
    # Nearby Search: https://maps.googleapis.com/maps/api/place/nearbysearch/json

    # Placeholder — returns structure for 3 mock results
    mock_results = [
        GooglePlacesResult(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            business_name=f"{query} - Central Branch",
            address=f"123 High Street, {location or 'London'}",
            rating=4.5,
            reviews_count=127,
            phone="+442071234567",
            website=f"https://www.{query.lower().replace(' ', '')}.co.uk",
            categories=["Business Services", "Consulting"],
            latitude=51.5074,
            longitude=-0.1278,
            photos_count=23,
        ),
        GooglePlacesResult(
            place_id="ChIJLfySpTDuEmsRq_ayqFjnqQg",
            business_name=f"{query} - Riverside",
            address=f"456 River Lane, {location or 'London'}",
            rating=4.2,
            reviews_count=89,
            phone="+442075678901",
            website=None,
            categories=["Small Business", "Retail"],
            latitude=51.5154,
            longitude=-0.1419,
            photos_count=12,
        ),
        GooglePlacesResult(
            place_id="ChIJQcRkyDDuEmsRjSJx0FJKh3I",
            business_name=f"{query} - Westside Ltd",
            address=f"789 Park Avenue, {location or 'London'}",
            rating=3.8,
            reviews_count=34,
            phone="+442079876543",
            website=None,
            categories=["Local Services"],
            latitude=51.5014,
            longitude=-0.1419,
            photos_count=5,
        ),
    ]

    return GooglePlacesSearchResponse(
        results=mock_results,
        total=len(mock_results),
        query=query,
        location=location,
    )


# ─── Lead CRUD ──────────────────────────────────────────────────────────────

async def create_lead_from_search(
    db: AsyncSession,
    result: GooglePlacesResult,
    organisation_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> Lead:
    """Create a lead from a Google Places search result."""
    lead_data = {
        "business_name": result.business_name,
        "website": result.website,
        "phone": result.phone,
        "address": result.address,
        "latitude": result.latitude,
        "longitude": result.longitude,
        "google_place_id": result.place_id,
        "google_rating": result.rating,
        "google_reviews_count": result.reviews_count,
        "google_categories": result.categories,
        "google_photos_count": result.photos_count,
        "source": LeadSource.google_places,
    }

    score, reason = calculate_opportunity_score(lead_data)

    lead = Lead(
        organisation_id=organisation_id,
        **lead_data,
        opportunity_score=score,
        opportunity_reason=reason,
    )
    db.add(lead)
    await db.flush()

    await _log_audit(db, actor_id, organisation_id, "lead.create", "lead", str(lead.id),
                     {"business_name": result.business_name, "score": score})
    return lead


async def create_lead_manual(db: AsyncSession, data: LeadCreate, organisation_id: uuid.UUID, actor_id: uuid.UUID) -> Lead:
    """Create a lead manually."""
    score, reason = calculate_opportunity_score(data.model_dump())
    lead = Lead(
        organisation_id=organisation_id,
        **data.model_dump(exclude={"source"}),
        source=data.source or LeadSource.manual,
        opportunity_score=score,
        opportunity_reason=reason,
    )
    db.add(lead)
    await db.flush()
    await _log_audit(db, actor_id, organisation_id, "lead.create", "lead", str(lead.id),
                     {"business_name": data.business_name})
    return lead


async def get_lead(db: AsyncSession, lead_id: uuid.UUID, organisation_id: uuid.UUID) -> Optional[Lead]:
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.organisation_id == organisation_id)
    )
    return result.scalar_one_or_none()


async def get_leads(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    status: Optional[LeadStatus] = None,
    search: Optional[str] = None,
    min_score: Optional[int] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> Tuple[List[Lead], int]:
    """List leads with filtering, search, and sorting."""
    query = select(Lead).where(Lead.organisation_id == organisation_id)
    count_query = select(func.count()).select_from(Lead).where(Lead.organisation_id == organisation_id)

    if status:
        query = query.where(Lead.status == status)
        count_query = count_query.where(Lead.status == status)

    if search:
        search_filter = or_(
            Lead.business_name.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%"),
            Lead.phone.ilike(f"%{search}%"),
            Lead.city.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if min_score is not None:
        query = query.where(Lead.opportunity_score >= min_score)
        count_query = count_query.where(Lead.opportunity_score >= min_score)

    # Sorting
    sort_col = getattr(Lead, sort_by, Lead.created_at)
    if sort_desc:
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)

    return list(result.scalars().all()), total or 0


async def update_lead(db: AsyncSession, lead_id: uuid.UUID, data: LeadUpdate, organisation_id: uuid.UUID, actor_id: uuid.UUID) -> Optional[Lead]:
    lead = await get_lead(db, lead_id, organisation_id)
    if not lead:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)
    await db.flush()
    await _log_audit(db, actor_id, organisation_id, "lead.update", "lead", str(lead.id), update_data)
    return lead


async def delete_lead(db: AsyncSession, lead_id: uuid.UUID, organisation_id: uuid.UUID, actor_id: uuid.UUID) -> bool:
    lead = await get_lead(db, lead_id, organisation_id)
    if not lead:
        return False
    lead.status = LeadStatus.archived
    await db.flush()
    await _log_audit(db, actor_id, organisation_id, "lead.archive", "lead", str(lead.id), {})
    return True


async def bulk_update_status(
    db: AsyncSession,
    lead_ids: List[uuid.UUID],
    status: LeadStatus,
    organisation_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> int:
    """Update status for multiple leads. Returns count updated."""
    count = 0
    for lid in lead_ids:
        lead = await get_lead(db, lid, organisation_id)
        if lead:
            lead.status = status
            count += 1
    await db.flush()
    await _log_audit(db, actor_id, organisation_id, "lead.bulk_status", "lead", "",
                     {"count": count, "status": status.value})
    return count


async def bulk_assign(
    db: AsyncSession,
    lead_ids: List[uuid.UUID],
    assigned_to: uuid.UUID,
    organisation_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> int:
    """Assign multiple leads to a user. Returns count updated."""
    count = 0
    for lid in lead_ids:
        lead = await get_lead(db, lid, organisation_id)
        if lead:
            lead.assigned_to = assigned_to
            count += 1
    await db.flush()
    await _log_audit(db, actor_id, organisation_id, "lead.bulk_assign", "lead", "",
                     {"count": count, "assigned_to": str(assigned_to)})
    return count


# ─── Search History ─────────────────────────────────────────────────────────

async def save_search_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    organisation_id: uuid.UUID,
    query: str,
    location: Optional[str],
    radius_km: int,
    results_count: int,
    filters: Optional[dict] = None,
) -> SearchHistory:
    history = SearchHistory(
        organisation_id=organisation_id,
        user_id=user_id,
        query=query,
        location=location,
        radius_km=radius_km,
        results_count=results_count,
        filters=filters or {},
    )
    db.add(history)
    await db.flush()
    return history


async def get_search_history(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    limit: int = 20,
) -> List[SearchHistory]:
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.organisation_id == organisation_id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())