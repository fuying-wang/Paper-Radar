from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any

import httpx

from app.schemas.paper import Paper


logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_SEARCH_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_authors(authors: list[dict[str, Any]] | None) -> list[str]:
    if not authors:
        return []
    names: list[str] = []
    for author in authors:
        name = _safe_str(author.get("name"))
        if name:
            names.append(name)
    return names


def _compute_scores(year: int, citation_count: int) -> tuple[float, float, float, float]:
    if year <= 0:
        return 0.0, 0.0, 0.0, 0.0
    current_year = datetime.utcnow().year
    year_gap = max(current_year - year, 0)
    latest_score = max(0.0, 1.0 - (year_gap / 10.0))
    influential_score = min(1.0, math.log1p(max(citation_count, 0)) / math.log(1001))
    yearly_velocity = citation_count / max(year_gap + 1, 1)
    hot_score = min(1.0, math.log1p(max(yearly_velocity, 0.0)) / math.log(101))
    final_score = round(latest_score * 0.35 + hot_score * 0.35 + influential_score * 0.30, 4)
    return (
        round(latest_score, 4),
        round(hot_score, 4),
        round(influential_score, 4),
        final_score,
    )


def _to_paper(item: dict[str, Any]) -> Paper:
    source_id = _safe_str(item.get("paperId"))
    if not source_id:
        source_id = _safe_str(item.get("url")) or "unknown"
    paper_id = f"semantic_scholar:{source_id}"
    title = _safe_str(item.get("title"))
    authors = _extract_authors(item.get("authors"))
    abstract = _safe_str(item.get("abstract"))
    venue = _safe_str(item.get("venue"))
    year = int(item.get("year") or 0)
    citation_count = int(item.get("citationCount") or 0)
    url = _safe_str(item.get("url"))
    latest_score, hot_score, influential_score, final_score = _compute_scores(
        year=year,
        citation_count=citation_count,
    )
    return Paper(
        id=paper_id,
        title=title,
        authors=authors,
        venue=venue,
        year=year,
        abstract=abstract,
        cited_by_count=citation_count,
        url=url,
        latest_score=latest_score,
        hot_score=hot_score,
        influential_score=influential_score,
        final_score=final_score,
        source_name="semantic_scholar",
        source_id=source_id,
    )


def fetch_semantic_scholar_papers(query: str, limit: int = 20) -> list[Paper]:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("query cannot be empty")
    safe_limit = max(1, min(limit, 100))
    params = {
        "query": cleaned_query,
        "limit": safe_limit,
        "fields": "paperId,title,authors,abstract,venue,year,citationCount,url",
    }
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(SEMANTIC_SCHOLAR_SEARCH_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.TimeoutException as exc:
        logger.warning("semantic scholar request timed out: %s", exc)
        return []
    except httpx.HTTPError as exc:
        logger.warning("semantic scholar request failed: %s", exc)
        return []
    except ValueError as exc:
        logger.warning("semantic scholar invalid json payload: %s", exc)
        return []

    items = payload.get("data", [])
    if not isinstance(items, list):
        return []

    papers: list[Paper] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            papers.append(_to_paper(item))
        except (TypeError, ValueError):
            continue
    return papers
