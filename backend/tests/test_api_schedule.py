import pytest
from httpx import AsyncClient


async def _create_page(client: AsyncClient) -> str:
    resp = await client.post("/api/pages/connect", json={
        "fb_page_id": "sched_page", "name": "Schedule Page", "access_token": "tok",
    })
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_get_schedule_empty(auth_client: AsyncClient):
    response = await auth_client.get("/api/schedule")
    assert response.status_code == 200
    assert response.json()["slots"] == []


@pytest.mark.asyncio
async def test_update_schedule(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    response = await auth_client.put("/api/schedule", json={
        "slots": [
            {"page_id": page_id, "day_of_week": 1, "time_utc": "14:00", "timezone": "UTC", "enabled": True},
            {"page_id": page_id, "day_of_week": 3, "time_utc": "09:00", "timezone": "UTC", "enabled": True},
        ]
    })
    assert response.status_code == 200
    # Verify slots created
    resp2 = await auth_client.get("/api/schedule")
    assert len(resp2.json()["slots"]) == 2


@pytest.mark.asyncio
async def test_pause_toggle(auth_client: AsyncClient):
    response = await auth_client.post("/api/schedule/pause", json={"paused": True})
    assert response.status_code == 200
    assert response.json()["paused"] is True

    response2 = await auth_client.post("/api/schedule/pause", json={"paused": False})
    assert response2.json()["paused"] is False


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "mode" in data


@pytest.mark.asyncio
async def test_schedule_slot_validates_day(auth_client: AsyncClient):
    """day_of_week must be 0-6."""
    page_id = await _create_page(auth_client)
    response = await auth_client.put("/api/schedule", json={
        "slots": [
            {"page_id": page_id, "day_of_week": 7, "time_utc": "10:00", "timezone": "UTC"},
        ]
    })
    assert response.status_code == 422  # Validation error
