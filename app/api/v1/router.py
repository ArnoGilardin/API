"""
API v1 router aggregation.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import search, scrapes, leads, consents

# Create main v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    search.router,
    tags=["Search"],
)

api_router.include_router(
    scrapes.router,
    tags=["Scrapes"],
)

api_router.include_router(
    leads.router,
    tags=["Leads"],
)

api_router.include_router(
    consents.router,
    tags=["GDPR Consents"],
)
