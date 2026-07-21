"""
Campus Copies ERP - Application Configuration

Uses pydantic-settings to load and validate environment variables.
Grounding: docs/EnvironmentSpecification.md, docs/BackendSpecification.md §11
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application Core
    PROJECT_NAME: str = "Campus Copies ERP"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development, staging, or production")
    LOG_LEVEL: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR, CRITICAL")

    # Security & Tokens
    JWT_SECRET: str = Field(..., description="256-bit secret key for signing JWT tokens")
    JWT_ALGORITHM: str = "HS256"
    STUDENT_TOKEN_EXPIRE_HOURS: int = 24
    ADMIN_TOKEN_EXPIRE_HOURS: int = 8
    ADMIN_SETUP_KEY: str = Field(..., description="One-time setup key for initial admin bootstrap")

    # Database
    DATABASE_URL: str = Field(..., description="Supabase PgBouncer URL (Port 6543) for app queries")
    DATABASE_URL_DIRECT: str = Field(..., description="Direct DB connection URL (Port 5432) for migrations")

    # Supabase Platform & Storage
    SUPABASE_URL: str = Field(..., description="Supabase project API URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase anon public key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., description="Supabase service role key bypassing RLS")
    STORAGE_BUCKET: str = "order-files"
    UPLOAD_LIMIT_MB: int = Field(default=200, description="Max upload size in MB per file")
    SIGNED_URL_EXPIRY: int = Field(default=3600, description="Signed URL validity in seconds (1 hour)")

    # CORS & Deployment
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed origins for CORS requests",
    )
    RENDER_EXTERNAL_URL: str = Field(default="http://localhost:8000", description="Backend public base URL")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            import json
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production"}
        lowered = value.lower()
        if lowered not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{value}'")
        return lowered


# Instantiate global settings singleton
settings = Settings()
