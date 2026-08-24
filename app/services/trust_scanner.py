"""Trust Intelligence Engine: website and Google Business scanner."""
import uuid
import re
import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trust_scan import TrustScan, TrustStandard, ScanStatus, ScanType
from app.models import Lead
from app.schemas.trust_scan import (
    WebsiteScanResult, GoogleBusinessScanResult, TrustStandardResult,
    WEBSITE_STANDARDS, GOOGLE_STANDARDS,
)
from app.services import _log_audit


# ─── Website Scanner ────────────────────────────────────────────────────────

async def scan_website(url: str) -> WebsiteScanResult:
    """Scan a website for trust signals.

    Visits the page, analyses HTML content for each standard.
    Returns a structured result with pass/fail per standard.
    """
    # Normalise URL
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    results = {}
    passed_count = 0
    total_count = len(WEBSITE_STANDARDS)
    overall_score = 0
    overall_max = sum(s[2] for s in WEBSITE_STANDARDS)

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ", strip=True).lower()
            links = [a.get("href", "").lower() for a in soup.find_all("a")]
            all_text = text + " " + " ".join(links)

            # HTTPS
            https_ok = response.url.scheme == "https"
            results["https"] = _standard_result("https", https_ok, 10, "HTTPS" + (" enabled" if https_ok else " not enabled"))

            # Contact page
            contact_found = bool(re.search(r"contact|get in touch|reach us", all_text))
            results["contact_page"] = _standard_result("contact_page", contact_found, 15,
                "Contact page" + (" found" if contact_found else " not found"))

            # About page
            about_found = bool(re.search(r"about us|about|our story|who we are", all_text))
            results["about_page"] = _standard_result("about_page", about_found, 10,
                "About page" + (" found" if about_found else " not found"))

            # CTA
            cta_found = bool(re.search(r"get started|book now|sign up|call now|buy now|contact us today|free quote", all_text))
            results["cta"] = _standard_result("cta", cta_found, 10,
                "Call-to-action" + (" found" if cta_found else " not found"))

            # Testimonials
            testimonial_found = bool(re.search(r"testimonial|review|what our clients say|trustpilot|google review", all_text))
            results["testimonials"] = _standard_result("testimonials", testimonial_found, 15,
                "Testimonials" + (" found" if testimonial_found else " not found"))

            # FAQ
            faq_found = bool(re.search(r"faq|frequently asked|common questions|help centre", all_text))
            results["faq"] = _standard_result("faq", faq_found, 10,
                "FAQ section" + (" found" if faq_found else " not found"))

            # Service pages
            services_found = bool(re.search(r"service|product|what we do|our work|portfolio", all_text))
            results["service_pages"] = _standard_result("service_pages", services_found, 15,
                "Service pages" + (" found" if services_found else " not found"))

            # Privacy policy
            privacy_found = bool(re.search(r"privacy policy|privacy|cookie policy|gdpr", all_text))
            results["privacy_policy"] = _standard_result("privacy_policy", privacy_found, 5,
                "Privacy policy" + (" found" if privacy_found else " not found"))

            # Mobile responsive (check viewport meta tag)
            viewport = soup.find("meta", attrs={"name": "viewport"})
            mobile_ok = viewport is not None
            results["mobile_responsive"] = _standard_result("mobile_responsive", mobile_ok, 10,
                "Mobile responsive" + (" (viewport meta found)" if mobile_ok else " (no viewport meta)"))

    except httpx.RequestError as e:
        # Connection failure — all fail
        for name, label, points in WEBSITE_STANDARDS:
            results[name] = _standard_result(name, False, points, f"Connection failed: {str(e)[:80]}")
    except Exception as e:
        for name, label, points in WEBSITE_STANDARDS:
            results[name] = _standard_result(name, False, points, f"Scan error: {str(e)[:80]}")

    # Calculate totals
    for name, label, points in WEBSITE_STANDARDS:
        r = results.get(name)
        if r:
            overall_score += r.score
            if r.passed:
                passed_count += 1

    return WebsiteScanResult(
        https=results.get("https", _standard_result("https", False, 10, "Not scanned")),
        contact_page=results.get("contact_page", _standard_result("contact_page", False, 15, "Not scanned")),
        about_page=results.get("about_page", _standard_result("about_page", False, 10, "Not scanned")),
        cta=results.get("cta", _standard_result("cta", False, 10, "Not scanned")),
        testimonials=results.get("testimonials", _standard_result("testimonials", False, 15, "Not scanned")),
        faq=results.get("faq", _standard_result("faq", False, 10, "Not scanned")),
        service_pages=results.get("service_pages", _standard_result("service_pages", False, 15, "Not scanned")),
        privacy_policy=results.get("privacy_policy", _standard_result("privacy_policy", False, 5, "Not scanned")),
        mobile_responsive=results.get("mobile_responsive", _standard_result("mobile_responsive", False, 10, "Not scanned")),
        overall_score=overall_score,
        overall_max=overall_max,
        passed_count=passed_count,
        total_count=total_count,
    )


