"""
PagesJaunes.fr spider.
Scrapes business listings from PagesJaunes (French Yellow Pages).

Legal Status: Public business directory, robots.txt allows crawling with rate limits.
"""
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import re

from app.workers.scraper.spiders.base_spider import BaseSpider


class PagesJaunesSpider(BaseSpider):
    """
    Spider for PagesJaunes.fr (French Yellow Pages).

    Data available:
    - Company name
    - Address
    - Phone
    - Website
    - Sector/Activity
    - Sometimes email on company pages
    """

    def __init__(self):
        super().__init__("https://www.pagesjaunes.fr")

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict]:
        """
        Scrape leads from PagesJaunes.

        Args:
            search_params: Search parameters including sector, location

        Returns:
            List of lead dictionaries
        """
        leads = []

        # Build search query
        sector = search_params.get("sector", "")
        location_str = self._build_location_string(search_params)

        if not sector:
            return leads

        # Construct search URL (simplified - actual URL structure may vary)
        search_url = f"{self.base_url}/recherche?quoi={sector}&ou={location_str}"

        try:
            # Note: This is a simplified example
            # In production, you would:
            # 1. Properly handle pagination
            # 2. Handle dynamic content (might need Playwright)
            # 3. Parse structured data (schema.org)
            # 4. Handle errors and retries

            html = self.fetch_page(search_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Parse business listings
            listings = soup.find_all('div', class_='bi-list-item')  # Example selector

            for listing in listings:
                lead_data = self._parse_listing(listing, search_params)
                if lead_data and lead_data.get("email"):
                    leads.append(lead_data)

                # Respect max_results
                if len(leads) >= search_params.get("max_results", 200):
                    break

        except Exception as e:
            print(f"Error scraping PagesJaunes: {e}")

        return leads

    def _parse_listing(self, listing, search_params: Dict) -> Dict:
        """
        Parse a single business listing.

        Args:
            listing: BeautifulSoup element
            search_params: Search parameters

        Returns:
            Lead data dictionary or None
        """
        try:
            # Extract basic info
            company_name = listing.find('h3', class_='bi-denom')
            if not company_name:
                return None

            company_name = company_name.get_text(strip=True)

            # Extract address
            address_elem = listing.find('div', class_='bi-address')
            address = address_elem.get_text(strip=True) if address_elem else None

            # Extract phone
            phone_elem = listing.find('span', class_='number-contact')
            phone = self.extract_phone(phone_elem.get_text()) if phone_elem else None

            # Extract website link
            website_elem = listing.find('a', class_='pj-lb-link-tel')
            website = website_elem.get('href') if website_elem else None

            # Try to extract email from listing or visit detail page
            emails = self.extract_emails(listing.get_text())
            email = emails[0] if emails else None

            # If no email in listing, try to visit company page
            if not email and website:
                try:
                    company_html = self.fetch_page(website)
                    emails = self.extract_emails(company_html)
                    email = emails[0] if emails else None
                except:
                    pass

            # Skip if no email found
            if not email:
                return None

            # Build lead data
            lead_data = {
                "email": email,
                "company_name": company_name,
                "address": address,
                "phone": phone,
                "website": website,
                "sector": search_params.get("sector"),
                "tags": ["pagesjaunes"],
            }

            # Calculate confidence score
            lead_data["confidence_score"] = self.calculate_confidence_score(lead_data)

            return lead_data

        except Exception as e:
            print(f"Error parsing listing: {e}")
            return None

    def _build_location_string(self, search_params: Dict) -> str:
        """Build location string for search URL."""
        location = search_params.get("location")
        if location:
            # In production, you would use reverse geocoding to get city name
            return "Paris"  # Placeholder
        return ""
