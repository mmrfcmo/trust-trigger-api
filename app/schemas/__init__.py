"""Pydantic schemas for Identity Engine and Lead Intelligence Engine."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models import UserRole, LeadStatus, LeadSource


# ─── Auth ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    organisation_name: str = Field(..., min_length=1, max_length=255)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# ─── User ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.agent
    organisation_id: UUID


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    organisation_id: UUID
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    phone: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ─── Organisation ───────────────────────────────────────────────────────────

class OrganisationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    domain: Optional[str] = None


class OrganisationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict] = None


class OrganisationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    domain: Optional[str]
    logo_url: Optional[str]
    is_active: bool
    settings: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ─── Audit Log ──────────────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    organisation_id: UUID
    action: str
    resource: str
    resource_id: Optional[str]
    details: dict
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class AuditLogList(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# ─── Lead ───────────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    source: LeadSource = LeadSource.manual


class LeadUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_to: Optional[UUID] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    opportunity_score: Optional[int] = None
    opportunity_reason: Optional[str] = None


class LeadResponse(BaseModel):
    id: UUID
    organisation_id: UUID
    assigned_to: Optional[UUID]
    business_name: str
    website: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postcode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    google_place_id: Optional[str]
    google_rating: Optional[float]
    google_reviews_count: Optional[int]
    google_categories: List
    google_photos_count: Optional[int]
    opportunity_score: int
    opportunity_reason: Optional[str]
    status: LeadStatus
    source: LeadSource
    tags: List
    notes: Optional[str]
    last_scanned_at: Optional[datetime]
    trust_score: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LeadList(BaseModel):
    items: List[LeadResponse]
    total: int
    page: int
    page_size: int


# ─── Search ─────────────────────────────────────────────────────────────────

class GooglePlacesSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=255)
    location: Optional[str] = None
    radius_km: int = Field(default=10, ge=1, le=100)


class GooglePlacesResult(BaseModel):
    place_id: str
    business_name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    categories: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos_count: Optional[int] = None


class GooglePlacesSearchResponse(BaseModel):
    results: List[GooglePlacesResult]
    total: int
    query: str
    location: Optional[str]


class SearchHistoryResponse(BaseModel):
    id: UUID
    query: str
    location: Optional[str]
    radius_km: int
    results_count: int
    created_at: datetime

    class Config:
        orm_mode = True


class SearchHistoryList(BaseModel):
    items: List[SearchHistoryResponse]
    total: int


# ─── Bulk Operations ────────────────────────────────────────────────────────

class BulkStatusUpdate(BaseModel):
    lead_ids: List[UUID]
    status: LeadStatus


class BulkAssign(BaseModel):
    lead_ids: List[UUID]
    assigned_to: UUID