def _standard_result(name: str, passed: bool, max_points: int, details: str) -> TrustStandardResult:
    return TrustStandardResult(
        standard_name=name,
        passed=passed,
        score=max_points if passed else 0,
        max_points=max_points,
        details=details,
    )


# ─── Google Business Scanner ────────────────────────────────────────────────

async def scan_google_business(place_id: str, api_key: Optional[str] = None) -> GoogleBusinessScanResult:
    """Scan Google Business Profile for trust signals.

    In production, this calls the Google Places Details API.
    For development, returns deterministic mock data.
    """
    # TODO: Replace with actual Google Places Details API call
    # GET https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=rating,review,photo,editorial_summary,types&key={api_key}

    passed_count = 0
    total_count = len(GOOGLE_STANDARDS)
    overall_score = 0
    overall_max = sum(s[2] for s in GOOGLE_STANDARDS)

    # Mock data for development
    mock_data = {
        "rating": 4.2,
        "reviews_count": 87,
        "photos_count": 15,
        "description": "Professional business services company",
        "categories": ["Business Services", "Consulting"],
    }

    results = {}

    # Rating ≥ 4.0
    rating_ok = mock_data["rating"] >= 4.0
    results["rating"] = _standard_result("rating", rating_ok, 25,
        f"Rating: {mock_data['rating']}" + (" ✓" if rating_ok else " (below 4.0 threshold)"))

    # Has reviews
    has_reviews = mock_data["reviews_count"] > 0
    results["reviews"] = _standard_result("reviews", has_reviews, 20,
        f"{mock_data['reviews_count']} reviews" if has_reviews else "No reviews found")

    # Has photos
    has_photos = mock_data["photos_count"] > 0
    results["photos"] = _standard_result("photos", has_photos, 20,
        f"{mock_data['photos_count']} photos" if has_photos else "No photos found")

    # Has description
    has_desc = bool(mock_data["description"])
    results["description"] = _standard_result("description", has_desc, 20,
        "Description found" if has_desc else "No description")

    # Has categories
    has_cats = len(mock_data["categories"]) > 0
    results["categories"] = _standard_result("categories", has_cats, 15,
        f"Categories: {', '.join(mock_data['categories'])}" if has_cats else "No categories")

    for name, label, points in GOOGLE_STANDARDS:
        r = results.get(name)
        if r:
            overall_score += r.score
            if r.passed:
                passed_count += 1

    return GoogleBusinessScanResult(
        rating=results.get("rating", _standard_result("rating", False, 25, "Not scanned")),
        reviews=results.get("reviews", _standard_result("reviews", False, 20, "Not scanned")),
        photos=results.get("photos", _standard_result("photos", False, 20, "Not scanned")),
        description=results.get("description", _standard_result("description", False, 20, "Not scanned")),
        categories=results.get("categories", _standard_result("categories", False, 15, "Not scanned")),
        overall_score=overall_score,
        overall_max=overall_max,
        passed_count=passed_count,
        total_count=total_count,
    )


