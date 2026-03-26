import os
import pytest
from app.config import Settings


def test_settings_has_sensible_defaults():
    s = Settings(FERNET_KEYS="test", API_KEY="test")
    assert s.REDIS_URL == "redis://redis:6379/0"
    assert s.MINIO_BUCKET == "post-images"
    assert s.MINIO_USE_SSL is False
    assert s.GRAPH_API_VERSION == "v25.0"
    assert s.CORS_ORIGINS == "http://localhost:3000"
    assert s.MINIO_EXTERNAL_ENDPOINT == "localhost:9000"
