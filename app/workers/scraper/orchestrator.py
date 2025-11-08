"""
Scraping orchestrator.
Coordinates scraping across multiple sources with respect to legal constraints.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import time
import random

from app.models.models import Source, Lead, Company
from app.workers.scraper.spiders.pagesjaunes_spider import PagesJaunesSpider
from app.workers.scraper.spiders.kompass_spider import KompassSpider
from app.workers.scraper.spiders.societe_spider import SocieteSpider
from app.config import settings


class ScraperOrchestrator:
    """
    Orchestrates scraping across multiple sources.

    IMPORTANT LEGAL CONSTRAINTS:
    - LinkedIn scraping is FORBIDDEN (TOS violation)
    - All sources must respect robots.txt
    - Rate limiting is enforced
    - User-agent must be identified
    """

    FORBIDDEN_SOURCES = ["linkedin.com", "linkedin.fr"]

    def __init__(self, db: Session, search_params: Dict[str, Any]):
        """
        Initialize orchestrator.

        Args:
            db: Database session
            search_params: Search parameters
        """
        self.db = db
        self.search_params = search_params
        self.results: List[Dict] = []

    def run(self) -> Dict[str, Any]:
        """
        Run scraping job across all enabled sources.

        Returns:
            Dictionary with scraping results
        """
        # Get enabled sources from database
        sources = (
            self.db.query(Source)
            .filter(Source.robots_allowed == True)
            .all()
        )

        # Filter out forbidden sources
        sources = [
            s for s in sources
            if not any(forbidden in s.url.lower() for forbidden in self.FORBIDDEN_SOURCES)
        ]

        total_found = 0
        total_saved = 0
        sources_used = []
        lead_ids = []

        # Run scrapers for each source
        for source in sources:
            try:
                spider = self._get_spider_for_source(source)

                if spider:
                    print(f"🕷️  Scraping from {source.name}...")

                    # Run spider
                    leads = spider.scrape(self.search_params)

                    # Save leads to database
                    for lead_data in leads:
                        lead_id = self._save_lead(lead_data, source)
                        if lead_id:
                            lead_ids.append(str(lead_id))
                            total_saved += 1

                    total_found += len(leads)
                    sources_used.append(source.name)

                    print(f"✅ Found {len(leads)} leads from {source.name}")

                    # Respect rate limiting
                    delay = random.uniform(
                        settings.DOWNLOAD_DELAY,
                        settings.DOWNLOAD_DELAY * 2 if settings.RANDOMIZE_DOWNLOAD_DELAY else settings.DOWNLOAD_DELAY
                    )
                    time.sleep(delay)

            except Exception as e:
                print(f"❌ Error scraping {source.name}: {e}")
                continue

        return {
            "total_found": total_found,
            "total_saved": total_saved,
            "sources_used": sources_used,
            "lead_ids": lead_ids,
        }

    def _get_spider_for_source(self, source: Source):
        """Get appropriate spider for a source."""
        if "pagesjaunes" in source.url.lower():
            return PagesJaunesSpider()
        elif "kompass" in source.url.lower():
            return KompassSpider()
        elif "societe" in source.url.lower():
            return SocieteSpider()
        else:
            return None

    def _save_lead(self, lead_data: Dict, source: Source) -> str:
        """
        Save a lead to the database.

        Args:
            lead_data: Lead information
            source: Source entity

        Returns:
            Lead ID if saved, None otherwise
        """
        try:
            # Check if lead already exists (by email)
            existing_lead = (
                self.db.query(Lead)
                .filter(Lead.email == lead_data["email"])
                .first()
            )

            if existing_lead:
                # Update existing lead if new data is better
                if lead_data.get("confidence_score", 0) > (existing_lead.confidence_score or 0):
                    existing_lead.confidence_score = lead_data.get("confidence_score")
                self.db.commit()
                return existing_lead.id

            # Create or get company
            company = None
            if lead_data.get("company_name"):
                company = (
                    self.db.query(Company)
                    .filter(Company.name == lead_data["company_name"])
                    .first()
                )

                if not company:
                    company = Company(
                        name=lead_data["company_name"],
                        address=lead_data.get("company_address"),
                        website=lead_data.get("website"),
                        sector=lead_data.get("sector"),
                        siren=lead_data.get("siren"),
                    )
                    self.db.add(company)
                    self.db.commit()
                    self.db.refresh(company)

            # Create new lead
            lead = Lead(
                first_name=lead_data.get("first_name"),
                last_name=lead_data.get("last_name"),
                function=lead_data.get("function"),
                email=lead_data["email"],
                company_id=company.id if company else None,
                address=lead_data.get("address"),
                phone=lead_data.get("phone"),
                website=lead_data.get("website"),
                sector=lead_data.get("sector"),
                confidence_score=lead_data.get("confidence_score", 0.5),
                tags=lead_data.get("tags", []),
                source_id=source.id,
            )

            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)

            return lead.id

        except Exception as e:
            self.db.rollback()
            print(f"Error saving lead: {e}")
            return None