# ─── Scan Orchestration ─────────────────────────────────────────────────────

async def run_scan(
    db: AsyncSession,
    lead_id: uuid.UUID,
    organisation_id: uuid.UUID,
    user_id: uuid.UUID,
    scan_type: ScanType = ScanType.full,
) -> TrustScan:
    """Run a trust scan for a lead. Creates scan record, executes checks, saves results."""
    # Get lead
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.organisation_id == organisation_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise ValueError("Lead not found")

    # Create scan record
    scan = TrustScan(
        organisation_id=organisation_id,
        lead_id=lead_id,
        user_id=user_id,
        scan_type=scan_type,
        status=ScanStatus.in_progress,
        target_url=lead.website,
        google_place_id=lead.google_place_id,
        started_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    await db.flush()

    errors = []
    website_result = None
    google_result = None

    try:
        if scan_type in (ScanType.website, ScanType.full) and lead.website:
            website_result = await scan_website(lead.website)
            # Save individual standards
            for std_name in [s[0] for s in WEBSITE_STANDARDS]:
                std = getattr(website_result, std_name, None)
                if std:
                    ts = TrustStandard(
                        scan_id=scan.id,
                        category="website",
                        standard_name=std.standard_name,
                        passed=std.passed,
                        score=std.score,
                        max_points=std.max_points,
                        details=std.details,
                    )
                    db.add(ts)

        if scan_type in (ScanType.google_business, ScanType.full) and lead.google_place_id:
            google_result = await scan_google_business(lead.google_place_id)
            for std_name in [s[0] for s in GOOGLE_STANDARDS]:
                std = getattr(google_result, std_name, None)
                if std:
                    ts = TrustStandard(
                        scan_id=scan.id,
                        category="google_business",
                        standard_name=std.standard_name,
                        passed=std.passed,
                        score=std.score,
                        max_points=std.max_points,
                        details=std.details,
                    )
                    db.add(ts)

    except Exception as e:
        errors.append(str(e))

    # Update scan record
    scan.status = ScanStatus.failed if errors else ScanStatus.completed
    scan.completed_at = datetime.now(timezone.utc)
    scan.duration_ms = int((scan.completed_at - scan.started_at).total_seconds() * 1000) if scan.started_at else 0
    scan.website_results = website_result.model_dump() if website_result else {}
    scan.google_results = google_result.model_dump() if google_result else {}
    if errors:
        scan.error_message = "; ".join(errors)

    # Update lead trust score
    total_score = 0
    total_max = 0
    if website_result:
        total_score += website_result.overall_score
        total_max += website_result.overall_max
    if google_result:
        total_score += google_result.overall_score
        total_max += google_result.overall_max
    if total_max > 0:
        lead.trust_score = int((total_score / total_max) * 100)
    lead.last_scanned_at = datetime.now(timezone.utc)

    await db.flush()
    await _log_audit(db, user_id, organisation_id, "scan.completed", "trust_scan", str(scan.id),
                     {"lead_id": str(lead_id), "score": lead.trust_score})

    return scan


async def get_scan(db: AsyncSession, scan_id: uuid.UUID, organisation_id: uuid.UUID) -> Optional[TrustScan]:
    result = await db.execute(
        select(TrustScan).where(TrustScan.id == scan_id, TrustScan.organisation_id == organisation_id)
    )
    return result.scalar_one_or_none()


async def get_scans(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    lead_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[TrustScan], int]:
    query = select(TrustScan).where(TrustScan.organisation_id == organisation_id)
    count_query = select(func.count()).select_from(TrustScan).where(TrustScan.organisation_id == organisation_id)
    if lead_id:
        query = query.where(TrustScan.lead_id == lead_id)
        count_query = count_query.where(TrustScan.lead_id == lead_id)
    query = query.order_by(TrustScan.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0