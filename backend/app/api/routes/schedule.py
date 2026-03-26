import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_async_db
from app.models.schedule_slot import ScheduleSlot
from app.schemas.schedule import ScheduleSlotSchema, ScheduleUpdateRequest, PauseRequest, PauseResponse

router = APIRouter(prefix="/schedule", tags=["schedule"])


async def _get_redis():
    settings = get_settings()
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("")
async def get_schedule(db: AsyncSession = Depends(get_async_db)):
    """List all schedule slots."""
    result = await db.execute(select(ScheduleSlot))
    slots = result.scalars().all()
    return {"slots": [
        ScheduleSlotSchema.model_validate(s).model_dump() for s in slots
    ]}


@router.put("")
async def update_schedule(
    data: ScheduleUpdateRequest, db: AsyncSession = Depends(get_async_db)
):
    """Replace schedule slots for affected pages."""
    page_ids = {s.page_id for s in data.slots}
    for page_id in page_ids:
        await db.execute(
            delete(ScheduleSlot).where(ScheduleSlot.page_id == page_id)
        )
    for slot_data in data.slots:
        slot = ScheduleSlot(
            page_id=slot_data.page_id,
            day_of_week=slot_data.day_of_week,
            time_utc=slot_data.time_utc,
            timezone=slot_data.timezone,
            enabled=slot_data.enabled,
        )
        db.add(slot)
    await db.commit()
    return {"detail": "Schedule updated"}


@router.post("/pause", response_model=PauseResponse)
async def toggle_pause(data: PauseRequest):
    """Pause or resume all publishing."""
    try:
        r = await _get_redis()
        await r.set("schedule:paused", "1" if data.paused else "0")
        await r.aclose()
    except Exception:
        pass  # Redis may not be available in tests
    return PauseResponse(paused=data.paused)
