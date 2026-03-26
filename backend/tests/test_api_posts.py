import pytest
from httpx import AsyncClient


async def _create_page(client: AsyncClient) -> str:
    resp = await client.post("/api/pages/connect", json={
        "fb_page_id": "test_page_1",
        "name": "Test Page",
        "access_token": "tok",
    })
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_draft_post(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    response = await auth_client.post("/api/posts", json={
        "page_id": page_id,
        "content_text": "Hello world",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["post_type"] == "text"
    assert data["content_text"] == "Hello world"


@pytest.mark.asyncio
async def test_create_photo_post_type(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    response = await auth_client.post("/api/posts", json={
        "page_id": page_id,
        "content_text": "Photo post",
        "image_key": "page1/abc.jpg",
    })
    assert response.status_code == 201
    assert response.json()["post_type"] == "photo"


@pytest.mark.asyncio
async def test_create_link_post_type(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    response = await auth_client.post("/api/posts", json={
        "page_id": page_id,
        "content_text": "Link post",
        "link_url": "https://example.com",
    })
    assert response.status_code == 201
    assert response.json()["post_type"] == "link"


@pytest.mark.asyncio
async def test_create_post_invalid_page(auth_client: AsyncClient):
    response = await auth_client.post("/api/posts", json={
        "page_id": "nonexistent-id",
        "content_text": "Will fail",
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_posts(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    await auth_client.post("/api/posts", json={
        "page_id": page_id, "content_text": "Post 1",
    })
    await auth_client.post("/api/posts", json={
        "page_id": page_id, "content_text": "Post 2",
    })
    response = await auth_client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["posts"]) == 2


@pytest.mark.asyncio
async def test_update_post_draft_to_queued(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    resp = await auth_client.post("/api/posts", json={
        "page_id": page_id, "content_text": "Draft",
    })
    post_id = resp.json()["id"]

    resp2 = await auth_client.put(f"/api/posts/{post_id}", json={"status": "queued"})
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "queued"
    assert resp2.json()["order_index"] is not None


@pytest.mark.asyncio
async def test_delete_draft_post(auth_client: AsyncClient):
    page_id = await _create_page(auth_client)
    resp = await auth_client.post("/api/posts", json={
        "page_id": page_id, "content_text": "Delete me",
    })
    post_id = resp.json()["id"]
    del_resp = await auth_client.delete(f"/api/posts/{post_id}")
    assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_bulk_import_rejects_txt(auth_client: AsyncClient):
    import io
    files = {"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")}
    response = await auth_client.post("/api/posts/bulk", files=files)
    assert response.status_code == 400
