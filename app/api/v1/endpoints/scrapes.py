"""
Scrape job status endpoints.
Track progress of asynchronous scraping jobs.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas.schemas import ScrapeStatusResponse
from app.services.auth import verify_api_key
from app.models.models import Scrape

router = APIRouter()


@router.get(
    "/scrapes/{job_id}",
    response_model=ScrapeStatusResponse,
    summary="Get scrape job status",
    description="Retrieve the current status and progress of a scraping job.",
)
async def get_scrape_status(
    job_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
) -> ScrapeStatusResponse:
    """
    Get status of a scraping job.

    Args:
        job_id: Unique job identifier
        db: Database session
        api_key: Validated API key

    Returns:
        Current job status and metrics

    Raises:
        HTTPException: If job not found
    """
    # Find scrape job
    scrape = db.query(Scrape).filter(Scrape.job_id == job_id).first()

    if not scrape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scrape job {job_id} not found",
        )

    return ScrapeStatusResponse(
        job_id=scrape.job_id,
        status=scrape.status,
        started_at=scrape.started_at,
        completed_at=scrape.completed_at,
        sources_used=scrape.sources_used or [],
        total_found=scrape.total_found,
        total_saved=scrape.total_saved,
        error_message=scrape.error_message,
    )
