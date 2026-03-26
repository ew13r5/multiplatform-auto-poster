from typing import Optional

from pydantic import BaseModel


class PublishNowResponse(BaseModel):
    post_id: str
    status: str
    fb_post_id: Optional[str] = None
    error_message: Optional[str] = None
