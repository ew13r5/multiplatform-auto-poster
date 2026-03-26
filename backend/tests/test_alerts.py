import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from app.alerts.alert_manager import (
    send_alert, format_alert_message, EMPTY_QUEUE, ERROR_SPIKE,
)


def test_format_alert_message():
    msg = format_alert_message("empty_queue", "No posts", "warning", "Test Page")
    assert "WARNING" in msg
    assert "Empty Queue" in msg
    assert "Test Page" in msg
    assert "No posts" in msg


@patch("app.alerts.alert_manager._get_redis")
def test_send_alert_dedup(mock_redis):
    mock_r = MagicMock()
    mock_r.exists.return_value = True  # Already sent
    mock_redis.return_value = mock_r
    result = send_alert(EMPTY_QUEUE, "No posts", "page1", "warning")
    assert result is False  # Deduplicated


@patch("app.alerts.alert_manager._get_redis")
def test_send_alert_new(mock_redis):
    mock_r = MagicMock()
    mock_r.exists.return_value = False
    mock_r.get.return_value = None  # No config
    mock_redis.return_value = mock_r
    result = send_alert(EMPTY_QUEUE, "No posts", "page1", "warning")
    assert result is True
    mock_r.setex.assert_called_once()  # Dedup key set


@pytest.mark.asyncio
async def test_alert_log_endpoint(auth_client: AsyncClient):
    response = await auth_client.get("/api/alerts/log")
    assert response.status_code == 200
    data = response.json()
    assert data["entries"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_alert_config_endpoint(auth_client: AsyncClient):
    response = await auth_client.get("/api/alerts/config")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_acknowledge_not_found(auth_client: AsyncClient):
    response = await auth_client.post("/api/alerts/nonexistent-id/acknowledge")
    assert response.status_code == 404
