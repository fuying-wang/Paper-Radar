from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.models.paper import PaperModel
from app.models.search_cache import SearchCacheModel
from app.schemas.paper import Paper
from app.services.topic_classifier import classify_paper_topics


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _extract_source(paper: Paper) -> tuple[str, str]:
    if paper.source_name and paper.source_id:
        return paper.source_name.strip().lower(), paper.source_id.strip()
    if ":" in paper.id:
        source_name, source_id = paper.id.split(":", 1)
        return source_name.strip().lower(), source_id.strip()
    return "unknown", paper.id.strip()


def _extract_doi(url: str) -> str:
    marker = "doi.org/"
    if marker in url:
        return url.split(marker, 1)[1].strip()
    return ""


def _compute_scores(year: int, cited_by_count: int) -> tuple[float, float, float, float]:
    if year <= 0:
        return 0.0, 0.0, 0.0, 0.0
    current_year = datetime.now(timezone.utc).year
    year_gap = max(current_year - year, 0)
    latest_score = max(0.0, 1.0 - (year_gap / 10.0))
    influential_score = min(1.0, math.log1p(max(cited_by_count, 0)) / math.log(1001))
    yearly_citation_velocity = cited_by_count / max(year_gap + 1, 1)
    hot_score = min(1.0, math.log1p(max(yearly_citation_velocity, 0.0)) / math.log(101))
    final_score = round(latest_score * 0.35 + hot_score * 0.35 + influential_score * 0.30, 4)
    return (
        round(latest_score, 4),
        round(hot_score, 4),
        round(influential_score, 4),
        final_score,
    )


def _paper_from_model(model: PaperModel) -> Paper:
    return Paper(
        id=f"{model.source_name}:{model.source_id}",
        title=model.title,
        authors=model.authors,
        venue=model.venue,
        year=model.year,
        abstract=model.abstract,
        cited_by_count=model.cited_by_count,
        url=model.url,
        latest_score=model.latest_score,
        hot_score=model.hot_score,
        influential_score=model.influential_score,
        final_score=model.final_score,
        source_name=model.source_name,
        source_id=model.source_id,
        published_at=model.source_published_at,
        updated_at=model.source_updated_at,
        journal_name=model.journal_name,
        primary_category=model.primary_category,
        pdf_url=model.pdf_url,
        primary_topic=model.primary_topic,
        topic_tags=model.topic_tags,
    )


def get_cached_papers(
    db: Session,
    query: str,
    sort_by: str,
    ttl_minutes: int,
    limit: int,
) -> list[Paper]:
    normalized_query = _normalize_text(query)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=ttl_minutes)
    score_field = {
        "latest": PaperModel.latest_score,
        "hot": PaperModel.hot_score,
        "influential": PaperModel.influential_score,
    }.get(sort_by, PaperModel.latest_score)

    stmt = (
        select(PaperModel)
        .join(SearchCacheModel, SearchCacheModel.paper_id == PaperModel.id)
        .where(
            SearchCacheModel.query == normalized_query,
            SearchCacheModel.sort_by == sort_by,
            SearchCacheModel.created_at >= cutoff,
        )
        .order_by(score_field.desc(), PaperModel.final_score.desc(), PaperModel.cited_by_count.desc())
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    return [_paper_from_model(row) for row in rows]


def upsert_single_paper(db: Session, paper: Paper) -> tuple[PaperModel, bool]:
    source_name, source_id = _extract_source(paper)
    normalized_title = _normalize_text(paper.title)
    latest_score, hot_score, influential_score, final_score = _compute_scores(paper.year, paper.cited_by_count)
    topic_assignment = classify_paper_topics(paper)

    stmt = select(PaperModel).where(
        or_(
            (PaperModel.source_name == source_name) & (PaperModel.source_id == source_id),
            (func.lower(PaperModel.title) == normalized_title) & (PaperModel.year == paper.year),
        )
    )
    existing = db.execute(stmt).scalars().first()
    if existing is None:
        existing = PaperModel(
            source_id=source_id,
            source_name=source_name,
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            venue=paper.venue,
            year=paper.year,
            cited_by_count=paper.cited_by_count,
            doi=_extract_doi(paper.url),
            url=paper.url,
            source_published_at=paper.published_at,
            source_updated_at=paper.updated_at,
            journal_name=paper.journal_name,
            primary_category=paper.primary_category,
            pdf_url=paper.pdf_url,
            latest_score=latest_score,
            hot_score=hot_score,
            influential_score=influential_score,
            final_score=final_score,
            primary_topic=topic_assignment.primary_topic,
            topic_tags=topic_assignment.secondary_topics,
        )
        db.add(existing)
        db.flush()
        return existing, True

    existing.source_id = source_id if source_id else existing.source_id
    existing.source_name = source_name if source_name else existing.source_name
    existing.title = paper.title if paper.title else existing.title
    existing.authors = paper.authors if paper.authors else existing.authors
    existing.abstract = paper.abstract if len(paper.abstract) >= len(existing.abstract) else existing.abstract
    existing.venue = paper.venue if paper.venue else existing.venue
    existing.year = paper.year if paper.year > 0 else existing.year
    existing.cited_by_count = max(existing.cited_by_count, paper.cited_by_count)
    existing.doi = existing.doi or _extract_doi(paper.url)
    existing.url = paper.url if paper.url else existing.url
    existing.source_published_at = paper.published_at if paper.published_at else existing.source_published_at
    existing.source_updated_at = paper.updated_at if paper.updated_at else existing.source_updated_at
    existing.journal_name = paper.journal_name if paper.journal_name else existing.journal_name
    existing.primary_category = paper.primary_category if paper.primary_category else existing.primary_category
    existing.pdf_url = paper.pdf_url if paper.pdf_url else existing.pdf_url
    existing.latest_score = latest_score
    existing.hot_score = hot_score
    existing.influential_score = influential_score
    existing.final_score = final_score
    existing.primary_topic = topic_assignment.primary_topic
    existing.topic_tags = topic_assignment.secondary_topics
    db.flush()
    return existing, False


def upsert_papers(db: Session, papers: list[Paper]) -> list[tuple[PaperModel, bool]]:
    results: list[tuple[PaperModel, bool]] = []
    for paper in papers:
        results.append(upsert_single_paper(db, paper))
    return results


def save_search_cache(
    db: Session,
    query: str,
    sort_by: str,
    papers: list[Paper],
) -> list[Paper]:
    normalized_query = _normalize_text(query)
    db.execute(
        delete(SearchCacheModel).where(
            SearchCacheModel.query == normalized_query,
            SearchCacheModel.sort_by == sort_by,
        )
    )

    persisted_map: dict[int, PaperModel] = {}
    for paper in papers:
        persisted, _ = upsert_single_paper(db, paper)
        persisted_map[persisted.id] = persisted

    for item in persisted_map.values():
        cache = SearchCacheModel(query=normalized_query, sort_by=sort_by, paper_id=item.id)
        db.add(cache)

    db.commit()
    return [_paper_from_model(item) for item in persisted_map.values()]
