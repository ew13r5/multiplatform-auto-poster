import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.token_manager import (
    exchange_short_to_long, get_page_tokens, verify_token, check_token_health,
    TokenExchangeResult, PageTokenInfo, TokenVerification, TokenHealthStatus,
)
from app.services.graph_api_client import GraphAPIResponse


@pytest.mark.asyncio
@patch("app.services.token_manager.graph_api_request")
@patch("app.services.token_manager.get_settings")
async def test_exchange_short_to_long(mock_settings, mock_request):
    mock_settings.return_value.APP_ID = "app123"
    mock_settings.return_value.APP_SECRET = "secret"
    mock_request.return_value = GraphAPIResponse(
        success=True, data={"access_token": "long_token", "token_type": "bearer", "expires_in": 5184000}
    )
    client = MagicMock()
    result = await exchange_short_to_long("short_tok", client)
    assert result.access_token == "long_token"
    assert result.expires_in == 5184000


@pytest.mark.asyncio
@patch("app.services.token_manager.graph_api_request")
async def test_get_page_tokens(mock_request):
    mock_request.return_value = GraphAPIResponse(
        success=True, data={"data": [
            {"id": "p1", "name": "Page 1", "access_token": "tok1"},
            {"id": "p2", "name": "Page 2", "access_token": "tok2"},
        ]}
    )
    client = MagicMock()
    pages = await get_page_tokens("long_tok", client)
    assert len(pages) == 2
    assert pages[0].page_id == "p1"
    assert pages[1].page_name == "Page 2"


@pytest.mark.asyncio
@patch("app.services.token_manager.graph_api_request")
@patch("app.services.token_manager.get_settings")
async def test_verify_token_valid(mock_settings, mock_request):
    mock_settings.return_value.APP_ID = "app123"
    mock_settings.return_value.APP_SECRET = "secret"
    mock_request.return_value = GraphAPIResponse(
        success=True, data={"data": {
            "is_valid": True, "expires_at": int(time.time()) + 86400,
            "scopes": ["pages_manage_posts", "pages_read_engagement"], "user_id": "u1"
        }}
    )
    client = MagicMock()
    result = await verify_token("tok", client)
    assert result.is_valid is True
    assert len(result.scopes) == 2


@pytest.mark.asyncio
@patch("app.services.token_manager.graph_api_request")
@patch("app.services.token_manager.get_settings")
async def test_verify_token_invalid(mock_settings, mock_request):
    mock_settings.return_value.APP_ID = "app123"
    mock_settings.return_value.APP_SECRET = "secret"
    mock_request.return_value = GraphAPIResponse(
        success=True, data={"data": {"is_valid": False, "error": {"message": "Token expired"}}}
    )
    client = MagicMock()
    result = await verify_token("bad_tok", client)
    assert result.is_valid is False


@pytest.mark.asyncio
@patch("app.services.token_manager.verify_token")
@patch("app.services.token_manager.decrypt_token", return_value="decrypted_tok")
async def test_check_health_healthy(mock_decrypt, mock_verify):
    mock_verify.return_value = TokenVerification(
        is_valid=True, expires_at=int(time.time()) + 30 * 86400,
        scopes=["pages_manage_posts", "pages_read_engagement"], user_id="u1"
    )
    page = MagicMock()
    page.access_token_encrypted = "encrypted"
    client = MagicMock()
    status = await check_token_health(page, client)
    assert status.is_healthy is True
    assert status.is_valid is True


@pytest.mark.asyncio
@patch("app.services.token_manager.verify_token")
@patch("app.services.token_manager.decrypt_token", return_value="decrypted_tok")
async def test_check_health_expires_soon(mock_decrypt, mock_verify):
    mock_verify.return_value = TokenVerification(
        is_valid=True, expires_at=int(time.time()) + 3 * 86400,  # 3 days
        scopes=["pages_manage_posts", "pages_read_engagement"],
    )
    page = MagicMock()
    page.access_token_encrypted = "encrypted"
    client = MagicMock()
    status = await check_token_health(page, client)
    assert status.expires_soon is True
    assert status.is_healthy is False


@pytest.mark.asyncio
@patch("app.services.token_manager.verify_token")
@patch("app.services.token_manager.decrypt_token", return_value="decrypted_tok")
async def test_check_health_missing_scopes(mock_decrypt, mock_verify):
    mock_verify.return_value = TokenVerification(
        is_valid=True, expires_at=int(time.time()) + 30 * 86400,
        scopes=["pages_manage_posts"],  # missing pages_read_engagement
    )
    page = MagicMock()
    page.access_token_encrypted = "encrypted"
    client = MagicMock()
    status = await check_token_health(page, client)
    assert "pages_read_engagement" in status.missing_scopes
    assert status.is_healthy is False
