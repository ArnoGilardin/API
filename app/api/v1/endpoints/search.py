"""
Search endpoints for lead generation.
Handles job creation and scraping orchestration.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.schemas.schemas import SearchRequest, SearchResponse
from app.services.auth import verify_api_key
from app.models.models import Scrape
from app.workers.tasks import start_scraping_job

router = APIRouter()


@router.post(
    "/search_jobs",
    response_model=SearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead search job",
    description="""
    Launch an asynchronous lead scraping job based on search criteria.

    Returns a job_id that can be used to track progress and retrieve results.

    **IMPORTANT:** This API respects GDPR and legal scraping practices:
    - LinkedIn scraping is strictly forbidden
    - All sources respect robots.txt
    - Rate limiting is enforced
    - Data minimization principles are applied
    """,
)
async def create_search_job(
    request: SearchRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> SearchResponse:
    """
    Create a new scraping job.

    Args:
        request: Search parameters
        db: Database session
        api_key: Validated API key

    Returns:
        Job information with unique ID
    """
    # Generate unique job ID
    job_id = uuid4()

    # Create scrape record
    scrape = Scrape(
        job_id=job_id,
        status="queued",
        search_params={
            "sector": request.sector,
            "function": request.function,
            "email_needle": request.email_needle,
            "location": {
                "lat": request.location.lat,
                "lng": request.location.lng,
            } if request.location else None,
            "radius_km": request.radius_km,
            "max_results": request.max_results,
        },
    )

    db.add(scrape)
    db.commit()
    db.refresh(scrape)

    # Queue the scraping job (async via Celery)
    try:
        start_scraping_job.delay(str(job_id), request.dict())
    except Exception as e:
        # If Celery is not available, log error but don't fail
        print(f"Warning: Could not queue job in Celery: {e}")
        # In production, you might want to handle this differently

    # Estimate completion time (simplified)
    estimated_results = min(request.max_results, 500)
    estimated_seconds = estimated_results * 2  # ~2 seconds per lead

    return SearchResponse(
        job_id=job_id,
        status="queued",
        estimated_time=f"{estimated_seconds}s",
    )
