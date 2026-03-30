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
    """Add a Facebook/Telegram Page with encrypted token."""
    if data.platform not in ("facebook", "telegram", "twitter"):
        raise HTTPException(status_code=400, detail="Platform must be 'facebook', 'telegram', or 'twitter'")
    encrypted = encrypt_token(data.access_token)
    page = Page(
        fb_page_id=data.fb_page_id,
        name=data.name,
        category=data.category,
        platform=data.platform,
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
        platform=page.platform,
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
                platform=getattr(page, "platform", "facebook"),
                token_status=token_status,
                queued_count=queued_count,
                last_published_at=last_published_at,
                created_at=page.created_at,
            )
        )
    return PageListResponse(pages=page_responses)


@router.post("/{page_id}/verify-token")
async def verify_token(page_id: str, db: AsyncSession = Depends(get_async_db)):
    """Verify token by calling platform-specific API."""
    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    if not page.access_token_encrypted:
        return {"valid": False, "error": "No token stored"}

    from app.services.encryption import decrypt_token
    try:
        token = decrypt_token(page.access_token_encrypted)
    except Exception:
        return {"valid": False, "error": "Token decryption failed"}

    platform = getattr(page, "platform", "facebook")

    if platform == "telegram":
        import httpx
        try:
            resp = await httpx.AsyncClient().get(
                f"https://api.telegram.org/bot{token}/getMe", timeout=10.0
            )
            data = resp.json()
            if data.get("ok"):
                bot = data["result"]
                return {"valid": True, "bot_name": bot.get("first_name"), "username": bot.get("username")}
            return {"valid": False, "error": data.get("description", "Invalid token")}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    else:
        return {"valid": False, "error": "Facebook token verification not configured"}
