"""Identity Engine: API routes for auth, users, organisations, and audit logs."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_organisation, require_role
from app.models import User, UserRole
from app.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse, UserCreate, UserUpdate,
    OrganisationResponse, OrganisationCreate, OrganisationUpdate,
    AuditLogResponse, AuditLogList,
)
from app.services import (
    register_user, login_user, reset_password_request, confirm_password_reset,
    create_user, get_user, get_users_by_organisation, update_user, delete_user,
    create_organisation, get_organisation, update_organisation,
    get_audit_logs,
)

router = APIRouter(prefix="/api/v1", tags=["Identity Engine"])


# ─── Auth ───────────────────────────────────────────────────────────────────

@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with a new organisation."""
    try:
        user, org = await register_user(
            db, req.email, req.password, req.full_name, req.organisation_name,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    _, token = await login_user(db, req.email, req.password)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and return a JWT token."""
    user, token = await login_user(
        db, req.email, req.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not user or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/auth/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return UserResponse.model_validate(current_user)


# ─── Users ──────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.admin, UserRole.manager])),
    db: AsyncSession = Depends(get_db),
):
    users, _ = await get_users_by_organisation(db, current_user.organisation_id, skip, limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_id)
    if not user or user.organisation_id != current_user.organisation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    data: UserCreate,
    current_user: User = Depends(require_role([UserRole.admin])),
    db: AsyncSession = Depends(get_db),
):
    data.organisation_id = current_user.organisation_id
    try:
        user = await create_user(db, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return UserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(require_role([UserRole.admin])),
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, user_id, data, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role([UserRole.admin])),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")
    success = await delete_user(db, user_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


# ─── Organisations ──────────────────────────────────────────────────────────

@router.get("/organisations/current", response_model=OrganisationResponse)
async def get_current_org(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await get_organisation(db, current_user.organisation_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return OrganisationResponse.model_validate(org)


@router.patch("/organisations/current", response_model=OrganisationResponse)
async def update_current_org(
    data: OrganisationUpdate,
    current_user: User = Depends(require_role([UserRole.admin])),
    db: AsyncSession = Depends(get_db),
):
    org = await update_organisation(db, current_user.organisation_id, data, current_user.id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return OrganisationResponse.model_validate(org)


# ─── Audit Logs ─────────────────────────────────────────────────────────────

@router.get("/audit-logs", response_model=AuditLogList)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_role([UserRole.admin, UserRole.manager])),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await get_audit_logs(db, current_user.organisation_id, skip, limit, action)
    return AuditLogList(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit,
    )