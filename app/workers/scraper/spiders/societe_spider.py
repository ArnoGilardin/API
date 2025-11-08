"""
Societe.com spider.
Scrapes company legal data and management information.

Legal Status: Public legal data (INSEE/INPI). Robots.txt is permissive.
Data is factual and public record (SIREN, managers).
"""
from typing import Dict, List, Any
from bs4 import BeautifulSoup

from app.workers.scraper.spiders.base_spider import BaseSpider


class SocieteSpider(BaseSpider):
    """
    Spider for Societe.com (French company legal database).

    Data available:
    - Company legal information (SIREN/SIRET)
    - Management (CEO, directors)
    - Official address
    - Sometimes contact information
    """

    def __init__(self):
        super().__init__("https://www.societe.com")

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict]:
        """
        Scrape company and manager data from Societe.com.

        Args:
            search_params: Search parameters

        Returns:
            List of lead dictionaries
        """
        leads = []

        sector = search_params.get("sector", "")

        if not sector:
            return leads

        # Build search URL
        search_url = f"{self.base_url}/recherche?q={sector}"

        try:
            html = self.fetch_page(search_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Parse company results
            companies = soup.find_all('div', class_='company-result')  # Example

            for company in companies:
                company_leads = self._scrape_company(company, search_params)
                leads.extend(company_leads)

                if len(leads) >= search_params.get("max_results", 200):
                    break

        except Exception as e:
            print(f"Error scraping Societe.com: {e}")

        return leads[:search_params.get("max_results", 200)]

    def _scrape_company(self, company_elem, search_params: Dict) -> List[Dict]:
        """
        Extract company and management information.

        Args:
            company_elem: Company element
            search_params: Search parameters

        Returns:
            List of leads (managers)
        """
        leads = []

        try:
            # Extract company name
            company_name_elem = company_elem.find('a', class_='company-name')
            if not company_name_elem:
                return leads

            company_name = company_name_elem.get_text(strip=True)

            # Visit company detail page
            company_url = company_name_elem.get('href')
            if not company_url.startswith('http'):
                company_url = f"{self.base_url}{company_url}"

            # Scrape company detail page
            html = self.fetch_page(company_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Extract SIREN
            siren_elem = soup.find('span', {'itemprop': 'identifier'})
            siren = siren_elem.get_text(strip=True) if siren_elem else None

            # Extract address
            address_elem = soup.find('div', {'itemprop': 'address'})
            address = address_elem.get_text(strip=True) if address_elem else None

            # Extract managers/directors
            managers_section = soup.find('div', class_='dirigeants')
            if not managers_section:
                return leads

            managers = managers_section.find_all('div', class_='personne')

            for manager in managers:
                lead_data = self._parse_manager(manager, company_name, siren, address, search_params)
                if lead_data:
                    leads.append(lead_data)

        except Exception as e:
            print(f"Error scraping company: {e}")

        return leads

    def _parse_manager(self, manager_elem, company_name: str, siren: str, address: str, search_params: Dict) -> Dict:
        """Parse manager information."""
        try:
            # Extract name
            name_elem = manager_elem.find('span', class_='nom')
            if not name_elem:
                return None

            full_name = name_elem.get_text(strip=True)
            name_parts = full_name.split()

            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None

            # Extract function
            function_elem = manager_elem.find('span', class_='fonction')
            function = function_elem.get_text(strip=True) if function_elem else "Dirigeant"

            # Filter by function if specified
            if search_params.get("function"):
                if search_params["function"].lower() not in function.lower():
                    return None

            # Try to find email (might not always be available)
            emails = self.extract_emails(manager_elem.get_text())

            # If no email, try to construct one (less reliable)
            if not emails and first_name and last_name:
                # This is speculative - in production, would need verification
                # Common patterns: firstname.lastname@company.com
                # For now, we skip leads without explicit emails
                return None

            if not emails:
                return None

            email = emails[0]

            # Extract phone if available
            phone = self.extract_phone(manager_elem.get_text())

            # Build lead data
            lead_data = {
                "first_name": first_name,
                "last_name": last_name,
                "function": function,
                "email": email,
                "company_name": company_name,
                "address": address,
                "phone": phone,
                "sector": search_params.get("sector"),
                "siren": siren,
                "tags": ["societe.com", "legal_data"],
            }

            lead_data["confidence_score"] = self.calculate_confidence_score(lead_data)

            return lead_data

        except Exception as e:
            print(f"Error parsing manager: {e}")
            return None
