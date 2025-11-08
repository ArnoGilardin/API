"""
Pydantic schemas for API request/response validation.
Based on the technical specification.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum


# ============================================================================
# Location Schemas
# ============================================================================

class LocationInput(BaseModel):
    """Geographic location input (latitude/longitude)."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class LocationOutput(BaseModel):
    """Geographic location output."""
    lat: float
    lng: float


# ============================================================================
# Search Schemas
# ============================================================================

class SearchRequest(BaseModel):
    """Request schema for POST /api/v1/search_jobs."""
    sector: Optional[str] = Field(None, description="Business sector (e.g., 'plomberie')")
    function: Optional[str] = Field(None, description="Job function (e.g., 'directeur commercial')")
    email_needle: Optional[str] = Field(None, description="Email pattern to search for")
    location: Optional[LocationInput] = Field(None, description="Geographic center point")
    radius_km: Optional[float] = Field(20, ge=1, le=100, description="Search radius in kilometers")
    max_results: int = Field(200, ge=1, le=1000, description="Maximum number of results")

    @validator('radius_km')
    def validate_radius(cls, v):
        """Ensure radius is within acceptable range."""
        if v and v > 100:
            raise ValueError("Radius cannot exceed 100km for performance reasons")
        return v


class SearchResponse(BaseModel):
    """Response schema for search job creation."""
    job_id: UUID = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Initial job status (queued)")
    estimated_time: str = Field(..., description="Estimated completion time")


# ============================================================================
# Scrape Schemas
# ============================================================================

class ScrapeStatus(str, Enum):
    """Possible scrape job statuses."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeStatusResponse(BaseModel):
    """Response schema for GET /api/v1/scrapes/{job_id}."""
    job_id: UUID
    status: ScrapeStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sources_used: List[str] = []
    total_found: int = 0
    total_saved: int = 0
    error_message: Optional[str] = None


# ============================================================================
# Company Schemas
# ============================================================================

class CompanyBase(BaseModel):
    """Base company information."""
    name: str
    siren: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None


class CompanyResponse(CompanyBase):
    """Company response with ID."""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Lead Schemas
# ============================================================================

class LeadBase(BaseModel):
    """Base lead information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    function: Optional[str] = None
    email: EmailStr
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    company_id: Optional[UUID] = None
    location: Optional[LocationInput] = None
    source_id: Optional[UUID] = None


class LeadResponse(LeadBase):
    """Detailed lead response (matches spec example)."""
    id: UUID
    company: Optional[str] = Field(None, description="Company name")
    location_distance_km: Optional[float] = Field(None, description="Distance from search center")
    email_verified: bool = Field(False, description="Whether email has been verified")
    confidence_score: float = Field(..., ge=0, le=1, description="Lead quality score")
    sector_match: Optional[float] = Field(None, ge=0, le=1, description="Sector matching score")
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = Field(None, description="Source name")
    scraped_at: datetime

    class Config:
        from_attributes = True


class LeadsListResponse(BaseModel):
    """Response for lead listing endpoints."""
    leads: List[LeadResponse]
    total: int = Field(..., description="Total leads found")
    filtered: int = Field(..., description="Leads after filtering")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(50, description="Items per page")


# ============================================================================
# Filter Schemas
# ============================================================================

class FilterRequest(BaseModel):
    """Additional filters for POST /api/v1/leads/{job_id}/filters."""
    min_confidence_score: Optional[float] = Field(None, ge=0, le=1)
    email_verified_only: bool = Field(False)
    exclude_tags: List[str] = Field(default_factory=list)
    include_tags: List[str] = Field(default_factory=list)
    sector: Optional[str] = None
    function: Optional[str] = None


# ============================================================================
# Export Schemas
# ============================================================================

class ExportFormat(str, Enum):
    """Available export formats."""
    CSV = "csv"
    JSON = "json"


# ============================================================================
# Consent Schemas (GDPR)
# ============================================================================

class ConsentRevokeRequest(BaseModel):
    """Request to revoke consent (opt-out)."""
    email: EmailStr = Field(..., description="Email address to opt-out")
    request_type: str = Field("opt_out", description="Type of GDPR request")
    reason: Optional[str] = Field(None, description="Optional reason for revocation")


class ConsentRevokeResponse(BaseModel):
    """Response for consent revocation."""
    success: bool
    message: str
    request_id: UUID
    processed_at: datetime


# ============================================================================
# Webhook Schemas
# ============================================================================

class WebhookPayload(BaseModel):
    """Webhook payload for CRM integration."""
    job_id: UUID
    leads: List[LeadResponse]
    total_count: int
    timestamp: datetime


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
