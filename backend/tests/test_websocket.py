import pytest
from app.api.websocket import ConnectionManager


@pytest.mark.asyncio
async def test_manager_starts_empty():
    mgr = ConnectionManager()
    assert len(mgr.active_connections) == 0


def test_celery_app_config():
    from app.tasks.celery_app import celery_app
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.task_time_limit == 300
    assert celery_app.conf.task_soft_time_limit == 250
    assert celery_app.conf.task_track_started is True
    assert celery_app.conf.timezone == "UTC"


def test_exception_classes():
    from app.exceptions import PostNotEditableError, PageNotFoundError, InvalidFileError

    e1 = PostNotEditableError("post-1", "published")
    assert "post-1" in str(e1)
    assert e1.post_id == "post-1"
    assert e1.status == "published"

    e2 = PageNotFoundError("page-2")
    assert "page-2" in str(e2)

    e3 = InvalidFileError("too large")
    assert "too large" in str(e3)
