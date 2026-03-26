import json
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_async_db
from app.models.alert_log import AlertLog
from app.models.page import Page
from app.schemas.alerts import (
    AlertConfigUpdate, AlertConfigResponse,
    AlertLogEntry, AlertLogResponse,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


async def _get_redis():
    settings = get_settings()
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("/config")
async def get_alert_config(
    page_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Get alert configuration per page."""
    configs = []
    try:
        r = await _get_redis()
        if page_id:
            pages_result = await db.execute(select(Page).where(Page.id == page_id))
            pages = [pages_result.scalar_one_or_none()]
        else:
            pages_result = await db.execute(select(Page).where(Page.is_active == True))
            pages = pages_result.scalars().all()

        for page in pages:
            if not page:
                continue
            config_str = await r.get(f"alert_config:{page.id}")
            config_data = json.loads(config_str) if config_str else {}
            configs.append(AlertConfigResponse(
                page_id=str(page.id),
                page_name=page.name,
                telegram_enabled=config_data.get("telegram_enabled", False),
                telegram_chat_ids=config_data.get("telegram_chat_ids", []),
                email_enabled=config_data.get("email_enabled", False),
                email_recipients=config_data.get("email_recipients", []),
                dedup_window_minutes=config_data.get("dedup_window_minutes", 30),
            ))
        await r.aclose()
    except Exception:
        pass

    return {"configs": configs}


@router.put("/config")
async def update_alert_config(data: AlertConfigUpdate):
    """Update alert config for a page (stored in Redis)."""
    try:
        r = await _get_redis()
        config = {
            "telegram_enabled": data.telegram_enabled,
            "telegram_chat_ids": data.telegram_chat_ids,
            "email_enabled": data.email_enabled,
            "email_recipients": data.email_recipients,
            "dedup_window_minutes": data.dedup_window_minutes,
        }
        await r.set(f"alert_config:{data.page_id}", json.dumps(config))
        await r.aclose()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {e}")

    return {"detail": "Config updated"}


@router.get("/log", response_model=AlertLogResponse)
async def get_alert_log(
    page_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """Get alert history with filters."""
    query = select(AlertLog).outerjoin(Page, AlertLog.page_id == Page.id)
    count_query = select(func.count(AlertLog.id))

    if page_id:
        query = query.where(AlertLog.page_id == page_id)
        count_query = count_query.where(AlertLog.page_id == page_id)
    if alert_type:
        query = query.where(AlertLog.type == alert_type)
        count_query = count_query.where(AlertLog.type == alert_type)
    if severity:
        query = query.where(AlertLog.severity == severity)
        count_query = count_query.where(AlertLog.severity == severity)
    if acknowledged is not None:
        query = query.where(AlertLog.acknowledged == acknowledged)
        count_query = count_query.where(AlertLog.acknowledged == acknowledged)

    query = query.order_by(AlertLog.sent_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()
    total = (await db.execute(count_query)).scalar() or 0

    entries = [
        AlertLogEntry(
            id=str(log.id),
            type=log.type,
            message=log.message,
            severity=log.severity.value if hasattr(log.severity, 'value') else str(log.severity),
            channel=log.channel.value if hasattr(log.channel, 'value') else str(log.channel),
            page_name=None,  # Would need join
            sent_at=log.sent_at,
            acknowledged=log.acknowledged,
        )
        for log in logs
    ]

    return AlertLogResponse(entries=entries, total=total)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Mark an alert as acknowledged."""
    result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Alert not found")

    log.acknowledged = True
    await db.commit()
    return {"acknowledged": True}
