import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.page import Page
from app.models.post import Post, PostStatus, PostType
from app.models.publish_log import PublishLog, PublishResult
from app.models.schedule_slot import ScheduleSlot
from app.models.engagement import Engagement
from app.models.alert_log import AlertLog, AlertChannel, AlertSeverity


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


def test_page_creates_with_required_fields(db: Session):
    page = Page(fb_page_id="123456", name="Test Page")
    db.add(page)
    db.flush()
    assert page.id is not None
    assert page.fb_page_id == "123456"
    assert page.name == "Test Page"
    assert page.is_active is True


def test_page_stores_encrypted_token(db: Session):
    page = Page(
        fb_page_id="789",
        name="Token Page",
        access_token_encrypted="encrypted_data_here",
    )
    db.add(page)
    db.flush()
    assert page.access_token_encrypted == "encrypted_data_here"


def test_post_creates_with_correct_type(db: Session):
    page = Page(fb_page_id="p1", name="Page1")
    db.add(page)
    db.flush()
    post = Post(
        page_id=page.id,
        content_text="Hello world",
        post_type=PostType.text,
        status=PostStatus.draft,
    )
    db.add(post)
    db.flush()
    assert post.post_type == PostType.text
    assert post.status == PostStatus.draft


def test_post_status_enum_has_all_values():
    values = {s.value for s in PostStatus}
    assert values == {"draft", "queued", "publishing", "published", "failed"}


def test_post_type_enum_has_all_values():
    values = {t.value for t in PostType}
    assert values == {"text", "photo", "link"}


def test_post_cascade_delete(db: Session):
    page = Page(fb_page_id="cascade1", name="CascadePage")
    db.add(page)
    db.flush()
    post = Post(
        page_id=page.id,
        content_text="Will be deleted",
        post_type=PostType.text,
    )
    db.add(post)
    db.flush()
    post_id = post.id
    db.delete(page)
    db.flush()
    result = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
    assert result is None


def test_publish_log_creates(db: Session):
    page = Page(fb_page_id="pl1", name="PLPage")
    db.add(page)
    db.flush()
    post = Post(page_id=page.id, content_text="Test", post_type=PostType.text)
    db.add(post)
    db.flush()
    log = PublishLog(
        post_id=post.id,
        page_id=page.id,
        result=PublishResult.success,
        fb_post_id="fb_123",
    )
    db.add(log)
    db.flush()
    assert log.result == PublishResult.success
    assert log.retry_count == 0


def test_publish_result_enum():
    values = {r.value for r in PublishResult}
    assert values == {"success", "retriable_error", "permanent_error"}


def test_schedule_slot_creates(db: Session):
    page = Page(fb_page_id="ss1", name="SchedulePage")
    db.add(page)
    db.flush()
    slot = ScheduleSlot(
        page_id=page.id, day_of_week=1, time_utc="14:00", timezone="UTC"
    )
    db.add(slot)
    db.flush()
    assert slot.day_of_week == 1
    assert slot.time_utc == "14:00"
    assert slot.enabled is True


def test_engagement_creates(db: Session):
    page = Page(fb_page_id="eng1", name="EngPage")
    db.add(page)
    db.flush()
    post = Post(page_id=page.id, content_text="Engaged", post_type=PostType.text)
    db.add(post)
    db.flush()
    eng = Engagement(post_id=post.id, fb_post_id="fb_eng_1", likes=10, comments=3)
    db.add(eng)
    db.flush()
    assert eng.likes == 10
    assert eng.shares == 0


def test_alert_log_enums():
    assert {c.value for c in AlertChannel} == {"telegram", "email", "in_app"}
    assert {s.value for s in AlertSeverity} == {"info", "warning", "critical"}


def test_alert_log_creates(db: Session):
    page = Page(fb_page_id="al1", name="AlertPage")
    db.add(page)
    db.flush()
    alert = AlertLog(
        type="empty_queue",
        message="No posts queued",
        page_id=page.id,
        channel=AlertChannel.telegram,
        severity=AlertSeverity.warning,
    )
    db.add(alert)
    db.flush()
    assert alert.acknowledged is False
    assert alert.channel == AlertChannel.telegram
