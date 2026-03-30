import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from app.database import SyncSessionLocal
from app.models.page import Page
from app.models.post import Post, PostStatus
from app.models.publish_log import PublishLog, PublishResult
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.report_task.send_daily_report")
def send_daily_report():
    """Compile and send daily health report."""
    db = SyncSessionLocal()
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)

        pages = db.execute(select(Page).where(Page.is_active == True)).scalars().all()

        report_lines = ["📊 Daily Report\n"]

        for page in pages:
            # Published count
            pub_count = db.execute(
                select(func.count(PublishLog.id)).where(
                    PublishLog.page_id == page.id,
                    PublishLog.attempted_at >= yesterday,
                    PublishLog.result == PublishResult.success,
                )
            ).scalar() or 0

            # Failed count
            fail_count = db.execute(
                select(func.count(PublishLog.id)).where(
                    PublishLog.page_id == page.id,
                    PublishLog.attempted_at >= yesterday,
                    PublishLog.result.in_([PublishResult.retriable_error, PublishResult.permanent_error]),
                )
            ).scalar() or 0

            # Queue size
            queue_size = db.execute(
                select(func.count(Post.id)).where(
                    Post.page_id == page.id,
                    Post.status == PostStatus.queued,
                )
            ).scalar() or 0

            report_lines.append(
                f"📄 {page.name}: ✅{pub_count} published, ❌{fail_count} failed, 📋{queue_size} queued"
            )

        report = "\n".join(report_lines)
        logger.info("Daily report:\n%s", report)

        return report

    finally:
        db.close()
