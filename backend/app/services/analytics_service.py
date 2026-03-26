from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostStatus
from app.models.page import Page
from app.models.engagement import Engagement


@dataclass
class PostEngagement:
    post_id: str
    content_preview: str
    page_name: str
    likes: int
    comments: int
    shares: int
    published_at: Optional[datetime]


@dataclass
class HeatmapCell:
    day: int
    hour: int
    avg_engagement: float


async def get_engagement_data(
    db: AsyncSession,
    page_id: Optional[str] = None,
    days: int = 30,
    limit: int = 20,
) -> List[PostEngagement]:
    """Get top posts by engagement, optionally filtered by page."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            Post.id,
            Post.content_text,
            Post.published_at,
            Post.page_id,
            Page.name.label("page_name"),
            func.coalesce(Engagement.likes, 0).label("likes"),
            func.coalesce(Engagement.comments, 0).label("comments"),
            func.coalesce(Engagement.shares, 0).label("shares"),
        )
        .outerjoin(Engagement, Post.id == Engagement.post_id)
        .join(Page, Post.page_id == Page.id)
        .where(Post.status == PostStatus.published)
        .where(Post.published_at >= cutoff)
    )

    if page_id:
        query = query.where(Post.page_id == page_id)

    query = query.order_by(
        (func.coalesce(Engagement.likes, 0) +
         func.coalesce(Engagement.comments, 0) +
         func.coalesce(Engagement.shares, 0)).desc()
    ).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return [
        PostEngagement(
            post_id=str(row.id),
            content_preview=row.content_text[:100],
            page_name=row.page_name,
            likes=row.likes,
            comments=row.comments,
            shares=row.shares,
            published_at=row.published_at,
        )
        for row in rows
    ]


async def get_best_time_data(
    db: AsyncSession,
    page_id: Optional[str] = None,
) -> List[HeatmapCell]:
    """Get average engagement by day_of_week x hour_of_day."""
    # SQLite uses strftime, PostgreSQL uses EXTRACT
    # For compatibility, use a simpler approach
    query = (
        select(Post, Engagement)
        .outerjoin(Engagement, Post.id == Engagement.post_id)
        .where(Post.status == PostStatus.published)
        .where(Post.published_at.isnot(None))
    )
    if page_id:
        query = query.where(Post.page_id == page_id)

    result = await db.execute(query)
    rows = result.all()

    # Aggregate in Python for DB compatibility
    cells = {}
    for post, engagement in rows:
        if not post.published_at:
            continue
        day = post.published_at.weekday()  # 0=Mon, 6=Sun
        hour = post.published_at.hour
        key = (day, hour)
        total = (
            (engagement.likes if engagement else 0) +
            (engagement.comments if engagement else 0) +
            (engagement.shares if engagement else 0)
        )
        if key not in cells:
            cells[key] = {"total": 0, "count": 0}
        cells[key]["total"] += total
        cells[key]["count"] += 1

    return [
        HeatmapCell(
            day=day,
            hour=hour,
            avg_engagement=data["total"] / data["count"] if data["count"] > 0 else 0,
        )
        for (day, hour), data in sorted(cells.items())
    ]
