import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_connect_page(auth_client: AsyncClient):
    response = await auth_client.post("/api/pages/connect", json={
        "fb_page_id": "123456",
        "name": "Test Page",
        "access_token": "secret-token-value",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["fb_page_id"] == "123456"
    assert data["name"] == "Test Page"
    assert data["token_status"] == "configured"
    assert "access_token" not in data  # token must NOT be in response


@pytest.mark.asyncio
async def test_list_pages_empty(auth_client: AsyncClient):
    response = await auth_client.get("/api/pages")
    assert response.status_code == 200
    assert response.json()["pages"] == []


@pytest.mark.asyncio
async def test_list_pages_with_data(auth_client: AsyncClient):
    await auth_client.post("/api/pages/connect", json={
        "fb_page_id": "p1", "name": "Page 1", "access_token": "tok1",
    })
    response = await auth_client.get("/api/pages")
    assert response.status_code == 200
    pages = response.json()["pages"]
    assert len(pages) == 1
    assert pages[0]["queued_count"] == 0


@pytest.mark.asyncio
async def test_verify_token_returns_501(auth_client: AsyncClient):
    response = await auth_client.post("/api/pages/some-id/verify-token")
    assert response.status_code == 501
