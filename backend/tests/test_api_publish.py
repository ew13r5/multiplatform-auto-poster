import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient
from app.services.publisher import PublishResult
from app.services.error_classifier import GraphAPIError


async def _create_page_and_post(client: AsyncClient, status="queued"):
    page_resp = await client.post("/api/pages/connect", json={
        "fb_page_id": "pub_page", "name": "Pub Page", "access_token": "tok",
    })
    page_id = page_resp.json()["id"]
    post_resp = await client.post("/api/posts", json={
        "page_id": page_id, "content_text": "Publish me",
    })
    post_id = post_resp.json()["id"]
    if status == "queued":
        await client.put(f"/api/posts/{post_id}", json={"status": "queued"})
    return page_id, post_id


@pytest.mark.asyncio
@patch("app.api.routes.publish.publish_post")
async def test_publish_now_success(mock_publish, auth_client: AsyncClient):
    mock_publish.return_value = PublishResult(success=True, fb_post_id="fb_123")
    _, post_id = await _create_page_and_post(auth_client)
    response = await auth_client.post(f"/api/posts/{post_id}/publish-now")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["fb_post_id"] == "fb_123"


@pytest.mark.asyncio
async def test_publish_now_not_found(auth_client: AsyncClient):
    response = await auth_client.post("/api/posts/nonexistent-id/publish-now")
    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.api.routes.publish.publish_post")
async def test_publish_now_failure(mock_publish, auth_client: AsyncClient):
    mock_publish.return_value = PublishResult(
        success=False,
        error=GraphAPIError(code=190, subcode=None, message="Token expired",
                           error_type="auth", is_retriable=False, retry_delay_seconds=0),
    )
    _, post_id = await _create_page_and_post(auth_client)
    response = await auth_client.post(f"/api/posts/{post_id}/publish-now")
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


@pytest.mark.asyncio
async def test_analytics_engagement_empty(auth_client: AsyncClient):
    response = await auth_client.get("/api/analytics/engagement")
    assert response.status_code == 200
    assert response.json()["posts"] == []


@pytest.mark.asyncio
async def test_analytics_best_time_empty(auth_client: AsyncClient):
    response = await auth_client.get("/api/analytics/best-time")
    assert response.status_code == 200
    assert response.json()["cells"] == []
