import logging
import pytest
import httpx
import respx

from app.services.graph_api_client import graph_api_request, GraphAPIResponse


@pytest.fixture
def mock_client():
    """Create httpx AsyncClient with mocked transport."""
    return httpx.AsyncClient(base_url="https://graph.facebook.com/v25.0")


@pytest.mark.asyncio
@respx.mock
async def test_request_sends_correct_url(mock_client):
    route = respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(200, json={"id": "123"})
    )
    result = await graph_api_request(mock_client, "GET", "/me", "tok123")
    assert route.called
    assert result.success is True


@pytest.mark.asyncio
@respx.mock
async def test_request_includes_access_token(mock_client):
    route = respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(200, json={"id": "123"})
    )
    await graph_api_request(mock_client, "GET", "/me", "test_token")
    assert "access_token=test_token" in str(route.calls[0].request.url)


@pytest.mark.asyncio
@respx.mock
async def test_success_response(mock_client):
    respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(200, json={"id": "123", "name": "Test"})
    )
    result = await graph_api_request(mock_client, "GET", "/me", "tok")
    assert result.success is True
    assert result.data == {"id": "123", "name": "Test"}


@pytest.mark.asyncio
@respx.mock
async def test_error_response_parsing(mock_client):
    respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(400, json={
            "error": {"message": "Invalid token", "type": "OAuthException", "code": 190}
        })
    )
    result = await graph_api_request(mock_client, "GET", "/me", "bad_tok")
    assert result.success is False
    assert result.error_code == 190
    assert result.error_type == "OAuthException"


@pytest.mark.asyncio
@respx.mock
async def test_error_extracts_subcode(mock_client):
    respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(400, json={
            "error": {"message": "Expired", "code": 190, "error_subcode": 463, "type": "OAuthException"}
        })
    )
    result = await graph_api_request(mock_client, "GET", "/me", "tok")
    assert result.error_code == 190
    assert result.error_subcode == 463


@pytest.mark.asyncio
@respx.mock
async def test_app_usage_warning(mock_client, caplog):
    respx.get("https://graph.facebook.com/v25.0/me").mock(
        return_value=httpx.Response(
            200,
            json={"id": "1"},
            headers={"X-App-Usage": '{"call_count": 85, "total_cputime": 10, "total_time": 10}'},
        )
    )
    with caplog.at_level(logging.WARNING):
        await graph_api_request(mock_client, "GET", "/me", "tok")
    assert "usage high" in caplog.text.lower()


@pytest.mark.asyncio
@respx.mock
async def test_timeout_handling(mock_client):
    respx.get("https://graph.facebook.com/v25.0/me").mock(side_effect=httpx.ReadTimeout("timed out"))
    result = await graph_api_request(mock_client, "GET", "/me", "tok")
    assert result.success is False
    assert "timed out" in result.error_message.lower()
    assert result.is_retriable is True


@pytest.mark.asyncio
@respx.mock
async def test_connect_error_handling(mock_client):
    respx.get("https://graph.facebook.com/v25.0/me").mock(side_effect=httpx.ConnectError("refused"))
    result = await graph_api_request(mock_client, "GET", "/me", "tok")
    assert result.success is False
    assert result.is_retriable is True
