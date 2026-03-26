import logging
from datetime import datetime

import httpx
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import select, update

from app.config import get_settings
from app.database import SyncSessionLocal
from app.models.page import Page
from app.models.post import Post, PostStatus
from app.models.publish_log import PublishLog, PublishResult
from app.services.queue_manager import get_next_queued_post_sync
from app.services.schedule_matcher import get_matching_slots, mark_slot_dispatched
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.publish_task.check_publish_slots")
def check_publish_slots():
    """Beat task: check schedule and dispatch publish tasks for matching slots."""
    now_utc = datetime.utcnow()
    db = SyncSessionLocal()
    try:
        matching = get_matching_slots(db, now_utc)
        for page_id, slot_id in matching:
            post = get_next_queued_post_sync(db, page_id)
            if not post:
                logger.info("No queued posts for page %s", page_id)
                continue

            # Atomic status transition
            result = db.execute(
                update(Post)
                .where(Post.id == post.id)
                .where(Post.status == PostStatus.queued)
                .values(status=PostStatus.publishing)
            )
            if result.rowcount == 0:
                continue  # Already picked up

            db.commit()
            mark_slot_dispatched(slot_id, now_utc)

            publish_post_task.delay(str(post.id), page_id)
            logger.info("Dispatched publish for post %s on page %s", post.id, page_id)
    finally:
        db.close()


@celery_app.task(
    bind=True,
    name="app.tasks.publish_task.publish_post_task",
    max_retries=3,
    acks_late=True,
    soft_time_limit=250,
    time_limit=300,
)
def publish_post_task(self, post_id: str, page_id: str):
    """Publish a single post with retry logic."""
    db = SyncSessionLocal()
    try:
        post = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
        if not post:
            logger.error("Post %s not found", post_id)
            return

        page = db.execute(select(Page).where(Page.id == page_id)).scalar_one_or_none()
        if not page:
            logger.error("Page %s not found", page_id)
            post.status = PostStatus.failed
            post.error_message = "Page not found"
            db.commit()
            return

        # Call publisher (sync wrapper around async)
        settings = get_settings()
        with httpx.Client(
            base_url=f"https://graph.facebook.com/{settings.GRAPH_API_VERSION}",
            timeout=httpx.Timeout(30.0, connect=10.0),
        ) as client:
            from app.services.publisher import publish_post as async_publish
            import asyncio
            pub_result = asyncio.run(async_publish(post, page, client))

        if pub_result.success:
            post.status = PostStatus.published
            post.fb_post_id = pub_result.fb_post_id
            post.published_at = datetime.utcnow()
            log_result = PublishResult.success

            # Reset error spike counter
            try:
                import redis as sync_redis
                r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
                r.delete(f"error_spike:{page_id}")
            except Exception:
                pass

            # Schedule engagement fetches
            from app.tasks.engagement_task import fetch_engagement_task
            for delay in [3600, 14400, 86400]:
                fetch_engagement_task.apply_async(
                    args=[post_id],
                    countdown=delay,
                    task_id=f"engagement-{post_id}-{delay}",
                )

        else:
            error = pub_result.error
            if error and error.is_retriable and self.request.retries < self.max_retries:
                # Write log before retry
                log = PublishLog(
                    post_id=post.id, page_id=page.id,
                    result=PublishResult.retriable_error,
                    error_code=error.code,
                    error_message=error.message,
                    retry_count=self.request.retries,
                )
                db.add(log)
                post.status = PostStatus.queued  # Revert for retry
                db.commit()
                raise self.retry(countdown=error.retry_delay_seconds)

            # Permanent error or max retries
            post.status = PostStatus.failed
            post.error_message = error.message if error else "Unknown error"
            log_result = PublishResult.permanent_error

            # Error spike tracking
            try:
                import redis as sync_redis
                r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
                count = r.incr(f"error_spike:{page_id}")
                r.expire(f"error_spike:{page_id}", 3600)
                if count >= 3:
                    r.set(f"page_paused:{page_id}", "1")
                    logger.warning("Page %s auto-paused after %d failures", page_id, count)
            except Exception:
                pass

        # Write publish log
        log = PublishLog(
            post_id=post.id, page_id=page.id,
            result=log_result if pub_result.success else PublishResult.permanent_error,
            fb_post_id=pub_result.fb_post_id,
            error_code=pub_result.error.code if pub_result.error else None,
            error_message=pub_result.error.message if pub_result.error else None,
            retry_count=self.request.retries,
        )
        db.add(log)
        db.commit()

    except SoftTimeLimitExceeded:
        logger.warning("Publish task timed out for post %s", post_id)
        post = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
        if post:
            post.status = PostStatus.failed
            post.error_message = "Task timed out"
            db.commit()
    except self.MaxRetriesExceededError:
        raise  # Let Celery handle max retries
    finally:
        db.close()
