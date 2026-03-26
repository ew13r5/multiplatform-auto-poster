from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.post import Post, PostStatus


async def assign_queue_position(db: AsyncSession, post_id: str, page_id: str) -> int:
    """Assign next order_index to a post being queued. Returns the assigned index."""
    max_result = await db.execute(
        select(func.coalesce(func.max(Post.order_index), 0)).where(
            Post.page_id == page_id
        )
    )
    next_index = (max_result.scalar() or 0) + 1
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one()
    post.order_index = next_index
    return next_index


async def reorder_posts(db: AsyncSession, items: list[dict]) -> None:
    """Bulk update order_index for posts. items: [{id, order_index}]."""
    ids = [item["id"] for item in items]
    result = await db.execute(select(Post).where(Post.id.in_(ids)))
    posts = {str(p.id): p for p in result.scalars().all()}

    if len(posts) != len(ids):
        raise ValueError("Some posts not found")

    page_ids = {p.page_id for p in posts.values()}
    if len(page_ids) > 1:
        raise ValueError("All posts must belong to the same page")

    for p in posts.values():
        if p.status not in (PostStatus.draft, PostStatus.queued):
            raise ValueError(f"Post {p.id} has status '{p.status.value}', cannot reorder")

    for item in items:
        posts[item["id"]].order_index = item["order_index"]


async def get_next_queued_post(db: AsyncSession, page_id: str):
    """Get the next queued post for a page (FIFO by order_index). Returns Post or None."""
    result = await db.execute(
        select(Post)
        .where(Post.page_id == page_id, Post.status == PostStatus.queued)
        .order_by(Post.order_index.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def get_next_queued_post_sync(db: Session, page_id: str):
    """Sync version for Celery workers."""
    result = db.execute(
        select(Post)
        .where(Post.page_id == page_id, Post.status == PostStatus.queued)
        .order_by(Post.order_index.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()
