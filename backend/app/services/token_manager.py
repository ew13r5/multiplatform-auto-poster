import time
from dataclasses import dataclass, field
from typing import Optional, List

import httpx

from app.config import get_settings
from app.services.encryption import decrypt_token
from app.services.graph_api_client import graph_api_request

REQUIRED_SCOPES = {"pages_manage_posts", "pages_read_engagement"}


@dataclass
class TokenExchangeResult:
    access_token: str
    token_type: str
    expires_in: int


@dataclass
class PageTokenInfo:
    page_id: str
    page_name: str
    access_token: str


@dataclass
class TokenVerification:
    is_valid: bool
    expires_at: Optional[int] = None
    scopes: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class TokenHealthStatus:
    is_healthy: bool
    is_valid: bool
    expires_soon: bool = False
    missing_scopes: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


def _mask_token(token: str) -> str:
    if len(token) <= 10:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


async def exchange_short_to_long(short_token: str, client: httpx.AsyncClient) -> TokenExchangeResult:
    """Exchange short-lived user token for long-lived (60-day) user token."""
    settings = get_settings()
    result = await graph_api_request(
        client=client,
        method="GET",
        endpoint="/oauth/access_token",
        access_token=short_token,
        params={
            "grant_type": "fb_exchange_token",
            "client_id": settings.APP_ID,
            "client_secret": settings.APP_SECRET,
            "fb_exchange_token": short_token,
        },
    )
    if not result.success:
        raise ValueError(f"Token exchange failed: {result.error_message}")
    return TokenExchangeResult(
        access_token=result.data["access_token"],
        token_type=result.data.get("token_type", "bearer"),
        expires_in=result.data.get("expires_in", 5184000),
    )


async def get_page_tokens(long_lived_user_token: str, client: httpx.AsyncClient) -> List[PageTokenInfo]:
    """Get page tokens from long-lived user token."""
    result = await graph_api_request(
        client=client,
        method="GET",
        endpoint="/me/accounts",
        access_token=long_lived_user_token,
    )
    if not result.success:
        raise ValueError(f"Failed to get page tokens: {result.error_message}")
    pages = []
    for item in result.data.get("data", []):
        pages.append(PageTokenInfo(
            page_id=item["id"],
            page_name=item["name"],
            access_token=item["access_token"],
        ))
    return pages


async def verify_token(token: str, client: httpx.AsyncClient) -> TokenVerification:
    """Verify token validity using debug_token endpoint."""
    settings = get_settings()
    app_token = f"{settings.APP_ID}|{settings.APP_SECRET}"
    result = await graph_api_request(
        client=client,
        method="GET",
        endpoint="/debug_token",
        access_token=app_token,
        params={"input_token": token},
    )
    if not result.success:
        return TokenVerification(
            is_valid=False,
            error_message=result.error_message,
        )
    data = result.data.get("data", {})
    return TokenVerification(
        is_valid=data.get("is_valid", False),
        expires_at=data.get("expires_at"),
        scopes=data.get("scopes", []),
        user_id=data.get("user_id"),
        error_message=data.get("error", {}).get("message") if not data.get("is_valid") else None,
    )


async def check_token_health(page, client: httpx.AsyncClient) -> TokenHealthStatus:
    """Check health of a page's stored access token."""
    if not page.access_token_encrypted:
        return TokenHealthStatus(
            is_healthy=False, is_valid=False,
            error_message="No token stored",
        )

    try:
        token = decrypt_token(page.access_token_encrypted)
    except Exception as e:
        return TokenHealthStatus(
            is_healthy=False, is_valid=False,
            error_message=f"Token decryption failed: {e}",
        )

    verification = await verify_token(token, client)

    if not verification.is_valid:
        return TokenHealthStatus(
            is_healthy=False, is_valid=False,
            error_message=verification.error_message or "Token is invalid",
        )

    # Check required scopes
    missing = list(REQUIRED_SCOPES - set(verification.scopes))

    # Check expiry (7 days warning)
    expires_soon = False
    if verification.expires_at and verification.expires_at > 0:
        seconds_left = verification.expires_at - int(time.time())
        if seconds_left < 7 * 24 * 3600:
            expires_soon = True

    is_healthy = not missing and not expires_soon
    return TokenHealthStatus(
        is_healthy=is_healthy,
        is_valid=True,
        expires_soon=expires_soon,
        missing_scopes=missing,
    )
