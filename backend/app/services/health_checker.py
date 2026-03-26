import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

import redis as sync_redis
from sqlalchemy import select, func

from app.config import get_settings
from app.models.page import Page
from app.models.post import Post, PostStatus

logger = logging.getLogger(__name__)


@dataclass
class SystemHealth:
    status: str  # healthy, degraded, unhealthy
    checks: dict
    mode: str = "development"
    scheduler_last_beat: Optional[datetime] = None
    pages_with_issues: List[str] = field(default_factory=list)


async def get_system_health(db=None) -> SystemHealth:
    """Check all system components and return aggregated health."""
    checks = {}
    pages_with_issues = []
    scheduler_last_beat = None

    # DB check
    try:
        from app.database import async_engine
        from sqlalchemy import text
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception:
        checks["db"] = False

    # Redis check
    try:
        settings = get_settings()
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()

        # Check scheduler heartbeat
        beat = await r.get("scheduler:heartbeat")
        if beat:
            beat_time = int(beat)
            scheduler_last_beat = datetime.utcfromtimestamp(beat_time)
            if time.time() - beat_time > 120:
                checks["scheduler"] = False
            else:
                checks["scheduler"] = True
        else:
            checks["scheduler"] = False

        await r.aclose()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
        checks["scheduler"] = False

    # MinIO check
    try:
        import asyncio
        from app.services.storage import get_minio_client
        settings = get_settings()
        client = get_minio_client()
        await asyncio.to_thread(client.bucket_exists, settings.MINIO_BUCKET)
        checks["minio"] = True
    except Exception:
        checks["minio"] = False

    # Determine status
    critical = checks.get("scheduler", True) and checks.get("db", True)
    all_ok = all(checks.values())

    if all_ok:
        status = "healthy"
    elif not critical:
        status = "unhealthy"
    else:
        status = "degraded"

    return SystemHealth(
        status=status,
        checks=checks,
        mode="development",
        scheduler_last_beat=scheduler_last_beat,
        pages_with_issues=pages_with_issues,
    )
