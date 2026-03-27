from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyDigestModel(Base):
    __tablename__ = "daily_digests"
    __table_args__ = (UniqueConstraint("topic_id", "digest_date", name="uq_digest_topic_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("research_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    digest_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    new_paper_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    paper_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    topic = relationship("ResearchTopicModel", back_populates="digests")
