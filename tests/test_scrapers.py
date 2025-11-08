"""
Test scraping functionality.
"""
import pytest
from app.workers.scraper.spiders.base_spider import BaseSpider


class TestBaseSpider:
    """Test base spider functionality."""

    def test_extract_emails(self):
        """Test email extraction from text."""
        text = """
        Contact us at info@example.com or john.doe@company.fr
        Also try noreply@test.com
        """

        emails = BaseSpider.extract_emails(text)

        # Should find emails and filter out noreply
        assert "john.doe@company.fr" in emails
        assert len(emails) >= 1

    def test_extract_phone_french(self):
        """Test French phone number extraction."""
        text = "Appelez-nous au 01 23 45 67 89 ou +33 6 12 34 56 78"

        phone = BaseSpider.extract_phone(text)

        assert phone is not None
        # Should clean spaces and dashes
        assert len(phone.replace('+', '')) >= 9

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Complete lead data
        complete_lead = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "function": "CEO",
            "phone": "0123456789",
            "company_name": "ACME Corp",
        }

        score = BaseSpider.calculate_confidence_score(complete_lead)
        assert score > 0.7  # Should have high score

        # Minimal lead data
        minimal_lead = {
            "email": "test@example.com",
        }

        score = BaseSpider.calculate_confidence_score(minimal_lead)
        assert score < 0.7  # Should have lower score


class TestEmailVerification:
    """Test email verification."""

    def test_email_format_validation(self):
        """Test basic email format validation."""
        from app.services.email_verifier import verify_email_async

        # Invalid format
        assert verify_email_async("invalid-email") == False
        assert verify_email_async("") == False
        assert verify_email_async(None) == False

    def test_disposable_email_detection(self):
        """Test disposable email detection."""
        from app.services.email_verifier import is_disposable_email

        assert is_disposable_email("test@guerrillamail.com") == True
        assert is_disposable_email("test@mailinator.com") == True
        assert is_disposable_email("test@company.com") == False
