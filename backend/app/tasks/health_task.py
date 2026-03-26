import logging
import time

import redis as sync_redis
from sqlalchemy import select

from app.config import get_settings
from app.database import SyncSessionLocal
from app.models.page import Page
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.health_task.update_heartbeat")
def update_heartbeat():
    """Update scheduler heartbeat Redis key."""
    try:
        settings = get_settings()
        r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.setex("scheduler:heartbeat", 120, str(int(time.time())))
    except Exception as e:
        logger.error("Failed to update heartbeat: %s", e)


@celery_app.task(name="app.tasks.health_task.check_all_tokens")
def check_all_tokens():
    """Verify all active page tokens."""
    db = SyncSessionLocal()
    try:
        result = db.execute(select(Page).where(Page.is_active == True))
        pages = result.scalars().all()

        for page in pages:
            if not page.access_token_encrypted:
                logger.warning("Page %s has no token", page.name)
                continue

            import asyncio
            import httpx
            from app.services.token_manager import check_token_health

            settings = get_settings()

            async def _check():
                async with httpx.AsyncClient(
                    base_url=f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}",
                    timeout=httpx.Timeout(30.0, connect=10.0),
                ) as client:
                    return await check_token_health(page, client)

            status = asyncio.run(_check())

            if not status.is_valid:
                logger.error("Token unhealthy for page %s: %s", page.name, status.error_message)
            elif status.expires_soon:
                logger.warning("Token for page %s expires soon", page.name)
            elif status.missing_scopes:
                logger.warning("Page %s missing scopes: %s", page.name, status.missing_scopes)
            else:
                logger.info("Token healthy for page %s", page.name)
    finally:
        db.close()
