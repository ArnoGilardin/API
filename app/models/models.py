"""
SQLAlchemy ORM models for the B2B Lead Generation API.
Implements the database schema with GDPR compliance features.
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Numeric, CheckConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.database import Base


class Source(Base):
    """
    Data sources for lead scraping (PagesJaunes, Kompass, etc.).
    Tracks which sources are allowed for scraping based on robots.txt.
    """
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 'HTML' or 'API'
    robots_allowed = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    leads = relationship("Lead", back_populates="source")

    __table_args__ = (
        CheckConstraint("type IN ('HTML', 'API')", name='check_source_type'),
    )


class Company(Base):
    """
    Companies extracted from various sources.
    Normalized to avoid duplication.
    """
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    siren = Column(String(9), unique=True, nullable=True)  # French company ID
    address = Column(Text)
    website = Column(Text)
    sector = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    leads = relationship("Lead", back_populates="company")

    # Indexes
    __table_args__ = (
        Index('idx_companies_siren', 'siren'),
        Index('idx_companies_sector', 'sector'),
    )


class Lead(Base):
    """
    Individual leads (decision-makers) with contact information.
    Core entity for B2B prospecting with GDPR compliance fields.
    """
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(255))
    last_name = Column(String(255))
    function = Column(String(255))  # Job title
    email = Column(String(255), unique=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    address = Column(Text)
    phone = Column(String(20))
    website = Column(Text)
    sector = Column(String(255))

    # Geolocation (PostGIS point)
    location = Column(Geography(geometry_type='POINT', srid=4326))

    # Quality metrics
    confidence_score = Column(Numeric(3, 2), default=0.5)
    tags = Column(JSONB, default=list)  # ['verified_email', 'opt_out', etc.]

    # Source tracking
    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id'))
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="leads")
    source = relationship("Source", back_populates="leads")
    enrichments = relationship("Enrichment", back_populates="lead", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="lead", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="lead", cascade="all, delete-orphan")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
        Index('idx_leads_location', 'location', postgresql_using='gist'),
        Index('idx_leads_sector_function', 'sector', 'function'),
        Index('idx_leads_email_verified', 'email', postgresql_where=Column('verified_at').isnot(None)),
        Index('idx_leads_confidence', 'confidence_score', postgresql_ops={'confidence_score': 'DESC'}),
        Index('idx_leads_tags', 'tags', postgresql_using='gin'),
    )


class Scrape(Base):
    """
    Scraping jobs tracking.
    Monitors status of asynchronous scraping operations.
    """
    __tablename__ = "scrapes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    status = Column(String(50), default='queued')  # queued, running, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    sources_used = Column(JSONB, default=list)  # List of source IDs used
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Search parameters (stored for reference)
    search_params = Column(JSONB)

    # Results metrics
    total_found = Column(Integer, default=0)
    total_saved = Column(Integer, default=0)

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'completed', 'failed')", name='check_scrape_status'),
        Index('idx_scrapes_job_id', 'job_id'),
        Index('idx_scrapes_status', 'status'),
    )


class Enrichment(Base):
    """
    Additional data enrichment for leads.
    Stores data from third-party APIs (Google Places, etc.).
    """
    __tablename__ = "enrichments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'))
    enriched_data = Column(JSONB, nullable=False)
    provider = Column(String(255), nullable=False)  # e.g., 'google_places', 'societe.com'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="enrichments")

    # Indexes
    __table_args__ = (
        Index('idx_enrichments_lead_id', 'lead_id'),
    )


class Consent(Base):
    """
    GDPR consent tracking.
    Manages opt-in/opt-out status and data processing requests.
    """
    __tablename__ = "consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'))
    consented = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True))
    request_id = Column(String(255))  # External request tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # GDPR request type
    request_type = Column(String(50))  # 'opt_out', 'access', 'delete', 'rectify'

    # Relationships
    lead = relationship("Lead", back_populates="consents")

    # Indexes
    __table_args__ = (
        Index('idx_consents_lead_id', 'lead_id'),
    )


class Log(Base):
    """
    Audit logs for all operations.
    Tracks who did what, when (GDPR compliance).
    """
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(255), nullable=False)
    user_id = Column(String(255))  # API key or user identifier
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id'))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(JSONB)

    # Relationships
    lead = relationship("Lead", back_populates="logs")

    # Indexes
    __table_args__ = (
        Index('idx_logs_timestamp', 'timestamp', postgresql_ops={'timestamp': 'DESC'}),
        Index('idx_logs_action', 'action'),
    )
