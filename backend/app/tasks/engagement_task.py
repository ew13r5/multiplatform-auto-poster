import logging

from sqlalchemy import select

from app.config import get_settings
from app.database import SyncSessionLocal
from app.models.post import Post
from app.models.page import Page
from app.models.engagement import Engagement
from app.services.encryption import decrypt_token
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.engagement_task.fetch_engagement_task")
def fetch_engagement_task(post_id: str):
    """Fetch engagement metrics for a published post."""
    db = SyncSessionLocal()
    try:
        post = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
        if not post or not post.fb_post_id:
            logger.info("Skipping engagement fetch for post %s (no fb_post_id)", post_id)
            return

        page = db.execute(select(Page).where(Page.id == post.page_id)).scalar_one_or_none()
        if not page or not page.access_token_encrypted:
            logger.warning("No page/token for post %s", post_id)
            return

        token = decrypt_token(page.access_token_encrypted)

        import asyncio
        import httpx
        from app.services.engagement_fetcher import fetch_engagement

        settings = get_settings()
        async def _fetch():
            async with httpx.AsyncClient(
                base_url=f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}",
                timeout=httpx.Timeout(30.0, connect=10.0),
            ) as client:
                return await fetch_engagement(post.fb_post_id, token, client)

        result = asyncio.run(_fetch())
        if result:
            eng = Engagement(
                post_id=post.id,
                fb_post_id=post.fb_post_id,
                likes=result.likes,
                comments=result.comments,
                shares=result.shares,
            )
            db.add(eng)
            db.commit()
            logger.info("Stored engagement for post %s: L=%d C=%d S=%d",
                       post_id, result.likes, result.comments, result.shares)
    except Exception as e:
        logger.error("Engagement fetch failed for post %s: %s", post_id, e)
    finally:
        db.close()
