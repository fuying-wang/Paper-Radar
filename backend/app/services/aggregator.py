from __future__ import annotations

import math
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from app.schemas.paper import Paper
from app.services.arxiv import fetch_arxiv_papers
from app.services.journal_feeds import fetch_nature_journal_papers
from app.services.openalex import fetch_openalex_papers
from app.services.semantic_scholar import fetch_semantic_scholar_papers


SORT_FIELDS: dict[str, str] = {
    "latest": "latest_score",
    "hot": "hot_score",
    "influential": "influential_score",
    "social_buzz": "hot_score",
}


def _normalize_title(title: str) -> str:
    normalized = re.sub(r"\s+", " ", title.strip().lower())
    return normalized


def _dedupe_key(paper: Paper) -> tuple[str, int]:
    return _normalize_title(paper.title), paper.year


def _compute_scores(year: int, cited_by_count: int) -> tuple[float, float, float, float]:
    if year <= 0:
        return 0.0, 0.0, 0.0, 0.0
    current_year = datetime.utcnow().year
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


def _merge_paper(base: Paper, incoming: Paper) -> Paper:
    merged_authors = list(dict.fromkeys([*base.authors, *incoming.authors]))
    merged_citations = max(base.cited_by_count, incoming.cited_by_count)
    merged_venue = base.venue if base.venue else incoming.venue
    merged_year = base.year if base.year > 0 else incoming.year
    merged_abstract = base.abstract if len(base.abstract) >= len(incoming.abstract) else incoming.abstract
    merged_url = base.url if base.url else incoming.url
    merged_pdf_url = base.pdf_url if base.pdf_url else incoming.pdf_url
    merged_title = base.title if base.title else incoming.title
    merged_id = base.id if base.id and base.id != "unknown" else incoming.id
    merged_source_name = base.source_name if base.source_name != "unknown" else incoming.source_name
    merged_source_id = base.source_id if base.source_id else incoming.source_id
    merged_published_at = base.published_at if base.published_at else incoming.published_at
    merged_updated_at = base.updated_at if base.updated_at else incoming.updated_at
    merged_primary_category = base.primary_category if base.primary_category else incoming.primary_category
    merged_journal_name = base.journal_name if base.journal_name else incoming.journal_name

    latest_score, hot_score, influential_score, final_score = _compute_scores(
        year=merged_year,
        cited_by_count=merged_citations,
    )

    return Paper(
        id=merged_id,
        title=merged_title,
        authors=merged_authors,
        venue=merged_venue,
        year=merged_year,
        abstract=merged_abstract,
        cited_by_count=merged_citations,
        url=merged_url,
        latest_score=latest_score,
        hot_score=hot_score,
        influential_score=influential_score,
        final_score=final_score,
        source_name=merged_source_name,
        source_id=merged_source_id,
        published_at=merged_published_at,
        updated_at=merged_updated_at,
        journal_name=merged_journal_name,
        primary_category=merged_primary_category,
        pdf_url=merged_pdf_url,
    )


def aggregate_papers(query: str, limit: int = 20, sort_by: str = "latest", source: str = "all") -> list[Paper]:
    cleaned_sort_by = sort_by.strip().lower()
    if cleaned_sort_by not in SORT_FIELDS:
        raise ValueError("sort_by must be one of: latest, hot, influential, social_buzz")
    cleaned_source = source.strip().lower()
    supported_sources = {"all", "openalex", "semantic_scholar", "arxiv", "journal"}
    if cleaned_source not in supported_sources:
        raise ValueError("source must be one of: all, openalex, semantic_scholar, arxiv, journal")

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures: dict[str, object] = {}
        if cleaned_source in {"all", "openalex"}:
            futures["openalex"] = executor.submit(fetch_openalex_papers, query=query, per_page=limit)
        if cleaned_source in {"all", "semantic_scholar"}:
            futures["semantic_scholar"] = executor.submit(fetch_semantic_scholar_papers, query=query, limit=limit)
        if cleaned_source in {"all", "arxiv"}:
            futures["arxiv"] = executor.submit(fetch_arxiv_papers, query=query, limit=limit)
        if cleaned_source in {"all", "journal"}:
            futures["journal"] = executor.submit(fetch_nature_journal_papers, query=query, limit=limit)

        openalex_papers = futures["openalex"].result() if "openalex" in futures else []
        semantic_papers = futures["semantic_scholar"].result() if "semantic_scholar" in futures else []
        arxiv_papers = futures["arxiv"].result() if "arxiv" in futures else []
        journal_papers = futures["journal"].result() if "journal" in futures else []

    merged_map: dict[tuple[str, int], Paper] = {}
    for paper in [*openalex_papers, *semantic_papers, *arxiv_papers, *journal_papers]:
        key = _dedupe_key(paper)
        if key in merged_map:
            merged_map[key] = _merge_paper(merged_map[key], paper)
        else:
            latest_score, hot_score, influential_score, final_score = _compute_scores(
                year=paper.year,
                cited_by_count=paper.cited_by_count,
            )
            merged_map[key] = Paper(
                id=paper.id,
                title=paper.title,
                authors=paper.authors,
                venue=paper.venue,
                year=paper.year,
                abstract=paper.abstract,
                cited_by_count=paper.cited_by_count,
                url=paper.url,
                latest_score=latest_score,
                hot_score=hot_score,
                influential_score=influential_score,
                final_score=final_score,
                source_name=paper.source_name,
                source_id=paper.source_id,
                published_at=paper.published_at,
                updated_at=paper.updated_at,
                journal_name=paper.journal_name,
                primary_category=paper.primary_category,
                pdf_url=paper.pdf_url,
                primary_topic=paper.primary_topic,
                topic_tags=paper.topic_tags,
            )

    sort_field = SORT_FIELDS[cleaned_sort_by]
    papers = list(merged_map.values())
    papers.sort(
        key=lambda p: (getattr(p, sort_field), p.final_score, p.cited_by_count),
        reverse=True,
    )
    return papers
