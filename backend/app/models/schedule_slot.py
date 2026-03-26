import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.page import Page
class ScheduleSlot(UUIDTimestampMixin, Base):
    __tablename__ = "schedule_slots"
    __table_args__ = (Index("ix_schedule_slots_page_day", "page_id", "day_of_week"),)

    page_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("pages.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    time_utc: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String, nullable=False, default="UTC")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    page: Mapped["Page"] = relationship(back_populates="schedule_slots")
