from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.schedule_slot import ScheduleSlot
    from app.models.alert_log import AlertLog


class Page(UUIDTimestampMixin, Base):
    __tablename__ = "pages"

    fb_page_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, default="facebook", server_default="facebook")
    avatar_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    posts: Mapped[list["Post"]] = relationship(
        back_populates="page", cascade="all, delete-orphan"
    )
    schedule_slots: Mapped[list["ScheduleSlot"]] = relationship(
        back_populates="page", cascade="all, delete-orphan"
    )
    alert_logs: Mapped[list["AlertLog"]] = relationship(
        back_populates="page", cascade="all, delete-orphan"
    )
