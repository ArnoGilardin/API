"""
B2B Lead Generation API - Main Application Entry Point

This API provides GDPR-compliant lead generation through legal web scraping.

IMPORTANT LEGAL NOTICES:
- LinkedIn scraping is STRICTLY FORBIDDEN (TOS violation + legal risks)
- All sources respect robots.txt and rate limiting
- GDPR compliant with consent management and data minimization
- Data retention: 3 years maximum
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import init_db, engine
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Initialize database on startup, cleanup on shutdown.
    """
    # Startup
    print("🚀 Starting B2B Lead Generation API...")

    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    yield

    # Shutdown
    print("👋 Shutting down...")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # B2B Lead Generation API

    A GDPR-compliant API for B2B lead generation through legal web scraping.

    ## Features

    - 🔍 **Multi-source scraping** from public directories (PagesJaunes, Kompass, Societe.com)
    - ✉️ **Email verification** with DNS MX and SMTP validation
    - 🌍 **Geographic filtering** with PostGIS
    - 📊 **Quality scoring** for lead confidence
    - 🔒 **GDPR compliant** with consent management
    - 📤 **Export** to CSV/JSON
    - 🔌 **Webhook integration** for CRMs

    ## Legal Compliance

    ⚠️ **IMPORTANT**: This API strictly follows legal scraping practices:

    - ❌ **LinkedIn scraping is FORBIDDEN** (TOS + legal risks)
    - ✅ All sources respect `robots.txt`
    - ✅ Rate limiting enforced
    - ✅ GDPR compliant (consent, opt-out, data minimization)
    - ✅ Data retention: 3 years maximum

    ## Authentication

    All endpoints require authentication via `X-API-Key` header.

    ## Rate Limits

    - 1000 requests/day per API key
    - 100 requests/hour per API key
    """,
    openapi_tags=[
        {
            "name": "Search",
            "description": "Create and manage lead search jobs",
        },
        {
            "name": "Scrapes",
            "description": "Track scraping job progress",
        },
        {
            "name": "Leads",
            "description": "Retrieve and filter leads",
        },
        {
            "name": "GDPR Consents",
            "description": "Manage consents and opt-outs (GDPR compliance)",
        },
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "error": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns API status and version.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Include API v1 router
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint.
    Provides basic information and navigation.
    """
    return {
        "message": "B2B Lead Generation API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX.rstrip('/')}/docs",
        "legal_notice": {
            "linkedin_scraping": "STRICTLY FORBIDDEN",
            "gdpr_compliant": True,
            "robots_txt_respected": True,
            "data_retention_days": settings.DATA_RETENTION_DAYS,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
