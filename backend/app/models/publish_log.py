import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.post import Post
class PublishResult(str, enum.Enum):
    success = "success"
    retriable_error = "retriable_error"
    permanent_error = "permanent_error"
class PublishLog(UUIDTimestampMixin, Base):
    __tablename__ = "publish_log"
    __table_args__ = (Index("ix_publish_log_attempted_at", "attempted_at"),)

    post_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("posts.id"), nullable=False
    )
    page_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("pages.id"), nullable=False
    )
    result: Mapped[PublishResult] = mapped_column(
        Enum(PublishResult, name="publish_result", native_enum=False), nullable=False
    )
    fb_post_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )

    post: Mapped["Post"] = relationship(back_populates="publish_logs")
