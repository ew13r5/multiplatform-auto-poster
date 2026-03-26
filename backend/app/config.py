import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    DATABASE_URL_SYNC: str = "sqlite:///:memory:"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "post-images"
    MINIO_USE_SSL: bool = False
    MINIO_EXTERNAL_ENDPOINT: str = "localhost:9000"

    # Security
    FERNET_KEYS: str = ""
    API_KEY: str = "dev-api-key"

    # Facebook
    APP_ID: str = ""
    APP_SECRET: str = ""
    GRAPH_API_VERSION: str = "v25.0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
