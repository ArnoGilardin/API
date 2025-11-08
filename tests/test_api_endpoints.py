"""
Test API endpoints.
"""
import pytest
from uuid import uuid4


class TestSearchEndpoint:
    """Test search_jobs endpoint."""

    def test_create_search_job_success(self, client, auth_headers):
        """Test successful job creation."""
        payload = {
            "sector": "plomberie",
            "function": "gérant",
            "location": {"lat": 48.8566, "lng": 2.3522},
            "radius_km": 20,
            "max_results": 50,
        }

        response = client.post(
            "/api/v1/search_jobs",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert "estimated_time" in data

    def test_create_search_job_missing_auth(self, client):
        """Test job creation without authentication."""
        payload = {"sector": "plomberie"}

        response = client.post("/api/v1/search_jobs", json=payload)

        assert response.status_code == 401

    def test_create_search_job_invalid_radius(self, client, auth_headers):
        """Test job creation with invalid radius."""
        payload = {
            "sector": "plomberie",
            "radius_km": 150,  # Exceeds max of 100
        }

        response = client.post(
            "/api/v1/search_jobs",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


class TestScrapesEndpoint:
    """Test scrapes status endpoint."""

    def test_get_scrape_status_not_found(self, client, auth_headers):
        """Test getting status of non-existent job."""
        fake_job_id = str(uuid4())

        response = client.get(
            f"/api/v1/scrapes/{fake_job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestLeadsEndpoint:
    """Test leads endpoints."""

    def test_get_leads_job_not_found(self, client, auth_headers):
        """Test getting leads from non-existent job."""
        fake_job_id = str(uuid4())

        response = client.get(
            f"/api/v1/leads/{fake_job_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_export_leads_csv(self, client, auth_headers):
        """Test CSV export."""
        # First create a job
        payload = {"sector": "test", "max_results": 10}
        create_response = client.post(
            "/api/v1/search_jobs",
            json=payload,
            headers=auth_headers,
        )

        job_id = create_response.json()["job_id"]

        # Try to export (will fail since job not completed, but tests endpoint)
        response = client.get(
            f"/api/v1/leads/{job_id}/export?format=csv",
            headers=auth_headers,
        )

        # Expect 400 since job not completed
        assert response.status_code in [400, 404]


class TestConsentsEndpoint:
    """Test GDPR consent endpoints."""

    def test_revoke_consent_email_not_found(self, client, auth_headers):
        """Test revoking consent for non-existent email."""
        payload = {
            "email": "nonexistent@example.com",
            "request_type": "opt_out",
        }

        response = client.post(
            "/api/v1/consents/revoke",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
