from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PublishLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempted_at: Optional[datetime] = None
    page_name: str = ""
    content_preview: str = ""
    result: str
    fb_post_id: Optional[str] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class PublishLogResponse(BaseModel):
    entries: list[PublishLogEntry]
    total: int
