import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Health Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    DATABASE_URL: str = "postgresql://healthintel:healthintel_dev@localhost:5432/healthintel"
    AUTO_MIGRATE: bool = True

    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOW_INSECURE_DEFAULTS: bool = True  # must be false in production

    AGENT_MODEL: str = "openai/gpt-4o"
    AGENT_TEMPERATURE: float = 0.2
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: Optional[str] = None

    SIMULATION_INTERVAL_SECONDS: int = 5

    LOG_LEVEL: str = "INFO"

    CONNECTOR_FHIR_URL: Optional[str] = None
    CONNECTOR_FHIR_AUTH_TYPE: Optional[str] = None
    CONNECTOR_FHIR_TOKEN: Optional[str] = None
    CONNECTOR_DHIS2_URL: Optional[str] = None
    CONNECTOR_DHIS2_USERNAME: Optional[str] = None
    CONNECTOR_DHIS2_PASSWORD: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

    def validate_for_runtime(self):
        """Refuse insecure defaults outside development."""
        if self.ENVIRONMENT == "production" or not self.ALLOW_INSECURE_DEFAULTS:
            if self.SECRET_KEY == "change-this-in-production":
                raise RuntimeError(
                    "SECRET_KEY must be set via environment when ALLOW_INSECURE_DEFAULTS=false "
                    "or ENVIRONMENT=production"
                )
            if self.AUTO_MIGRATE:
                raise RuntimeError(
                    "AUTO_MIGRATE must be false in production — run alembic upgrade head in CI/CD"
                )


settings = Settings()
