import hashlib
import hmac
import json
import logging
import secrets
import time
import urllib.parse
from dataclasses import dataclass
from typing import Optional

import httpx

from app.models.post import Post, PostType
from app.models.page import Page
from app.services.encryption import decrypt_token
from app.services.error_classifier import GraphAPIError

logger = logging.getLogger(__name__)

TWITTER_API = "https://api.twitter.com"


@dataclass
class PublishResult:
    success: bool
    fb_post_id: Optional[str] = None
    error: Optional[GraphAPIError] = None


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def _build_oauth_signature(
    method: str,
    url: str,
    params: dict,
    consumer_secret: str,
    token_secret: str,
) -> str:
    """Build OAuth 1.0a HMAC-SHA1 signature."""
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(params.items())
    )
    base_string = f"{method.upper()}&{_percent_encode(url)}&{_percent_encode(sorted_params)}"
    signing_key = f"{_percent_encode(consumer_secret)}&{_percent_encode(token_secret)}"
    signature = hmac.new(
        signing_key.encode(), base_string.encode(), hashlib.sha1
    ).digest()
    import base64
    return base64.b64encode(signature).decode()


def _build_auth_header(
    method: str,
    url: str,
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
) -> str:
    """Build OAuth 1.0a Authorization header for Twitter API."""
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    sig_params = dict(oauth_params)
    signature = _build_oauth_signature(method, url, sig_params, consumer_secret, access_token_secret)
    oauth_params["oauth_signature"] = signature

    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


async def publish_post_twitter(
    post: Post,
    page: Page,
    client: httpx.AsyncClient,
) -> PublishResult:
    """Publish a post to Twitter/X via API v2.

    page.access_token_encrypted = encrypted JSON:
      {"api_key": "...", "api_secret": "...", "access_token": "...", "access_token_secret": "..."}
    page.fb_page_id = twitter username (for display only)
    """
    try:
        creds_json = decrypt_token(page.access_token_encrypted)
        creds = json.loads(creds_json)
    except Exception as e:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message=f"Credentials parse failed: {e}",
                error_type="auth", is_retriable=False, retry_delay_seconds=0,
            ),
        )

    api_key = creds.get("api_key", "")
    api_secret = creds.get("api_secret", "")
    access_token = creds.get("access_token", "")
    access_token_secret = creds.get("access_token_secret", "")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message="Missing Twitter credentials",
                error_type="auth", is_retriable=False, retry_delay_seconds=0,
            ),
        )

    # Build tweet text
    text = post.content_text
    if post.post_type == PostType.link and post.link_url:
        text = f"{post.content_text}\n{post.link_url}"

    # Truncate to 280 chars
    if len(text) > 280:
        text = text[:277] + "..."

    url = f"{TWITTER_API}/2/tweets"

    try:
        auth_header = _build_auth_header(
            "POST", url, api_key, api_secret, access_token, access_token_secret
        )

        resp = await client.post(
            url,
            json={"text": text},
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            tweet_id = data.get("data", {}).get("id", "")
            return PublishResult(success=True, fb_post_id=tweet_id)

        # Handle errors
        error_data = resp.json() if resp.headers.get("content-type", "").startswith("application/") else {}
        detail = error_data.get("detail", "") or error_data.get("title", "") or resp.text[:200]
        error_code = resp.status_code

        is_retriable = error_code == 429
        retry_delay = 0
        if is_retriable:
            retry_after = resp.headers.get("retry-after", "60")
            retry_delay = int(retry_after) if retry_after.isdigit() else 60

        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=error_code, subcode=None, message=detail,
                error_type="rate_limit" if is_retriable else ("auth" if error_code == 401 else "other"),
                is_retriable=is_retriable, retry_delay_seconds=retry_delay,
            ),
        )

    except httpx.TimeoutException:
        return PublishResult(
            success=False,
            error=GraphAPIError(
                code=0, subcode=None, message="Twitter request timed out",
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
