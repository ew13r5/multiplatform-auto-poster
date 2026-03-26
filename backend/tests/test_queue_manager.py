import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.page import Page
from app.models.post import Post, PostStatus, PostType
from app.services.queue_manager import get_next_queued_post_sync


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


def test_get_next_queued_post_returns_lowest_order(db):
    page = Page(fb_page_id="qm1", name="QM Page")
    db.add(page)
    db.flush()

    p1 = Post(page_id=page.id, content_text="First", post_type=PostType.text, status=PostStatus.queued, order_index=2)
    p2 = Post(page_id=page.id, content_text="Second", post_type=PostType.text, status=PostStatus.queued, order_index=1)
    db.add_all([p1, p2])
    db.flush()

    result = get_next_queued_post_sync(db, page.id)
    assert result is not None
    assert result.content_text == "Second"  # order_index=1


def test_get_next_queued_post_returns_none_when_empty(db):
    page = Page(fb_page_id="qm2", name="Empty Page")
    db.add(page)
    db.flush()

    result = get_next_queued_post_sync(db, page.id)
    assert result is None


def test_get_next_queued_skips_non_queued(db):
    page = Page(fb_page_id="qm3", name="Mixed Page")
    db.add(page)
    db.flush()

    p1 = Post(page_id=page.id, content_text="Draft", post_type=PostType.text, status=PostStatus.draft, order_index=1)
    p2 = Post(page_id=page.id, content_text="Queued", post_type=PostType.text, status=PostStatus.queued, order_index=2)
    db.add_all([p1, p2])
    db.flush()

    result = get_next_queued_post_sync(db, page.id)
    assert result.content_text == "Queued"
