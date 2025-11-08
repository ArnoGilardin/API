"""
Base spider class with common functionality.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

from app.config import settings


class BaseSpider(ABC):
    """
    Base class for all web scrapers.

    Implements:
    - robots.txt checking
    - Rate limiting
    - Email extraction
    - Common parsing utilities
    """

    def __init__(self, base_url: str):
        """
        Initialize spider.

        Args:
            base_url: Base URL of the target website
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.USER_AGENT})

        # Initialize robots.txt parser
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(base_url, "/robots.txt"))

        if settings.RESPECT_ROBOTS_TXT:
            try:
                self.robot_parser.read()
            except Exception as e:
                print(f"Warning: Could not read robots.txt for {base_url}: {e}")

    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False otherwise
        """
        if not settings.RESPECT_ROBOTS_TXT:
            return True

        return self.robot_parser.can_fetch(settings.USER_AGENT, url)

    def fetch_page(self, url: str) -> str:
        """
        Fetch a web page with rate limiting.

        Args:
            url: URL to fetch

        Returns:
            Page HTML content

        Raises:
            Exception: If fetch fails or not allowed
        """
        if not self.can_fetch(url):
            raise Exception(f"robots.txt forbids fetching {url}")

        # Rate limiting
        time.sleep(settings.DOWNLOAD_DELAY)

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        return response.text

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from text using regex.

        Args:
            text: Text to extract from

        Returns:
            List of unique email addresses
        """
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)

        # Filter out common non-personal emails
        excluded_patterns = [
            r'@example\.com',
            r'@test\.com',
            r'noreply@',
            r'no-reply@',
            r'info@',
            r'contact@',
            r'admin@',
        ]

        filtered_emails = []
        for email in emails:
            if not any(re.search(pattern, email, re.IGNORECASE) for pattern in excluded_patterns):
                filtered_emails.append(email.lower())

        return list(set(filtered_emails))  # Remove duplicates

    @staticmethod
    def extract_phone(text: str) -> str:
        """
        Extract French phone number from text.

        Args:
            text: Text to extract from

        Returns:
            Phone number or None
        """
        # French phone patterns
        patterns = [
            r'\+33\s?[1-9](?:[\s.-]?\d{2}){4}',  # +33 1 23 45 67 89
            r'0[1-9](?:[\s.-]?\d{2}){4}',  # 01 23 45 67 89
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Clean up phone number
                phone = match.group(0)
                phone = re.sub(r'[\s.-]', '', phone)
                return phone

        return None

    @staticmethod
    def calculate_confidence_score(lead_data: Dict) -> float:
        """
        Calculate confidence score for a lead based on available data.

        Args:
            lead_data: Lead information

        Returns:
            Score between 0 and 1
        """
        score = 0.5  # Base score

        # Email present (already guaranteed)
        score += 0.1

        # Has first and last name
        if lead_data.get("first_name") and lead_data.get("last_name"):
            score += 0.15

        # Has function/job title
        if lead_data.get("function"):
            score += 0.1

        # Has phone
        if lead_data.get("phone"):
            score += 0.1

        # Has company info
        if lead_data.get("company_name"):
            score += 0.05

        return min(1.0, score)

    @abstractmethod
    def scrape(self, search_params: Dict[str, Any]) -> List[Dict]:
        """
        Scrape leads from the source.

        Must be implemented by subclasses.

        Args:
            search_params: Search parameters

        Returns:
            List of lead dictionaries
        """
        pass
