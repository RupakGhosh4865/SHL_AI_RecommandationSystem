"""
Configuration Settings
Loads from environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # ✅ this allows unknown env vars like API_URL etc.
    )

    APP_NAME: str = Field(default="SHL Assessment Recommender API")
    VERSION: str = Field(default="1.0.0")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    GEMINI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None

    DATA_PATH: str = "../data/processed/shl_catalog_enriched.csv"
    EMBEDDINGS_PATH: str = "../data/embeddings/"
    LOGS_PATH: str = "../logs/"

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8080",
        "https://*.streamlit.app",
        "https://*.onrender.com",
    ]

    MAX_RECOMMENDATIONS: int = 10
    MIN_RECOMMENDATIONS: int = 1
    DEFAULT_RECOMMENDATIONS: int = 10
    RATE_LIMIT_PER_MINUTE: int = 60


settings = Settings()
