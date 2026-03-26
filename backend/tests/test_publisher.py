import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.publisher import publish_post, PublishResult
from app.services.graph_api_client import GraphAPIResponse
from app.models.post import PostType, PostStatus


def _make_post(post_type="text", image_key=None, link_url=None):
    post = MagicMock()
    post.content_text = "Hello world"
    post.post_type = PostType(post_type)
    post.image_key = image_key
    post.link_url = link_url
    return post


def _make_page():
    page = MagicMock()
    page.fb_page_id = "12345"
    page.access_token_encrypted = "encrypted_token"
    return page


@pytest.mark.asyncio
@patch("app.services.publisher.graph_api_request")
@patch("app.services.publisher.decrypt_token", return_value="real_token")
async def test_text_post_sends_to_feed(mock_decrypt, mock_request):
    mock_request.return_value = GraphAPIResponse(success=True, data={"id": "12345_67890"})
    client = MagicMock()
    result = await publish_post(_make_post("text"), _make_page(), client)

    assert result.success is True
    assert result.fb_post_id == "12345_67890"
    call_args = mock_request.call_args
    assert "/12345/feed" in call_args.kwargs.get("endpoint", call_args[0][2] if len(call_args[0]) > 2 else "")


@pytest.mark.asyncio
@patch("app.services.publisher.get_presigned_url", return_value="http://minio/signed")
@patch("app.services.publisher.graph_api_request")
@patch("app.services.publisher.decrypt_token", return_value="real_token")
async def test_photo_post_uses_caption(mock_decrypt, mock_request, mock_url):
    mock_request.return_value = GraphAPIResponse(success=True, data={"id": "photo1", "post_id": "12345_photo1"})
    client = MagicMock()
    result = await publish_post(_make_post("photo", image_key="img.jpg"), _make_page(), client)

    assert result.success is True
    assert result.fb_post_id == "12345_photo1"  # uses post_id, not id
    call_data = mock_request.call_args.kwargs.get("data", {})
    assert "caption" in call_data
    assert "message" not in call_data


@pytest.mark.asyncio
@patch("app.services.publisher.graph_api_request")
@patch("app.services.publisher.decrypt_token", return_value="real_token")
async def test_link_post_sends_link(mock_decrypt, mock_request):
    mock_request.return_value = GraphAPIResponse(success=True, data={"id": "link_post_1"})
    client = MagicMock()
    result = await publish_post(_make_post("link", link_url="https://example.com"), _make_page(), client)

    assert result.success is True
    call_data = mock_request.call_args.kwargs.get("data", {})
    assert call_data.get("link") == "https://example.com"
    assert "message" in call_data


@pytest.mark.asyncio
@patch("app.services.publisher.graph_api_request")
@patch("app.services.publisher.decrypt_token", return_value="real_token")
async def test_publish_failure(mock_decrypt, mock_request):
    mock_request.return_value = GraphAPIResponse(
        success=False, error_code=190, error_message="Token expired"
    )
    client = MagicMock()
    result = await publish_post(_make_post(), _make_page(), client)

    assert result.success is False
    assert result.error is not None
    assert result.error.error_type == "auth"


@pytest.mark.asyncio
@patch("app.services.publisher.decrypt_token", side_effect=Exception("decrypt failed"))
async def test_decrypt_failure(mock_decrypt):
    client = MagicMock()
    result = await publish_post(_make_post(), _make_page(), client)
    assert result.success is False
    assert result.error.error_type == "auth"
