# B2B Lead Generation API - Replit Environment

## Overview

This is a GDPR-compliant B2B Lead Generation API built with FastAPI that allows legal web scraping of public business directories (PagesJaunes, Kompass, Societe.com) for B2B prospecting.

**Version:** 1.0.0  
**Environment:** Replit (Development)  
**Port:** 5000

## Project Architecture

### Technology Stack
- **Backend Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL with PostGIS extension
- **ORM:** SQLAlchemy with GeoAlchemy2
- **Async Task Queue:** Celery (requires Redis - not available in Replit)
- **Web Scraping:** BeautifulSoup4, Requests (Playwright disabled for Replit)
- **Email Verification:** DNSPython, email-validator

### Directory Structure
```
API/
├── app/
│   ├── api/v1/              # API endpoints
│   │   └── endpoints/       # Individual endpoint modules
│   ├── models/              # SQLAlchemy database models
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic (auth, email verification)
│   ├── workers/             # Celery workers (currently not active)
│   ├── config.py            # Application configuration
│   ├── database.py          # Database connection setup
│   └── main.py              # FastAPI application entry point
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── .env                     # Environment variables
└── requirements.txt         # Python dependencies
```

## Features

### Core Functionality
- 🔍 Multi-source lead scraping from public directories
- ✉️ Email verification with DNS MX and SMTP validation
- 🌍 Geographic filtering using PostGIS
- 📊 Lead quality scoring (confidence scores)
- 📤 Export to CSV/JSON formats
- 🔒 GDPR-compliant consent management

### Legal Compliance
- ❌ **LinkedIn scraping FORBIDDEN** (TOS violation)
- ✅ Respects robots.txt
- ✅ Rate limiting enforced
- ✅ GDPR compliant (consent, opt-out, data minimization)
- ✅ Data retention: 3 years maximum

## Recent Changes (Replit Adaptation)

### Date: 2025-11-08

#### Modifications for Replit Environment
1. **Port Configuration:** Changed from port 8000 to port 5000 (required for Replit webview)
2. **Database Setup:** Using Replit's built-in PostgreSQL with PostGIS extension
3. **Simplified Models:** Removed problematic PostGIS indexes that caused conflicts
4. **Dependencies:** Added email-validator package for Pydantic email validation
5. **Removed Index:** Simplified Lead model indexes (removed location and email_verified GIST indexes)

#### Known Limitations in Replit
- **No Redis/Celery:** Async job processing not available (Celery requires Redis)
- **No Playwright:** Browser automation disabled (heavy system requirements)
- **Scraping Jobs:** Will fail when queued (no Celery worker) but API structure remains intact

## API Documentation

### Access Points
- **Swagger UI:** http://localhost:5000/docs
- **ReDoc:** http://localhost:5000/redoc
- **Health Check:** http://localhost:5000/health

### Authentication
All API endpoints require the `X-API-Key` header.

**Development API Key:** `dev-api-key-12345`

Example:
```bash
curl -H "X-API-Key: dev-api-key-12345" http://localhost:5000/health
```

### Main Endpoints

#### 1. Health Check
```
GET /health
```
Returns API status and version.

#### 2. Create Search Job
```
POST /api/v1/search_jobs
```
Creates an asynchronous lead scraping job (Note: will not process without Celery).

#### 3. Get Scrape Status
```
GET /api/v1/scrapes/{job_id}
```
Check the status of a scraping job.

#### 4. Retrieve Leads
```
GET /api/v1/leads/{job_id}
```
Get the leads from a completed job.

#### 5. Export Leads
```
GET /api/v1/leads/{job_id}/export?format=csv
```
Export leads as CSV or JSON.

#### 6. GDPR Consent Management
```
POST /api/v1/consents/revoke
POST /api/v1/consents/delete
```
Manage user consents and data deletion requests.

## Database

### PostgreSQL Setup
- **Extension:** PostGIS (enabled)
- **Connection:** Managed via Replit's DATABASE_URL environment variable

### Main Tables
- `sources` - Data sources for scraping
- `companies` - Company information
- `leads` - Individual lead contacts
- `scrapes` - Scraping job tracking
- `enrichments` - Additional lead data
- `consents` - GDPR consent records
- `logs` - Audit trail

### Database Initialization
The database is automatically initialized on application startup via the lifespan handler in `app/main.py`.

## Environment Variables

Key environment variables (stored in `.env`):

```env
# Application
APP_NAME=B2B Lead Generation API
APP_VERSION=1.0.0
DEBUG=True

# Security
API_KEY=dev-api-key-12345
SECRET_KEY=replit-dev-secret-key-change-in-production-12345

# Database (automatically set by Replit)
DATABASE_URL=<provided by Replit>

# GDPR
DATA_RETENTION_DAYS=1095  # 3 years
AUTO_DELETE_ENABLED=True
```

## Development Workflow

### Running the API
The FastAPI server runs automatically via the configured workflow:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### Testing
Run the test suite:
```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

## Deployment

The project is configured for Replit deployment with:
- **Type:** VM (stateful application)
- **Command:** `uvicorn app.main:app --host 0.0.0.0 --port 5000`

## Security Notes

### Production Checklist
Before deploying to production:
- [ ] Change `API_KEY` to a strong, random key
- [ ] Change `SECRET_KEY` to a 64+ character random string
- [ ] Set `DEBUG=False`
- [ ] Configure CORS properly (don't use `allow_origins=["*"]`)
- [ ] Set up HTTPS
- [ ] Enable database backups
- [ ] Set up monitoring and alerting

## Known Issues & Limitations

1. **Celery Jobs Not Processing:** Scraping jobs will be queued but won't process without Redis/Celery
2. **PostGIS Indexes:** Some advanced geospatial indexes are disabled to avoid conflicts
3. **Playwright Disabled:** Heavy browser automation is not available in this environment

## Support & Documentation

- **Full Documentation:** See README.md
- **Architecture:** See ARCHITECTURE.md
- **Privacy Policy:** See PRIVACY_POLICY.md
- **Contributing:** See CONTRIBUTING.md

## Legal Disclaimer

This API is for legal B2B prospecting only:
- Only scrapes publicly available business information
- Complies with GDPR regulations
- Respects robots.txt and rate limits
- **Strictly forbids LinkedIn scraping**

Users are responsible for:
- Legal compliance in their jurisdiction
- Ethical use of collected data
- Respecting source websites' terms of service

---

**Note:** This is a development environment. The scraping functionality requires external infrastructure (Redis for Celery) not available in Replit. The API structure and endpoints are fully functional for testing and development purposes.
