import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.models.post import Post, PostType
from app.models.page import Page
from app.services.encryption import decrypt_token
from app.services.error_classifier import GraphAPIError
from app.services.storage import get_presigned_url

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


@dataclass
class PublishResult:
    success: bool
    fb_post_id: Optional[str] = None  # reuse field name for message_id
    error: Optional[GraphAPIError] = None


async def publish_post_telegram(
    post: Post,
    page: Page,
    client: httpx.AsyncClient,
) -> PublishResult:
    """Publish a post to a Telegram channel/chat.

    page.access_token_encrypted = encrypted bot token
    page.fb_page_id = chat_id (e.g. @channel_name or -100xxx)
    """
    try:
        bot_token = decrypt_token(page.access_token_encrypted)
    except Exception as e:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message=f"Token decryption failed: {e}",
                error_type="auth", is_retriable=False, retry_delay_seconds=0,
            ),
        )

    chat_id = page.fb_page_id
    post_type = post.post_type
    if isinstance(post_type, PostType):
        post_type = post_type.value

    try:
        if post_type == "photo" and post.image_key:
            photo_url = get_presigned_url(post.image_key)
            resp = await client.post(
                f"{TELEGRAM_API}/bot{bot_token}/sendPhoto",
                json={"chat_id": chat_id, "photo": photo_url, "caption": post.content_text},
                timeout=30.0,
            )
        else:
            text = post.content_text
            if post_type == "link" and post.link_url:
                text = f"{post.content_text}\n\n{post.link_url}"
            resp = await client.post(
                f"{TELEGRAM_API}/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=30.0,
            )

        data = resp.json()

        if data.get("ok"):
            message_id = str(data["result"]["message_id"])
            return PublishResult(success=True, fb_post_id=message_id)
        else:
            error_code = data.get("error_code", 0)
            description = data.get("description", "Unknown Telegram error")

            is_retriable = error_code == 429  # Too Many Requests
            retry_delay = 0
            if is_retriable:
                retry_delay = data.get("parameters", {}).get("retry_after", 30)

            return PublishResult(
                success=False,
                error=GraphAPIError(
                    code=error_code, subcode=None, message=description,
                    error_type="rate_limit" if is_retriable else "other",
                    is_retriable=is_retriable, retry_delay_seconds=retry_delay,
                ),
            )

    except httpx.TimeoutException:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message="Telegram request timed out",
                error_type="network", is_retriable=True, retry_delay_seconds=30,
            ),
        )
    except Exception as e:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message=str(e),
                error_type="network", is_retriable=True, retry_delay_seconds=30,
            ),
        )
