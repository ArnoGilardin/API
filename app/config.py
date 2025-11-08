"""
Application configuration settings.
Loads from environment variables with sensible defaults.
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "B2B Lead Generation API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY: str = "your-api-key-here"

    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "leadgen"
    POSTGRES_PASSWORD: str = "leadgen_password"
    POSTGRES_DB: str = "leadgen_db"
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Construct database URL from components."""
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}:"
            f"{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Scraping Settings
    USER_AGENT: str = "LeadGenBot/1.0 (+https://yourapi.com/bot)"
    CONCURRENT_REQUESTS: int = 2
    DOWNLOAD_DELAY: int = 2
    RANDOMIZE_DOWNLOAD_DELAY: bool = True
    RESPECT_ROBOTS_TXT: bool = True
    PROXY_LIST: str = ""

    @property
    def proxies(self) -> List[str]:
        """Parse proxy list from comma-separated string."""
        if not self.PROXY_LIST:
            return []
        return [p.strip() for p in self.PROXY_LIST.split(",") if p.strip()]

    # Email Verification
    SMTP_TIMEOUT: int = 10
    SMTP_VERIFY_ENABLED: bool = True
    EMAIL_VERIFICATION_FROM: str = "verify@yourapi.com"

    # Rate Limiting
    RATE_LIMIT_PER_DAY: int = 1000
    RATE_LIMIT_PER_HOUR: int = 100

    # GDPR Settings
    DATA_RETENTION_DAYS: int = 1095  # 3 years
    AUTO_DELETE_ENABLED: bool = True

    # Export Settings
    MAX_EXPORT_RECORDS: int = 10000

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
