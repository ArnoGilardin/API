"""
Pydantic schemas for request/response validation.
"""
from app.schemas.schemas import (
    # Search
    SearchRequest,
    SearchResponse,

    # Scrape
    ScrapeStatus,
    ScrapeStatusResponse,

    # Lead
    LeadBase,
    LeadCreate,
    LeadResponse,
    LeadsListResponse,

    # Company
    CompanyBase,
    CompanyResponse,

    # Filter
    FilterRequest,

    # Export
    ExportFormat,

    # Consent
    ConsentRevokeRequest,
    ConsentRevokeResponse,

    # Common
    LocationInput,
    LocationOutput,
)

__all__ = [
    "SearchRequest",
    "SearchResponse",
    "ScrapeStatus",
    "ScrapeStatusResponse",
    "LeadBase",
    "LeadCreate",
    "LeadResponse",
    "LeadsListResponse",
    "CompanyBase",
    "CompanyResponse",
    "FilterRequest",
    "ExportFormat",
    "ConsentRevokeRequest",
    "ConsentRevokeResponse",
    "LocationInput",
    "LocationOutput",
]
