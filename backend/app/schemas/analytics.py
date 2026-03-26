from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PostEngagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    post_id: str
    content_preview: str
    page_name: str
    likes: int
    comments: int
    shares: int
    published_at: Optional[datetime] = None


class EngagementListResponse(BaseModel):
    posts: list[PostEngagementResponse]


class HeatmapCell(BaseModel):
    day: int = Field(ge=0, le=6)
    hour: int = Field(ge=0, le=23)
    avg_engagement: float


class HeatmapResponse(BaseModel):
    cells: list[HeatmapCell]
