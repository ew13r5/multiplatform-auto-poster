import pytest
from unittest.mock import patch, MagicMock
from app.tasks.celery_app import celery_app


def test_beat_schedule_has_check_publish_slots():
    assert "check-publish-slots" in celery_app.conf.beat_schedule
    assert celery_app.conf.beat_schedule["check-publish-slots"]["schedule"] == 60.0


def test_beat_schedule_has_heartbeat():
    assert "update-heartbeat" in celery_app.conf.beat_schedule


def test_beat_schedule_has_daily_report():
    assert "daily-report" in celery_app.conf.beat_schedule


def test_beat_schedule_has_token_check():
    assert "check-token-health" in celery_app.conf.beat_schedule


@pytest.mark.asyncio
async def test_log_endpoint_empty(auth_client):
    response = await auth_client.get("/api/log")
    assert response.status_code == 200
    data = response.json()
    assert data["entries"] == []
    assert data["total"] == 0
