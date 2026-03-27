from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SocialPostModel(Base):
    __tablename__ = "social_posts"
    __table_args__ = (UniqueConstraint("source_name", "source_post_id", name="uq_social_source_post"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="x")
    source_post_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    query: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    post_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    public_metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    primary_topic: Mapped[str] = mapped_column(String(64), nullable=False, default="General AI", index=True)
    topic_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    inserted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
