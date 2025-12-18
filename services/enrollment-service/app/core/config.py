"""Configuration settings for Enrollment Service."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Enrollment Service"
    SERVICE_NAME: str = "enrollment-service"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://enrollment_user:enrollment_password@localhost:5432/enrollment_service_db"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Redis
    REDIS_URL: str = "redis://localhost:6379/2"
    REDIS_DECODE_RESPONSES: bool = True

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ]

    # External Services
    USER_SERVICE_URL: str = "http://localhost:8001"
    COURSE_SERVICE_URL: str = "http://localhost:8002"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="allow"
    )


settings = Settings()
