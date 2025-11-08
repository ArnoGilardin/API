"""
Lead management endpoints.
Retrieve, filter, and export lead data.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from uuid import UUID
from typing import Optional, List
import csv
import json
import io

from app.database import get_db
from app.schemas.schemas import (
    LeadResponse,
    LeadsListResponse,
    FilterRequest,
    ExportFormat,
)
from app.services.auth import verify_api_key
from app.models.models import Lead, Company, Source, Scrape
from app.config import settings

router = APIRouter()


def calculate_distance(lead_location, search_location) -> Optional[float]:
    """
    Calculate distance between lead and search location.
    Returns distance in kilometers or None if location not available.
    """
    if not lead_location or not search_location:
        return None

    # This is a simplified calculation
    # In production, use PostGIS ST_Distance
    return 0.0  # Placeholder


def build_lead_response(lead: Lead, search_params: dict = None) -> LeadResponse:
    """Build a LeadResponse from a Lead model."""

    # Calculate distance if search location provided
    distance_km = None
    if search_params and search_params.get("location"):
        # Would use PostGIS here in production
        distance_km = 0.0  # Placeholder

    return LeadResponse(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        function=lead.function,
        email=lead.email,
        company=lead.company.name if lead.company else None,
        address=lead.address,
        phone=lead.phone,
        website=lead.website,
        sector=lead.sector,
        location_distance_km=distance_km,
        email_verified=lead.verified_at is not None,
        confidence_score=float(lead.confidence_score) if lead.confidence_score else 0.5,
        sector_match=0.9 if lead.sector else None,  # Simplified
        tags=lead.tags or [],
        source=lead.source.name if lead.source else None,
        scraped_at=lead.scraped_at,
    )


@router.get(
    "/leads/{job_id}",
    response_model=LeadsListResponse,
    summary="Get leads from a scraping job",
    description="Retrieve leads collected by a specific scraping job with optional pagination.",
)
async def get_leads(
    job_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> LeadsListResponse:
    """
    Get leads from a completed scraping job.

    Args:
        job_id: Scraping job identifier
        page: Page number (1-indexed)
        page_size: Number of items per page
        db: Database session
        api_key: Validated API key

    Returns:
        Paginated list of leads

    Raises:
        HTTPException: If job not found or not completed
    """
    # Verify job exists
    scrape = db.query(Scrape).filter(Scrape.job_id == job_id).first()
    if not scrape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if scrape.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed yet (status: {scrape.status})",
        )

    # Get search parameters
    search_params = scrape.search_params or {}

    # Build query
    query = db.query(Lead).join(Source, isouter=True).join(Company, isouter=True)

    # Apply filters based on search params
    filters = []

    if search_params.get("sector"):
        filters.append(Lead.sector.ilike(f"%{search_params['sector']}%"))

    if search_params.get("function"):
        filters.append(Lead.function.ilike(f"%{search_params['function']}%"))

    if search_params.get("email_needle"):
        filters.append(Lead.email.ilike(f"%{search_params['email_needle']}%"))

    if filters:
        query = query.filter(and_(*filters))

    # Count total
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    leads = query.offset(offset).limit(page_size).all()

    # Build response
    lead_responses = [build_lead_response(lead, search_params) for lead in leads]

    return LeadsListResponse(
        leads=lead_responses,
        total=total,
        filtered=len(lead_responses),
        page=page,
        page_size=page_size,
    )


@router.post(
    "/leads/{job_id}/filters",
    response_model=LeadsListResponse,
    summary="Apply additional filters to leads",
    description="Filter leads from a job with advanced criteria.",
)
async def filter_leads(
    job_id: UUID,
    filters: FilterRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> LeadsListResponse:
    """
    Apply additional filters to leads.

    Args:
        job_id: Scraping job identifier
        filters: Filter criteria
        page: Page number
        page_size: Items per page
        db: Database session
        api_key: Validated API key

    Returns:
        Filtered leads list
    """
    # Verify job exists
    scrape = db.query(Scrape).filter(Scrape.job_id == job_id).first()
    if not scrape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Build query
    query = db.query(Lead)

    # Apply filters
    if filters.min_confidence_score:
        query = query.filter(Lead.confidence_score >= filters.min_confidence_score)

    if filters.email_verified_only:
        query = query.filter(Lead.verified_at.isnot(None))

    if filters.exclude_tags:
        for tag in filters.exclude_tags:
            query = query.filter(~Lead.tags.contains([tag]))

    if filters.include_tags:
        for tag in filters.include_tags:
            query = query.filter(Lead.tags.contains([tag]))

    if filters.sector:
        query = query.filter(Lead.sector.ilike(f"%{filters.sector}%"))

    if filters.function:
        query = query.filter(Lead.function.ilike(f"%{filters.function}%"))

    # Count total
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    leads = query.offset(offset).limit(page_size).all()

    # Build response
    lead_responses = [build_lead_response(lead) for lead in leads]

    return LeadsListResponse(
        leads=lead_responses,
        total=total,
        filtered=len(lead_responses),
        page=page,
        page_size=page_size,
    )


@router.get(
    "/leads/{job_id}/export",
    summary="Export leads to CSV or JSON",
    description="Export leads from a job in CSV or JSON format.",
)
async def export_leads(
    job_id: UUID,
    format: ExportFormat = Query(ExportFormat.CSV, description="Export format"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> StreamingResponse:
    """
    Export leads to CSV or JSON.

    Args:
        job_id: Scraping job identifier
        format: Export format (csv or json)
        db: Database session
        api_key: Validated API key

    Returns:
        File download response
    """
    # Verify job exists
    scrape = db.query(Scrape).filter(Scrape.job_id == job_id).first()
    if not scrape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    # Get leads (limit to MAX_EXPORT_RECORDS)
    leads = (
        db.query(Lead)
        .limit(settings.MAX_EXPORT_RECORDS)
        .all()
    )

    if format == ExportFormat.CSV:
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "first_name", "last_name", "function", "email",
            "company", "address", "phone", "website", "sector",
            "confidence_score", "email_verified", "tags", "source",
        ])

        # Write data
        for lead in leads:
            writer.writerow([
                lead.first_name or "",
                lead.last_name or "",
                lead.function or "",
                lead.email,
                lead.company.name if lead.company else "",
                lead.address or "",
                lead.phone or "",
                lead.website or "",
                lead.sector or "",
                lead.confidence_score,
                "yes" if lead.verified_at else "no",
                ",".join(lead.tags or []),
                lead.source.name if lead.source else "",
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=leads_{job_id}.csv"
            },
        )

    else:  # JSON
        # Generate JSON
        leads_data = [
            {
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "function": lead.function,
                "email": lead.email,
                "company": lead.company.name if lead.company else None,
                "address": lead.address,
                "phone": lead.phone,
                "website": lead.website,
                "sector": lead.sector,
                "confidence_score": float(lead.confidence_score) if lead.confidence_score else 0.5,
                "email_verified": lead.verified_at is not None,
                "tags": lead.tags or [],
                "source": lead.source.name if lead.source else None,
                "scraped_at": lead.scraped_at.isoformat(),
            }
            for lead in leads
        ]

        json_output = json.dumps({"leads": leads_data}, indent=2)

        return StreamingResponse(
            iter([json_output]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=leads_{job_id}.json"
            },
        )
