from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.analytics import (
    EngagementListResponse,
    HeatmapResponse,
    PostEngagementResponse,
    HeatmapCell,
)
from app.services.analytics_service import get_engagement_data, get_best_time_data

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/engagement", response_model=EngagementListResponse)
async def engagement_data(
    page_id: Optional[str] = None,
    days: int = 30,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
):
    """Get top posts by engagement."""
    data = await get_engagement_data(db, page_id=page_id, days=days, limit=limit)
    return EngagementListResponse(
        posts=[PostEngagementResponse(**d.__dict__) for d in data]
    )


@router.get("/best-time", response_model=HeatmapResponse)
async def best_time_data(
    page_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Get best posting time heatmap data."""
    data = await get_best_time_data(db, page_id=page_id)
    return HeatmapResponse(
        cells=[HeatmapCell(**d.__dict__) for d in data]
    )
