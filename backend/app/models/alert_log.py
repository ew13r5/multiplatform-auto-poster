import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.page import Page
class AlertChannel(str, enum.Enum):
    telegram = "telegram"
    email = "email"
    in_app = "in_app"
class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"
class AlertLog(UUIDTimestampMixin, Base):
    __tablename__ = "alert_logs"

    type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        String(36), ForeignKey("pages.id"), nullable=True
    )
    channel: Mapped[AlertChannel] = mapped_column(
        Enum(AlertChannel, name="alert_channel", native_enum=False), nullable=False
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity", native_enum=False), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    page: Mapped[Optional["Page"]] = relationship(back_populates="alert_logs")
