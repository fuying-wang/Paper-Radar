from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SearchCacheModel(Base):
    __tablename__ = "paper_search_cache"
    __table_args__ = (UniqueConstraint("query", "sort_by", "paper_id", name="uq_cache_query_sort_paper"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    sort_by: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    paper = relationship("PaperModel", back_populates="cache_entries")
