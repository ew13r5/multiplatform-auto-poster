import pytest
from unittest.mock import MagicMock, patch
from app.services.engagement_fetcher import fetch_engagement, EngagementData
from app.services.graph_api_client import GraphAPIResponse
from pydantic import ValidationError
from app.schemas.analytics import HeatmapCell


@pytest.mark.asyncio
@patch("app.services.engagement_fetcher.graph_api_request")
async def test_fetch_engagement_parses_data(mock_request):
    mock_request.return_value = GraphAPIResponse(success=True, data={
        "likes": {"summary": {"total_count": 42}},
        "comments": {"summary": {"total_count": 5}},
        "shares": {"count": 3},
    })
    client = MagicMock()
    result = await fetch_engagement("post123", "token", client)
    assert result is not None
    assert result.likes == 42
    assert result.comments == 5
    assert result.shares == 3
    assert result.fetched_at is not None


@pytest.mark.asyncio
@patch("app.services.engagement_fetcher.graph_api_request")
async def test_fetch_engagement_missing_shares(mock_request):
    mock_request.return_value = GraphAPIResponse(success=True, data={
        "likes": {"summary": {"total_count": 10}},
        "comments": {"summary": {"total_count": 2}},
    })
    client = MagicMock()
    result = await fetch_engagement("post123", "token", client)
    assert result.shares == 0


@pytest.mark.asyncio
@patch("app.services.engagement_fetcher.graph_api_request")
async def test_fetch_engagement_error(mock_request):
    mock_request.return_value = GraphAPIResponse(success=False, error_message="Error")
    client = MagicMock()
    result = await fetch_engagement("post123", "token", client)
    assert result is None


def test_heatmap_cell_validates_day():
    HeatmapCell(day=0, hour=0, avg_engagement=5.0)
    HeatmapCell(day=6, hour=23, avg_engagement=10.0)
    with pytest.raises(ValidationError):
        HeatmapCell(day=7, hour=0, avg_engagement=0)
    with pytest.raises(ValidationError):
        HeatmapCell(day=0, hour=24, avg_engagement=0)
