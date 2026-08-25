"""Trust Intelligence Engine schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.trust_scan import ScanStatus, ScanType


class ScanRequest(BaseModel):
    lead_id: UUID
    scan_type: ScanType = ScanType.full
    target_url: Optional[str] = None


class TrustStandardResult(BaseModel):
    standard_name: str
    passed: bool
    score: int
    max_points: int
    details: Optional[str] = None


class WebsiteScanResult(BaseModel):
    https: TrustStandardResult
    contact_page: TrustStandardResult
    about_page: TrustStandardResult
    cta: TrustStandardResult
    testimonials: TrustStandardResult
    faq: TrustStandardResult
    service_pages: TrustStandardResult
    privacy_policy: TrustStandardResult
    mobile_responsive: TrustStandardResult
    overall_score: int
    overall_max: int
    passed_count: int
    total_count: int


class GoogleBusinessScanResult(BaseModel):
    rating: TrustStandardResult
    reviews: TrustStandardResult
    photos: TrustStandardResult
    description: TrustStandardResult
    categories: TrustStandardResult
    overall_score: int
    overall_max: int
    passed_count: int
    total_count: int


class ScanResult(BaseModel):
    website: Optional[WebsiteScanResult] = None
    google_business: Optional[GoogleBusinessScanResult] = None


class ScanResponse(BaseModel):
    id: UUID
    organisation_id: UUID
    lead_id: Optional[UUID]
    scan_type: ScanType
    status: ScanStatus
    target_url: Optional[str]
    results: Optional[ScanResult] = None
    error_message: Optional[str]
    duration_ms: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ScanList(BaseModel):
    items: list[ScanResponse]
    total: int
    page: int
    page_size: int


# Website standard checks
WEBSITE_STANDARDS = [
    ("https", "HTTPS Enabled", 10),
    ("contact_page", "Contact Page", 15),
    ("about_page", "About Page", 10),
    ("cta", "Call-to-Action", 10),
    ("testimonials", "Testimonials / Reviews", 15),
    ("faq", "FAQ Section", 10),
    ("service_pages", "Service/Product Pages", 15),
    ("privacy_policy", "Privacy Policy", 5),
    ("mobile_responsive", "Mobile Responsive", 10),
]

GOOGLE_STANDARDS = [
    ("rating", "Google Rating ≥ 4.0", 25),
    ("reviews", "Has Reviews", 20),
    ("photos", "Has Photos", 20),
    ("description", "Business Description", 20),
    ("categories", "Business Categories", 15),
]