from __future__ import annotations

from datetime import date, timezone, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.daily_digest import DailyDigestModel
from app.models.paper import PaperModel
from app.models.research_topic import ResearchTopicModel
from app.models.topic_paper import TopicPaperModel
from app.services.aggregator import aggregate_papers
from app.services.paper_store import upsert_papers


def ensure_default_topics(db: Session) -> None:
    raw_topics = [topic.strip() for topic in settings.default_topics.split(",")]
    topics = [topic for topic in raw_topics if topic]
    if not topics:
        return
    existing_topics = db.execute(select(ResearchTopicModel.name)).scalars().all()
    existing_set = {name.strip().lower() for name in existing_topics}
    for topic in topics:
        if topic.lower() in existing_set:
            continue
        db.add(ResearchTopicModel(name=topic, is_active=True))
    db.commit()


def _build_daily_digest_content(topic_name: str, papers: list[PaperModel]) -> str:
    if not papers:
        return f"Daily Digest for {topic_name}: no new papers found today."
    lines = [f"Daily Digest for {topic_name}: {len(papers)} new papers."]
    for paper in papers[:10]:
        lines.append(f"- {paper.title} ({paper.venue}, {paper.year}) | citations: {paper.cited_by_count}")
    return "\n".join(lines)


def _save_daily_digest(
    db: Session,
    topic: ResearchTopicModel,
    digest_date: date,
    new_papers: list[PaperModel],
) -> DailyDigestModel:
    stmt = select(DailyDigestModel).where(
        DailyDigestModel.topic_id == topic.id,
        DailyDigestModel.digest_date == digest_date,
    )
    existing_digest = db.execute(stmt).scalars().first()
    paper_ids = [paper.id for paper in new_papers]
    content = _build_daily_digest_content(topic.name, new_papers)
    if existing_digest is None:
        digest = DailyDigestModel(
            topic_id=topic.id,
            digest_date=digest_date,
            new_paper_count=len(paper_ids),
            paper_ids=paper_ids,
            content=content,
        )
        db.add(digest)
        db.flush()
        return digest
    existing_digest.new_paper_count = len(paper_ids)
    existing_digest.paper_ids = paper_ids
    existing_digest.content = content
    db.flush()
    return existing_digest


def refresh_topic_papers(db: Session, topic: ResearchTopicModel, limit: int = 30) -> dict[str, int | str]:
    fetched = aggregate_papers(query=topic.name, limit=limit, sort_by="latest")
    upserted = upsert_papers(db, fetched)
    db.execute(update(TopicPaperModel).where(TopicPaperModel.topic_id == topic.id).values(is_new=False))

    now = datetime.now(timezone.utc)
    new_papers_for_topic: list[PaperModel] = []
    for paper_model, _ in upserted:
        link_stmt = select(TopicPaperModel).where(
            TopicPaperModel.topic_id == topic.id,
            TopicPaperModel.paper_id == paper_model.id,
        )
        existing_link = db.execute(link_stmt).scalars().first()
        if existing_link is None:
            db.add(
                TopicPaperModel(
                    topic_id=topic.id,
                    paper_id=paper_model.id,
                    is_new=True,
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )
            new_papers_for_topic.append(paper_model)
            continue
        existing_link.is_new = False
        existing_link.last_seen_at = now

    today = datetime.now(timezone.utc).date()
    _save_daily_digest(db, topic=topic, digest_date=today, new_papers=new_papers_for_topic)
    db.commit()
    return {
        "topic": topic.name,
        "fetched_count": len(fetched),
        "new_count": len(new_papers_for_topic),
    }


def run_daily_update(db: Session, limit: int | None = None) -> list[dict[str, int | str]]:
    ensure_default_topics(db)
    effective_limit = limit if limit is not None else settings.daily_update_limit
    topic_stmt = select(ResearchTopicModel).where(ResearchTopicModel.is_active.is_(True))
    topics = db.execute(topic_stmt).scalars().all()
    results: list[dict[str, int | str]] = []
    for topic in topics:
        results.append(refresh_topic_papers(db, topic=topic, limit=effective_limit))
    return results


def get_daily_digest(db: Session, topic_name: str, digest_date: date | None = None) -> DailyDigestModel | None:
    effective_date = digest_date or datetime.now(timezone.utc).date()
    stmt = (
        select(DailyDigestModel)
        .join(ResearchTopicModel, ResearchTopicModel.id == DailyDigestModel.topic_id)
        .where(
            ResearchTopicModel.name == topic_name,
            DailyDigestModel.digest_date == effective_date,
        )
    )
    return db.execute(stmt).scalars().first()
