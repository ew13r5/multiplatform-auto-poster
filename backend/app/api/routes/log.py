from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.publish_log import PublishLog
from app.models.post import Post
from app.models.page import Page
from app.schemas.log import PublishLogEntry, PublishLogResponse

router = APIRouter(tags=["log"])


@router.get("/log", response_model=PublishLogResponse)
async def get_publish_log(
    page_id: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """Get publishing log with filters."""
    query = (
        select(
            PublishLog.attempted_at,
            PublishLog.result,
            PublishLog.fb_post_id,
            PublishLog.error_code,
            PublishLog.error_message,
            PublishLog.retry_count,
            Post.content_text,
            Page.name.label("page_name"),
        )
        .join(Post, PublishLog.post_id == Post.id)
        .join(Page, PublishLog.page_id == Page.id)
    )

    count_query = (
        select(func.count(PublishLog.id))
        .join(Post, PublishLog.post_id == Post.id)
    )

    if page_id:
        query = query.where(PublishLog.page_id == page_id)
        count_query = count_query.where(PublishLog.page_id == page_id)
    if status:
        query = query.where(PublishLog.result == status)
        count_query = count_query.where(PublishLog.result == status)
    if date_from:
        query = query.where(PublishLog.attempted_at >= datetime.combine(date_from, datetime.min.time()))
        count_query = count_query.where(PublishLog.attempted_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(PublishLog.attempted_at <= datetime.combine(date_to, datetime.max.time()))
        count_query = count_query.where(PublishLog.attempted_at <= datetime.combine(date_to, datetime.max.time()))

    query = query.order_by(PublishLog.attempted_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    rows = result.all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    entries = [
        PublishLogEntry(
            attempted_at=row.attempted_at,
            page_name=row.page_name,
            content_preview=row.content_text[:80] if row.content_text else "",
            result=row.result.value if hasattr(row.result, 'value') else str(row.result),
            fb_post_id=row.fb_post_id,
            error_code=row.error_code,
            error_message=row.error_message,
            retry_count=row.retry_count,
        )
        for row in rows
    ]

    return PublishLogResponse(entries=entries, total=total)
