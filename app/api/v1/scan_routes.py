"""Trust Intelligence Engine: API routes."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.trust_scan import ScanRequest, ScanResponse, ScanList
from app.services.trust_scanner import run_scan, get_scan, get_scans

router = APIRouter(prefix="/api/v1/scans", tags=["Trust Intelligence Engine"])


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    req: ScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run a trust scan for a lead."""
    try:
        scan = await run_scan(
            db, req.lead_id, current_user.organisation_id, current_user.id, req.scan_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return ScanResponse.model_validate(scan)


@router.get("", response_model=ScanList)
async def list_scans(
    lead_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List trust scans, optionally filtered by lead."""
    scans, total = await get_scans(db, current_user.organisation_id, lead_id, skip, limit)
    return ScanList(
        items=[ScanResponse.model_validate(s) for s in scans],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_by_id(
    scan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single scan with full results."""
    scan = await get_scan(db, scan_id, current_user.organisation_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return ScanResponse.model_validate(scan)