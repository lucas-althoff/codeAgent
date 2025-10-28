"""Configuration module for the Code Agent application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    postgres_url: str = "postgresql://mirante:mirante2025pass@localhost:5434/codeAgent?sslmode=disable"

    # Redis (for future caching)
    redis_url: str = "redis://localhost:6382"

    # API Settings
    api_title: str = "Mirante - Code Agent"
    api_description: str = "Agent module that provides code optimization suggestions based on Python best practices"
    api_version: str = "1.0.0"

    # CrewAI Settings
    openai_api_key: str = ""  # Set via environment variable

    # Application Settings
    debug: bool = False


# Global settings instance
settings = Settings()
