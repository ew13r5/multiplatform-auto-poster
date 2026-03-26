import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.page import Page
from app.models.schedule_slot import ScheduleSlot
from app.services.schedule_matcher import get_matching_slots


@pytest.fixture(scope="module")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    session = sessionmaker(bind=engine)()
    yield session
    session.rollback()
    session.close()


@patch("app.services.schedule_matcher._get_sync_redis")
def test_returns_matching_slot(mock_redis, db):
    mock_r = MagicMock()
    mock_r.get.return_value = None
    mock_r.exists.return_value = False
    mock_redis.return_value = mock_r

    page = Page(fb_page_id="sm1", name="SM Page")
    db.add(page)
    db.flush()

    # Monday at 14:00 UTC
    slot = ScheduleSlot(
        page_id=page.id, day_of_week=0, time_utc="14:00", timezone="UTC", enabled=True
    )
    db.add(slot)
    db.flush()

    # Monday 14:00 UTC
    now = datetime(2026, 3, 30, 14, 0, tzinfo=ZoneInfo("UTC"))  # Monday
    result = get_matching_slots(db, now)
    assert len(result) == 1
    assert result[0][0] == str(page.id)


@patch("app.services.schedule_matcher._get_sync_redis")
def test_returns_empty_when_no_match(mock_redis, db):
    mock_r = MagicMock()
    mock_r.get.return_value = None
    mock_redis.return_value = mock_r

    page = Page(fb_page_id="sm2", name="SM Page 2")
    db.add(page)
    db.flush()

    slot = ScheduleSlot(
        page_id=page.id, day_of_week=0, time_utc="14:00", timezone="UTC", enabled=True
    )
    db.add(slot)
    db.flush()

    # Wrong time
    now = datetime(2026, 3, 30, 15, 0, tzinfo=ZoneInfo("UTC"))
    result = get_matching_slots(db, now)
    assert len(result) == 0


@patch("app.services.schedule_matcher._get_sync_redis")
def test_returns_empty_when_paused(mock_redis, db):
    mock_r = MagicMock()
    mock_r.get.return_value = "1"  # Paused
    mock_redis.return_value = mock_r

    now = datetime(2026, 3, 30, 14, 0, tzinfo=ZoneInfo("UTC"))
    result = get_matching_slots(db, now)
    assert len(result) == 0


@patch("app.services.schedule_matcher._get_sync_redis")
def test_skips_disabled_slots(mock_redis, db):
    mock_r = MagicMock()
    mock_r.get.return_value = None
    mock_r.exists.return_value = False
    mock_redis.return_value = mock_r

    page = Page(fb_page_id="sm3", name="SM Page 3")
    db.add(page)
    db.flush()

    slot = ScheduleSlot(
        page_id=page.id, day_of_week=0, time_utc="14:00", timezone="UTC", enabled=False
    )
    db.add(slot)
    db.flush()

    now = datetime(2026, 3, 30, 14, 0, tzinfo=ZoneInfo("UTC"))
    result = get_matching_slots(db, now)
    assert len(result) == 0


@patch("app.services.schedule_matcher._get_sync_redis")
def test_timezone_conversion(mock_redis, db):
    """Slot at 17:00 Moscow (UTC+3) = 14:00 UTC."""
    mock_r = MagicMock()
    mock_r.get.return_value = None
    mock_r.exists.return_value = False
    mock_redis.return_value = mock_r

    page = Page(fb_page_id="sm4", name="TZ Page")
    db.add(page)
    db.flush()

    slot = ScheduleSlot(
        page_id=page.id, day_of_week=0, time_utc="17:00", timezone="Europe/Moscow", enabled=True
    )
    db.add(slot)
    db.flush()

    # 14:00 UTC = 17:00 Moscow
    now = datetime(2026, 3, 30, 14, 0, tzinfo=ZoneInfo("UTC"))
    result = get_matching_slots(db, now)
    assert len(result) == 1
