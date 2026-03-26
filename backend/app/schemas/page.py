from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PageConnect(BaseModel):
    fb_page_id: str
    name: str
    access_token: str
    category: Optional[str] = None


class PageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fb_page_id: str
    name: str
    category: Optional[str] = None
    token_status: str = "configured"
    queued_count: int = 0
    last_published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class PageListResponse(BaseModel):
    pages: list[PageResponse]
