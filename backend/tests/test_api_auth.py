import os
import pytest
from unittest.mock import patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_accessible_without_key(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_api_key_returns_401(client: AsyncClient):
    response = await client.get("/api/pages")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_api_key_returns_401(client: AsyncClient):
    response = await client.get(
        "/api/pages", headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_valid_api_key_returns_not_401(client: AsyncClient):
    with patch.dict(os.environ, {"API_KEY": "test-key-123"}):
        from app.config import get_settings
        get_settings.cache_clear()
        response = await client.get(
            "/api/pages", headers={"X-API-Key": "test-key-123"}
        )
        # Should not be 401 (may be 404 or 200 since stub router has no endpoints)
        assert response.status_code != 401
        get_settings.cache_clear()
