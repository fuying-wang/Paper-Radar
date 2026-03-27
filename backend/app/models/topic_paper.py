from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TopicPaperModel(Base):
    __tablename__ = "topic_papers"
    __table_args__ = (UniqueConstraint("topic_id", "paper_id", name="uq_topic_paper"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("research_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    is_new: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    topic = relationship("ResearchTopicModel", back_populates="paper_links")
    paper = relationship("PaperModel", back_populates="topic_links")
