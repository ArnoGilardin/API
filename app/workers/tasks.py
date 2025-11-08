"""
Celery tasks for asynchronous operations.
"""
from celery import Task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import Scrape, Lead, Source
from app.workers.scraper.orchestrator import ScraperOrchestrator
from app.services.email_verifier import verify_email_async
from app.config import settings


class DatabaseTask(Task):
    """Base task with database session management."""

    _db: Session = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.workers.tasks.start_scraping_job")
def start_scraping_job(self, job_id: str, search_params: Dict[str, Any]):
    """
    Start a scraping job.

    Args:
        job_id: Unique job identifier
        search_params: Search parameters from SearchRequest
    """
    db = self.db

    try:
        # Update scrape status
        scrape = db.query(Scrape).filter(Scrape.job_id == uuid.UUID(job_id)).first()
        if not scrape:
            raise ValueError(f"Scrape job {job_id} not found")

        scrape.status = "running"
        scrape.started_at = datetime.utcnow()
        db.commit()

        # Initialize orchestrator
        orchestrator = ScraperOrchestrator(db, search_params)

        # Run scraping
        results = orchestrator.run()

        # Update scrape with results
        scrape.status = "completed"
        scrape.completed_at = datetime.utcnow()
        scrape.total_found = results.get("total_found", 0)
        scrape.total_saved = results.get("total_saved", 0)
        scrape.sources_used = results.get("sources_used", [])
        db.commit()

        # Queue email verification for collected leads
        lead_ids = results.get("lead_ids", [])
        for lead_id in lead_ids:
            verify_lead_email.delay(str(lead_id))

        return {
            "success": True,
            "job_id": job_id,
            "total_found": results.get("total_found", 0),
            "total_saved": results.get("total_saved", 0),
        }

    except Exception as e:
        # Mark job as failed
        scrape = db.query(Scrape).filter(Scrape.job_id == uuid.UUID(job_id)).first()
        if scrape:
            scrape.status = "failed"
            scrape.error_message = str(e)
            scrape.completed_at = datetime.utcnow()
            db.commit()

        raise


@celery_app.task(base=DatabaseTask, bind=True, name="app.workers.tasks.verify_lead_email")
def verify_lead_email(self, lead_id: str):
    """
    Verify a lead's email address.

    Args:
        lead_id: Lead UUID
    """
    db = self.db

    try:
        lead = db.query(Lead).filter(Lead.id == uuid.UUID(lead_id)).first()
        if not lead:
            return {"success": False, "error": "Lead not found"}

        # Skip if already verified
        if lead.verified_at:
            return {"success": True, "already_verified": True}

        # Skip if opted out
        if lead.tags and "opt_out" in lead.tags:
            return {"success": False, "error": "Lead opted out"}

        # Perform verification
        is_valid = verify_email_async(lead.email)

        if is_valid:
            lead.verified_at = datetime.utcnow()

            # Add verified_email tag
            if not lead.tags:
                lead.tags = []
            if "verified_email" not in lead.tags:
                lead.tags.append("verified_email")

            # Increase confidence score
            if lead.confidence_score:
                lead.confidence_score = min(1.0, float(lead.confidence_score) + 0.2)
            else:
                lead.confidence_score = 0.7

            db.commit()

            return {"success": True, "email": lead.email, "valid": True}
        else:
            # Mark as invalid
            if not lead.tags:
                lead.tags = []
            if "invalid_email" not in lead.tags:
                lead.tags.append("invalid_email")

            # Decrease confidence score
            if lead.confidence_score:
                lead.confidence_score = max(0.0, float(lead.confidence_score) - 0.2)

            db.commit()

            return {"success": True, "email": lead.email, "valid": False}

    except Exception as e:
        return {"success": False, "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True, name="app.workers.tasks.cleanup_old_data")
def cleanup_old_data(self):
    """
    Clean up old data based on retention policy (GDPR compliance).

    Runs daily to delete data older than DATA_RETENTION_DAYS.
    """
    db = self.db

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.DATA_RETENTION_DAYS)

        # Delete old leads
        deleted_leads = (
            db.query(Lead)
            .filter(Lead.created_at < cutoff_date)
            .delete(synchronize_session=False)
        )

        # Delete old scrapes
        deleted_scrapes = (
            db.query(Scrape)
            .filter(Scrape.created_at < cutoff_date)
            .delete(synchronize_session=False)
        )

        db.commit()

        return {
            "success": True,
            "deleted_leads": deleted_leads,
            "deleted_scrapes": deleted_scrapes,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
