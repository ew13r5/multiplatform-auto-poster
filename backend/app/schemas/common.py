from typing import Any, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    checks: dict[str, bool]
    mode: str  # development, production


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    result: Optional[Any] = None
