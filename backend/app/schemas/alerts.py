from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class AlertConfigUpdate(BaseModel):
    page_id: str
    telegram_enabled: bool = False
    telegram_chat_ids: List[str] = []
    email_enabled: bool = False
    email_recipients: List[str] = []
    dedup_window_minutes: int = 30


class AlertConfigResponse(BaseModel):
    page_id: str
    page_name: str = ""
    telegram_enabled: bool = False
    telegram_chat_ids: List[str] = []
    email_enabled: bool = False
    email_recipients: List[str] = []
    dedup_window_minutes: int = 30


class AlertLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    message: str
    severity: str
    channel: str
    page_name: Optional[str] = None
    sent_at: Optional[datetime] = None
    acknowledged: bool = False


class AlertLogResponse(BaseModel):
    entries: List[AlertLogEntry]
    total: int
