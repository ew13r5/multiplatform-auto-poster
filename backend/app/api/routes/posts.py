from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.page import Page
from app.models.post import Post, PostStatus, PostType
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostListResponse,
    ReorderRequest, BulkImportResponse,
)
from app.services.storage import get_presigned_url

router = APIRouter(prefix="/posts", tags=["posts"])


def _detect_post_type(image_key: Optional[str], link_url: Optional[str]) -> PostType:
    if image_key:
        return PostType.photo
    if link_url:
        return PostType.link
    return PostType.text


def _post_to_response(post: Post) -> PostResponse:
    image_url = None
    if post.image_key:
        try:
            image_url = get_presigned_url(post.image_key)
        except Exception:
            pass
    return PostResponse(
        id=str(post.id),
        page_id=str(post.page_id),
        content_text=post.content_text,
        post_type=post.post_type.value if post.post_type else "text",
        status=post.status.value if post.status else "draft",
        order_index=post.order_index,
        image_key=post.image_key,
        image_url=image_url,
        link_url=post.link_url,
        fb_post_id=post.fb_post_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.get("", response_model=PostListResponse)
async def list_posts(
    page_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """List posts with optional filters, ordered by order_index."""
    query = select(Post)
    count_query = select(func.count(Post.id))

    if page_id:
        query = query.where(Post.page_id == page_id)
        count_query = count_query.where(Post.page_id == page_id)
    if status:
        query = query.where(Post.status == status)
        count_query = count_query.where(Post.status == status)

    query = query.order_by(Post.order_index.asc().nullslast()).limit(limit).offset(offset)

    result = await db.execute(query)
    posts = result.scalars().all()
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return PostListResponse(
        posts=[_post_to_response(p) for p in posts],
        total=total,
    )


@router.post("", status_code=201, response_model=PostResponse)
async def create_post(data: PostCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new draft post."""
    # Validate page exists
    page = await db.execute(select(Page).where(Page.id == data.page_id))
    if not page.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Page not found")

    post_type = _detect_post_type(data.image_key, data.link_url)
    post = Post(
        page_id=data.page_id,
        content_text=data.content_text,
        image_key=data.image_key,
        link_url=data.link_url,
        post_type=post_type,
        status=PostStatus.draft,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return _post_to_response(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str, data: PostUpdate, db: AsyncSession = Depends(get_async_db)
):
    """Update a post. Only draft/queued posts can be edited."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status not in (PostStatus.draft, PostStatus.queued):
        raise HTTPException(status_code=403, detail=f"Cannot edit post with status '{post.status.value}'")

    if data.content_text is not None:
        post.content_text = data.content_text
    if data.image_key is not None:
        post.image_key = data.image_key
    if data.link_url is not None:
        post.link_url = data.link_url

    # Handle status transitions
    if data.status is not None:
        new_status = PostStatus(data.status)
        if new_status == PostStatus.queued and post.status == PostStatus.draft:
            # Assign order_index
            max_idx = await db.execute(
                select(func.coalesce(func.max(Post.order_index), 0)).where(
                    Post.page_id == post.page_id
                )
            )
            post.order_index = (max_idx.scalar() or 0) + 1
        elif new_status == PostStatus.draft and post.status == PostStatus.queued:
            post.order_index = None
        post.status = new_status

    # Re-detect post_type
    post.post_type = _detect_post_type(post.image_key, post.link_url)

    await db.commit()
    await db.refresh(post)
    return _post_to_response(post)


@router.delete("/{post_id}")
async def delete_post(post_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete a draft or queued post."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status not in (PostStatus.draft, PostStatus.queued):
        raise HTTPException(status_code=403, detail=f"Cannot delete post with status '{post.status.value}'")

    await db.delete(post)
    await db.commit()
    return {"detail": "Post deleted"}


@router.put("/reorder")
async def reorder_posts(data: ReorderRequest, db: AsyncSession = Depends(get_async_db)):
    """Update order_index for multiple posts."""
    ids = [item.id for item in data.items]
    result = await db.execute(select(Post).where(Post.id.in_(ids)))
    posts = {str(p.id): p for p in result.scalars().all()}

    if len(posts) != len(ids):
        raise HTTPException(status_code=400, detail="Some posts not found")

    # Validate same page and editable status
    page_ids = {p.page_id for p in posts.values()}
    if len(page_ids) > 1:
        raise HTTPException(status_code=400, detail="All posts must belong to the same page")

    for p in posts.values():
        if p.status not in (PostStatus.draft, PostStatus.queued):
            raise HTTPException(status_code=400, detail=f"Post {p.id} has status '{p.status.value}', cannot reorder")

    for item in data.items:
        posts[item.id].order_index = item.order_index

    await db.commit()
    return {"detail": "Reordered"}


@router.post("/bulk", status_code=202, response_model=BulkImportResponse)
async def bulk_import(file: UploadFile = File(...)):
    """Trigger bulk import from CSV/JSON file. Returns task_id for polling."""
    if not file.content_type or file.content_type not in ("text/csv", "application/json"):
        if file.filename:
            if not (file.filename.endswith(".csv") or file.filename.endswith(".json")):
                raise HTTPException(status_code=400, detail="Only CSV or JSON files are accepted")

    content = await file.read()
    file_type = "csv" if (file.filename and file.filename.endswith(".csv")) or file.content_type == "text/csv" else "json"

    # TODO: dispatch Celery task in section-07
    # For now return a placeholder task_id
    return BulkImportResponse(task_id="placeholder-task-id")
