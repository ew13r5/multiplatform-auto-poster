from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleSlotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_id: str
    day_of_week: int = Field(ge=0, le=6)
    time_utc: str
    timezone: str = "UTC"
    enabled: bool = True


class ScheduleUpdateRequest(BaseModel):
    slots: list[ScheduleSlotSchema]


class PauseRequest(BaseModel):
    paused: bool


class PauseResponse(BaseModel):
    paused: bool
