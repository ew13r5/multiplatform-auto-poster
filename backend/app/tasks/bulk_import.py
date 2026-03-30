import csv
import json
import io
import logging
from typing import Any

from sqlalchemy import select, func

from app.models.page import Page
from app.models.post import Post, PostStatus, PostType
from app.tasks.celery_app import celery_app
from app.database import SyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.bulk_import.run_bulk_import", bind=True)
def run_bulk_import(self, file_content: str, file_type: str) -> dict:
    """Celery task wrapper for bulk import."""
    logger.info("Starting bulk import task %s", self.request.id)
    with SyncSessionLocal() as session:
        result = process_bulk_import(file_content, file_type, session)
    logger.info("Bulk import complete: %s", result)
    return result


def _detect_post_type(image_key: str, link_url: str) -> PostType:
    if image_key:
        return PostType.photo
    if link_url:
        return PostType.link
    return PostType.text


def process_bulk_import(file_content: str, file_type: str, db_session) -> dict:
    """Process bulk import synchronously. Called from Celery task or directly.

    Returns: {"total": N, "imported": N, "errors": [{row, reason}]}
    """
    errors = []
    imported = 0

    if file_type == "csv":
        rows = list(csv.DictReader(io.StringIO(file_content)))
    elif file_type == "json":
        rows = json.loads(file_content)
    else:
        return {"total": 0, "imported": 0, "errors": [{"row": 0, "reason": f"Unknown file type: {file_type}"}]}

    if not rows:
        return {"total": 0, "imported": 0, "errors": []}

    # Cache page lookups and order counters
    page_cache: dict[str, Any] = {}
    order_counters: dict[str, int] = {}

    for i, row in enumerate(rows):
        page_name = row.get("page_name", "").strip()
        content_text = row.get("content_text", "").strip()
        image_key = row.get("image_key", "").strip()
        link_url = row.get("link_url", "").strip()

        if not page_name:
            errors.append({"row": i + 1, "reason": "Missing page_name"})
            continue
        if not content_text:
            errors.append({"row": i + 1, "reason": "Missing content_text"})
            continue

        # Look up page
        if page_name not in page_cache:
            result = db_session.execute(
                select(Page).where(Page.name == page_name)
            )
            page = result.scalar_one_or_none()
            if page:
                page_cache[page_name] = page
                # Get current max order_index
                max_result = db_session.execute(
                    select(func.coalesce(func.max(Post.order_index), 0)).where(
                        Post.page_id == page.id
                    )
                )
                order_counters[page_name] = max_result.scalar() or 0
            else:
                page_cache[page_name] = None

        page = page_cache[page_name]
        if page is None:
            errors.append({"row": i + 1, "reason": f"Page '{page_name}' not found"})
            continue

        order_counters[page_name] += 1
        post_type = _detect_post_type(image_key, link_url)

        post = Post(
            page_id=page.id,
            content_text=content_text,
            image_key=image_key or None,
            link_url=link_url or None,
            post_type=post_type,
            status=PostStatus.queued,
            order_index=order_counters[page_name],
        )
        db_session.add(post)
        imported += 1

    db_session.commit()
    return {"total": len(rows), "imported": imported, "errors": errors}
