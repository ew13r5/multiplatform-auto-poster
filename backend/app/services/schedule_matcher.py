import logging
from datetime import datetime, date
from typing import List, Tuple
from zoneinfo import ZoneInfo

import redis as sync_redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.schedule_slot import ScheduleSlot

logger = logging.getLogger(__name__)


def _get_sync_redis():
    settings = get_settings()
    return sync_redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_matching_slots(db: Session, now_utc: datetime) -> List[Tuple[str, str]]:
    """Return list of (page_id, slot_id) pairs matching current UTC time.

    Converts each slot's time from its timezone to UTC for comparison.
    Checks global pause and per-page pause state via Redis.
    """
    # Check global pause
    try:
        r = _get_sync_redis()
        if r.get("schedule:paused") == "1":
            return []
    except Exception:
        pass  # Redis unavailable — continue without pause check

    # Query enabled slots
    result = db.execute(select(ScheduleSlot).where(ScheduleSlot.enabled == True))
    slots = result.scalars().all()

    matching = []
    for slot in slots:
        try:
            # Parse slot time
            hour, minute = map(int, slot.time_utc.split(":"))
            # Create datetime in slot's timezone
            slot_tz = ZoneInfo(slot.timezone)
            today = now_utc.date()
            slot_local = datetime(today.year, today.month, today.day, hour, minute, tzinfo=slot_tz)
            # Convert to UTC
            slot_utc = slot_local.astimezone(ZoneInfo("UTC"))

            # Compare hour and minute
            if slot_utc.hour != now_utc.hour or slot_utc.minute != now_utc.minute:
                continue

            # Compare day of week (Monday=0, Sunday=6)
            if now_utc.weekday() != slot.day_of_week:
                continue

            # Check per-page pause
            try:
                if r.get(f"page_paused:{slot.page_id}") == "1":
                    continue
            except Exception:
                pass

            # Check slot dedup
            dedup_key = f"slot_dispatched:{slot.id}:{now_utc.strftime('%Y-%m-%d-%H:%M')}"
            try:
                if r.exists(dedup_key):
                    continue
            except Exception:
                pass

            matching.append((str(slot.page_id), str(slot.id)))

        except Exception as e:
            logger.warning("Error matching slot %s: %s", slot.id, e)
            continue

    return matching


def mark_slot_dispatched(slot_id: str, now_utc: datetime) -> None:
    """Set Redis dedup key to prevent double-dispatch."""
    try:
        r = _get_sync_redis()
        key = f"slot_dispatched:{slot_id}:{now_utc.strftime('%Y-%m-%d-%H:%M')}"
        r.setex(key, 120, "1")
    except Exception:
        pass
