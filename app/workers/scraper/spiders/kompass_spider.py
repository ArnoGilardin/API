"""
Kompass.com spider.
Scrapes B2B company and decision-maker data.

Legal Status: Public B2B directory. Prefers API access (paid) but web scraping
is tolerated with rate limits. Check robots.txt before deployment.
"""
from typing import Dict, List, Any
from bs4 import BeautifulSoup

from app.workers.scraper.spiders.base_spider import BaseSpider


class KompassSpider(BaseSpider):
    """
    Spider for Kompass.com (B2B business directory).

    Data available:
    - Company information
    - Decision-makers (names, functions)
    - Contact details (email, phone)
    - Business sector
    """

    def __init__(self):
        super().__init__("https://fr.kompass.com")

    def scrape(self, search_params: Dict[str, Any]) -> List[Dict]:
        """
        Scrape leads from Kompass.

        Args:
            search_params: Search parameters

        Returns:
            List of lead dictionaries
        """
        leads = []

        sector = search_params.get("sector", "")
        function = search_params.get("function", "")

        if not sector:
            return leads

        # Build search URL (simplified)
        search_url = f"{self.base_url}/fr/recherche/entreprises?q={sector}"

        try:
            html = self.fetch_page(search_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Parse company listings
            companies = soup.find_all('div', class_='company-item')  # Example

            for company in companies:
                # Visit company detail page to get decision-makers
                company_url = company.find('a')
                if not company_url:
                    continue

                company_url = company_url.get('href')
                company_leads = self._scrape_company_page(company_url, search_params)

                leads.extend(company_leads)

                if len(leads) >= search_params.get("max_results", 200):
                    break

        except Exception as e:
            print(f"Error scraping Kompass: {e}")

        return leads[:search_params.get("max_results", 200)]

    def _scrape_company_page(self, company_url: str, search_params: Dict) -> List[Dict]:
        """
        Scrape decision-makers from a company page.

        Args:
            company_url: Company detail page URL
            search_params: Search parameters

        Returns:
            List of leads from this company
        """
        leads = []

        try:
            html = self.fetch_page(company_url)
            soup = BeautifulSoup(html, 'html.parser')

            # Extract company info
            company_name = soup.find('h1', class_='company-name')
            company_name = company_name.get_text(strip=True) if company_name else None

            # Extract decision-makers section
            contacts_section = soup.find('div', class_='contacts')
            if not contacts_section:
                return leads

            contact_items = contacts_section.find_all('div', class_='contact-item')

            for contact in contact_items:
                lead_data = self._parse_contact(contact, company_name, search_params)
                if lead_data and lead_data.get("email"):
                    leads.append(lead_data)

        except Exception as e:
            print(f"Error scraping company page {company_url}: {e}")

        return leads

    def _parse_contact(self, contact, company_name: str, search_params: Dict) -> Dict:
        """Parse a contact/decision-maker."""
        try:
            # Extract name
            name_elem = contact.find('span', class_='name')
            if not name_elem:
                return None

            full_name = name_elem.get_text(strip=True)
            name_parts = full_name.split()

            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None

            # Extract function
            function_elem = contact.find('span', class_='function')
            function = function_elem.get_text(strip=True) if function_elem else None

            # Filter by function if specified
            if search_params.get("function"):
                if not function or search_params["function"].lower() not in function.lower():
                    return None

            # Extract email
            emails = self.extract_emails(contact.get_text())
            if not emails:
                return None

            email = emails[0]

            # Extract phone
            phone = self.extract_phone(contact.get_text())

            # Build lead data
            lead_data = {
                "first_name": first_name,
                "last_name": last_name,
                "function": function,
                "email": email,
                "company_name": company_name,
                "phone": phone,
                "sector": search_params.get("sector"),
                "tags": ["kompass", "b2b"],
            }

            lead_data["confidence_score"] = self.calculate_confidence_score(lead_data)

            return lead_data

        except Exception as e:
            print(f"Error parsing contact: {e}")
            return None
