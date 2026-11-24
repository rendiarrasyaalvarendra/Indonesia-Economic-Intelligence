"""
Indonesia Economic Intelligence — Application Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # AI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # BPS
    bps_api_key: str = Field(default="", env="BPS_API_KEY")
    bps_base_url: str = "https://webapi.bps.go.id/v1/api"

    # Bank Indonesia
    bi_api_key: str = Field(default="", env="BI_API_KEY")

    # App
    app_env: str = Field(default="development", env="APP_ENV")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    app_debug: bool = Field(default=True, env="APP_DEBUG")

    # Cache
    data_cache_ttl: int = Field(default=3600, env="DATA_CACHE_TTL")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        env="CORS_ORIGINS",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
