from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaperModel(Base):
    __tablename__ = "papers"
    __table_args__ = (UniqueConstraint("source_name", "source_id", name="uq_papers_source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_name: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")
    venue: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    year: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cited_by_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    doi: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_published_at: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    source_updated_at: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    journal_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    primary_category: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    pdf_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    latest_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hot_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    influential_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    primary_topic: Mapped[str] = mapped_column(String(64), nullable=False, default="General AI", index=True)
    topic_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cache_entries = relationship("SearchCacheModel", back_populates="paper", cascade="all, delete-orphan")
    topic_links = relationship("TopicPaperModel", back_populates="paper", cascade="all, delete-orphan")
