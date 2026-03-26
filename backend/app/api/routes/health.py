from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check — checks DB, Redis, MinIO connectivity."""
    checks = {}
    all_ok = True

    # DB check
    try:
        from app.database import async_engine
        from sqlalchemy import text
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception:
        checks["db"] = False
        all_ok = False

    # Redis check
    try:
        import redis.asyncio as aioredis
        from app.config import get_settings
        settings = get_settings()
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
        all_ok = False

    # MinIO check
    try:
        import asyncio
        from app.services.storage import get_minio_client
        from app.config import get_settings
        settings = get_settings()
        client = get_minio_client()
        result = await asyncio.to_thread(client.bucket_exists, settings.MINIO_BUCKET)
        checks["minio"] = True
    except Exception:
        checks["minio"] = False
        all_ok = False

    if all_ok:
        status = "healthy"
    elif not any(checks.values()):
        status = "unhealthy"
    else:
        status = "degraded"

    return HealthResponse(status=status, checks=checks, mode="development")
