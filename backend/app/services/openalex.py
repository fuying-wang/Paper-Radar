from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any

import httpx

from app.schemas.paper import Paper


logger = logging.getLogger(__name__)

OPENALEX_WORKS_API_URL = "https://api.openalex.org/works"
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_abstract(abstract_inverted_index: dict[str, list[int]] | None) -> str:
    if not abstract_inverted_index:
        return ""
    position_to_word: dict[int, str] = {}
    for word, positions in abstract_inverted_index.items():
        for position in positions:
            if position not in position_to_word:
                position_to_word[position] = word
    if not position_to_word:
        return ""
    ordered_words = [position_to_word[pos] for pos in sorted(position_to_word.keys())]
    return " ".join(ordered_words)


def _extract_authors(authorships: list[dict[str, Any]] | None) -> list[str]:
    if not authorships:
        return []
    authors: list[str] = []
    for authorship in authorships:
        author = authorship.get("author", {})
        display_name = _safe_str(author.get("display_name"))
        if display_name:
            authors.append(display_name)
    return authors


def _compute_scores(year: int, cited_by_count: int) -> tuple[float, float, float, float]:
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


def _to_paper(work: dict[str, Any]) -> Paper:
    paper_id = _safe_str(work.get("id")) or "unknown"
    title = _safe_str(work.get("title")) or "Untitled"
    authors = _extract_authors(work.get("authorships"))
    publication_year = int(work.get("publication_year") or 0)
    cited_by_count = int(work.get("cited_by_count") or 0)
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    venue = _safe_str(source.get("display_name")) or "Unknown Venue"
    abstract = _extract_abstract(work.get("abstract_inverted_index"))
    doi = _safe_str(work.get("doi"))
    url = (
        _safe_str(work.get("primary_location", {}).get("landing_page_url"))
        or _safe_str(work.get("primary_location", {}).get("pdf_url"))
        or doi
        or _safe_str(work.get("id"))
    )
    latest_score, hot_score, influential_score, final_score = _compute_scores(
        year=publication_year,
        cited_by_count=cited_by_count,
    )
    return Paper(
        id=paper_id,
        title=title,
        authors=authors,
        venue=venue,
        year=publication_year,
        abstract=abstract,
        cited_by_count=cited_by_count,
        url=url,
        latest_score=latest_score,
        hot_score=hot_score,
        influential_score=influential_score,
        final_score=final_score,
    )


def fetch_openalex_papers(query: str, per_page: int = 20) -> list[Paper]:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("query cannot be empty")
    safe_per_page = max(1, min(per_page, 100))
    params = {
        "search": cleaned_query,
        "per-page": safe_per_page,
        "sort": "cited_by_count:desc",
    }
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(OPENALEX_WORKS_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.TimeoutException as exc:
        logger.warning("openalex request timed out: %s", exc)
        return []
    except httpx.HTTPError as exc:
        logger.warning("openalex request failed: %s", exc)
        return []
    except ValueError as exc:
        logger.warning("openalex invalid json payload: %s", exc)
        return []

    results = payload.get("results", [])
    if not isinstance(results, list):
        logger.warning("openalex results is not a list")
        return []

    papers: list[Paper] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        try:
            papers.append(_to_paper(item))
        except (TypeError, ValueError) as exc:
            logger.warning("openalex item parse failed: %s", exc)
            continue
    return papers
