import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.page import Page
    from app.models.publish_log import PublishLog
    from app.models.engagement import Engagement
class PostStatus(str, enum.Enum):
    draft = "draft"
    queued = "queued"
    publishing = "publishing"
    published = "published"
    failed = "failed"
class PostType(str, enum.Enum):
    text = "text"
    photo = "photo"
    link = "link"
class Post(UUIDTimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_page_order", "page_id", "order_index"),
        Index("ix_posts_status", "status"),
    )

    page_id: Mapped[uuid.UUID] = mapped_column(
        String(36), ForeignKey("pages.id"), nullable=False
    )
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type", native_enum=False),
        nullable=False,
        default=PostType.text,
    )
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", native_enum=False),
        nullable=False,
        default=PostStatus.draft,
    )
    image_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    link_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    fb_post_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    order_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    page: Mapped["Page"] = relationship(back_populates="posts")
    publish_logs: Mapped[list["PublishLog"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    engagements: Mapped[list["Engagement"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
