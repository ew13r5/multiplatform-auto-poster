from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.page import Page
from app.models.post import Post, PostStatus
from app.schemas.page import PageConnect, PageResponse, PageListResponse
from app.services.encryption import encrypt_token

router = APIRouter(prefix="/pages", tags=["pages"])


@router.post("/connect", status_code=201, response_model=PageResponse)
async def connect_page(data: PageConnect, db: AsyncSession = Depends(get_async_db)):
    """Add a Facebook Page with encrypted token."""
    encrypted = encrypt_token(data.access_token)
    page = Page(
        fb_page_id=data.fb_page_id,
        name=data.name,
        category=data.category,
        access_token_encrypted=encrypted,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return PageResponse(
        id=str(page.id),
        fb_page_id=page.fb_page_id,
        name=page.name,
        category=page.category,
        token_status="configured",
        queued_count=0,
        last_published_at=None,
        created_at=page.created_at,
    )


@router.get("", response_model=PageListResponse)
async def list_pages(db: AsyncSession = Depends(get_async_db)):
    """List all connected pages with queue and publish stats."""
    result = await db.execute(select(Page))
    pages = result.scalars().all()

    page_responses = []
    for page in pages:
        q_count = await db.execute(
            select(func.count(Post.id)).where(
                Post.page_id == page.id, Post.status == PostStatus.queued
            )
        )
        queued_count = q_count.scalar() or 0

        q_last = await db.execute(
            select(func.max(Post.published_at)).where(
                Post.page_id == page.id, Post.status == PostStatus.published
            )
        )
        last_published_at = q_last.scalar()

        token_status = "configured" if page.access_token_encrypted else "missing"
        page_responses.append(
            PageResponse(
                id=str(page.id),
                fb_page_id=page.fb_page_id,
                name=page.name,
                category=page.category,
                token_status=token_status,
                queued_count=queued_count,
                last_published_at=last_published_at,
                created_at=page.created_at,
            )
        )
    return PageListResponse(pages=page_responses)


@router.post("/{page_id}/verify-token", status_code=501)
async def verify_token(page_id: str):
    """Stub — token verification implemented in split 02."""
    return {"detail": "Not implemented. Token verification handled in a later split."}
