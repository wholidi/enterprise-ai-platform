"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EAP_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Enterprise AI Platform API"
    environment: str = "local"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
