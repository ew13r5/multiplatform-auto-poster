import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx

from app.services.graph_api_client import graph_api_request

logger = logging.getLogger(__name__)


@dataclass
class EngagementData:
    likes: int
    comments: int
    shares: int
    fetched_at: datetime


async def fetch_engagement(
    fb_post_id: str,
    access_token: str,
    client: httpx.AsyncClient,
) -> Optional[EngagementData]:
    """Fetch likes, comments, shares for a post from Graph API.

    Returns EngagementData on success, None on error.
    """
    result = await graph_api_request(
        client=client,
        method="GET",
        endpoint=f"/{fb_post_id}",
        access_token=access_token,
        params={"fields": "likes.summary(true),comments.summary(true),shares"},
    )

    if not result.success:
        logger.warning("Failed to fetch engagement for %s: %s", fb_post_id, result.error_message)
        return None

    data = result.data or {}
    likes = data.get("likes", {}).get("summary", {}).get("total_count", 0)
    comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
    shares = data.get("shares", {}).get("count", 0)

    return EngagementData(
        likes=likes,
        comments=comments,
        shares=shares,
        fetched_at=datetime.utcnow(),
    )
