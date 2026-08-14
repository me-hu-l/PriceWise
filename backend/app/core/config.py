from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, sourced from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./pricewise.db"

    llm_provider: str = "mock"
    llm_api_key: str = ""

    market_data_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]

    # Low-data mode thresholds (roadmap section 10), configurable per-deployment.
    low_data_max_observations: int = 12
    limited_data_max_observations: int = 24
    moderate_data_max_observations: int = 48

    # Confidence formula weights (roadmap section 13), must sum to 1.0.
    confidence_weight_data: float = 0.20
    confidence_weight_driver: float = 0.25
    confidence_weight_model: float = 0.25
    confidence_weight_market: float = 0.15
    confidence_weight_stability: float = 0.15


@lru_cache
def get_settings() -> Settings:
    return Settings()
