"""Configuration settings for Payment Service."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Payment Service"
    SERVICE_NAME: str = "payment-service"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://payment_user:payment_password@localhost:5432/payment_service_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
    ]

    # External Services
    USER_SERVICE_URL: str = "http://localhost:8001"
    COURSE_SERVICE_URL: str = "http://localhost:8002"
    ENROLLMENT_SERVICE_URL: str = "http://localhost:8003"

    # Payment Gateway (Stripe mock)
    STRIPE_SECRET_KEY: str = "sk_test_mock_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_mock_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_test_mock_secret"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")


settings = Settings()
