import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.models.post import Post, PostType
from app.models.page import Page
from app.services.encryption import decrypt_token
from app.services.error_classifier import GraphAPIError, classify_error
from app.services.graph_api_client import graph_api_request
from app.services.storage import get_presigned_url

logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    """Result of publishing a post to Facebook."""
    success: bool
    fb_post_id: Optional[str] = None
    error: Optional[GraphAPIError] = None


async def publish_post(
    post: Post,
    page: Page,
    client: httpx.AsyncClient,
) -> PublishResult:
    """Publish a post to a Facebook Page via Graph API.

    Supports text, photo (via URL), and link posts.
    Returns PublishResult with success status and fb_post_id or error.
    """
    # Decrypt page access token
    try:
        access_token = decrypt_token(page.access_token_encrypted)
    except Exception as e:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message=f"Token decryption failed: {e}",
                error_type="auth", is_retriable=False, retry_delay_seconds=0,
            ),
        )

    # Determine endpoint and data based on post type
    post_type = post.post_type
    if isinstance(post_type, PostType):
        post_type = post_type.value

    if post_type == "photo" and post.image_key:
        endpoint = f"/{page.fb_page_id}/photos"
        presigned_url = get_presigned_url(post.image_key)
        request_data = {"url": presigned_url, "caption": post.content_text}
    elif post_type == "link" and post.link_url:
        endpoint = f"/{page.fb_page_id}/feed"
        request_data = {"message": post.content_text, "link": post.link_url}
    else:
        endpoint = f"/{page.fb_page_id}/feed"
        request_data = {"message": post.content_text}

    # Make Graph API request
    result = await graph_api_request(
        client=client,
        method="POST",
        endpoint=endpoint,
        access_token=access_token,
        data=request_data,
    )

    if result.success:
        # Photo posts return {"id": "...", "post_id": "..."}
        fb_post_id = result.data.get("post_id") or result.data.get("id")
        return PublishResult(success=True, fb_post_id=fb_post_id)
    else:
        error = classify_error(
            code=result.error_code or 0,
            subcode=result.error_subcode,
            message=result.error_message or "Unknown error",
        )
        return PublishResult(success=False, error=error)
