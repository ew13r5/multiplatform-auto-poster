import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.page import Page
from app.models.post import Post
from app.tasks.bulk_import import process_bulk_import


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


def test_csv_import_creates_posts(db):
    page = Page(fb_page_id="bi1", name="Import Page")
    db.add(page)
    db.commit()

    csv_content = "page_name,content_text,image_key,link_url\nImport Page,Hello,,\nImport Page,World,,"
    result = process_bulk_import(csv_content, "csv", db)
    assert result["total"] == 2
    assert result["imported"] == 2
    assert result["errors"] == []


def test_csv_import_unknown_page(db):
    csv_content = "page_name,content_text,image_key,link_url\nNonexistent,Hello,,"
    result = process_bulk_import(csv_content, "csv", db)
    assert result["imported"] == 0
    assert len(result["errors"]) == 1
    assert "not found" in result["errors"][0]["reason"]


def test_json_import_creates_posts(db):
    page = Page(fb_page_id="bi2", name="JSON Page")
    db.add(page)
    db.commit()

    json_content = '[{"page_name": "JSON Page", "content_text": "JSON post", "image_key": "", "link_url": ""}]'
    result = process_bulk_import(json_content, "json", db)
    assert result["imported"] == 1


def test_xquik_json_payload_import_creates_link_posts(db):
    page = Page(fb_page_id="bi-xquik", name="Xquik Page")
    db.add(page)
    db.commit()

    json_content = """{
        "page_name": "Xquik Page",
        "tweets": [
            {"id": "123", "text": "Launch update", "author": {"username": "xquik"}}
        ]
    }"""
    result = process_bulk_import(json_content, "json", db)

    assert result["total"] == 1
    assert result["imported"] == 1
    assert result["errors"] == []
    post = db.query(Post).filter(Post.page_id == page.id).one()
    assert post.content_text == "Launch update"
    assert post.link_url == "https://x.com/xquik/status/123"


def test_json_import_rejects_invalid_root(db):
    result = process_bulk_import('{"items": []}', "json", db)

    assert result["imported"] == 0
    assert result["errors"][0]["reason"] == "JSON import must be a row array or an Xquik tweets payload"


def test_csv_import_rejects_missing_required_headers(db):
    result = process_bulk_import("content_text\nMissing page", "csv", db)

    assert result["total"] == 0
    assert result["imported"] == 0
    assert result["errors"][0]["reason"] == "Missing columns: page_name"


def test_csv_import_accepts_utf8_bom(db):
    page = Page(fb_page_id="bi-bom", name="BOM Page")
    db.add(page)
    db.commit()

    result = process_bulk_import("\ufeffpage_name,content_text\nBOM Page,Hello", "csv", db)

    assert result["total"] == 1
    assert result["imported"] == 1
    assert result["errors"] == []


def test_import_auto_detects_post_type(db):
    page = Page(fb_page_id="bi3", name="Type Page")
    db.add(page)
    db.commit()

    csv_content = "page_name,content_text,image_key,link_url\nType Page,Photo post,img.jpg,\nType Page,Link post,,https://example.com"
    result = process_bulk_import(csv_content, "csv", db)
    assert result["imported"] == 2


def test_import_empty_file(db):
    result = process_bulk_import("", "csv", db)
    assert result["total"] == 0
    assert result["imported"] == 0
