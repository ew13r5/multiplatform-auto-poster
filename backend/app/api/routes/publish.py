from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.post import Post, PostStatus
from app.models.page import Page
from app.models.publish_log import PublishLog, PublishResult
from app.schemas.publish import PublishNowResponse
from app.services.publisher import publish_post

router = APIRouter(prefix="/posts", tags=["publish"])


@router.post("/{post_id}/publish-now", response_model=PublishNowResponse)
async def publish_now(
    post_id: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    """Immediately publish a post, bypassing the schedule."""
    # Load post
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status not in (PostStatus.queued, PostStatus.draft):
        raise HTTPException(
            status_code=400,
            detail=f"Post must be in queued or draft status, got '{post.status.value}'",
        )

    # Atomic status transition
    update_result = await db.execute(
        update(Post)
        .where(Post.id == post_id)
        .where(Post.status.in_([PostStatus.queued, PostStatus.draft]))
        .values(status=PostStatus.publishing)
    )
    if update_result.rowcount == 0:
        raise HTTPException(status_code=409, detail="Post already being published")

    await db.commit()
    await db.refresh(post)

    # Load page
    page_result = await db.execute(select(Page).where(Page.id == post.page_id))
    page = page_result.scalar_one_or_none()
    if not page:
        post.status = PostStatus.failed
        post.error_message = "Page not found"
        await db.commit()
        raise HTTPException(status_code=404, detail="Page not found")

    # Get or create httpx client
    graph_client = getattr(request.app.state, "graph_client", None)
    if not graph_client:
        from app.config import get_settings
        settings = get_settings()
        graph_client = httpx.AsyncClient(
            base_url=f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}",
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    # Publish
    try:
        pub_result = await publish_post(post, page, graph_client)
    except Exception as e:
        post.status = PostStatus.failed
        post.error_message = str(e)
        await db.commit()
        return PublishNowResponse(
            post_id=str(post.id), status="failed", error_message=str(e)
        )

    if pub_result.success:
        post.status = PostStatus.published
        post.fb_post_id = pub_result.fb_post_id
        post.published_at = datetime.utcnow()
        log_result = PublishResult.success
    else:
        post.status = PostStatus.failed
        post.error_message = pub_result.error.message if pub_result.error else "Unknown error"
        log_result = PublishResult.permanent_error

    # Write publish log
    log = PublishLog(
        post_id=post.id,
        page_id=page.id,
        result=log_result,
        fb_post_id=pub_result.fb_post_id,
        error_code=pub_result.error.code if pub_result.error else None,
        error_message=pub_result.error.message if pub_result.error else None,
        retry_count=0,
    )
    db.add(log)
    await db.commit()

    return PublishNowResponse(
        post_id=str(post.id),
        status=post.status.value,
        fb_post_id=post.fb_post_id,
        error_message=post.error_message,
    )
