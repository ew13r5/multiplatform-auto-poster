from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class PostCreate(BaseModel):
    page_id: str
    content_text: str
    image_key: Optional[str] = None
    link_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    content_text: Optional[str] = None
    image_key: Optional[str] = None
    link_url: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("draft", "queued"):
            raise ValueError("Status can only be changed to 'draft' or 'queued'")
        return v


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_id: str
    content_text: str
    post_type: str
    status: str
    order_index: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    image_key: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    fb_post_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PostListResponse(BaseModel):
    posts: list[PostResponse]
    total: int


class ReorderItem(BaseModel):
    id: str
    order_index: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]


class BulkImportResponse(BaseModel):
    task_id: str
