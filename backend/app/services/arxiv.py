from __future__ import annotations

import logging
import math
import xml.etree.ElementTree as ET
from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.paper import Paper


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _get_text(element: ET.Element | None, path: str) -> str:
    if element is None:
        return ""
    found = element.find(path, ATOM_NS)
    if found is None or found.text is None:
        return ""
    return found.text.strip()


def _extract_arxiv_id(id_url: str) -> str:
    if "/abs/" in id_url:
        return id_url.split("/abs/", 1)[1].strip()
    return id_url.strip()


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


def _entry_to_paper(entry: ET.Element) -> Paper:
    title = _get_text(entry, "atom:title")
    abstract = _get_text(entry, "atom:summary")
    published = _get_text(entry, "atom:published")
    updated = _get_text(entry, "atom:updated")
    primary_category = ""
    category_element = entry.find("arxiv:primary_category", ATOM_NS)
    if category_element is not None:
        primary_category = category_element.attrib.get("term", "").strip()

    author_elements = entry.findall("atom:author", ATOM_NS)
    authors = []
    for author in author_elements:
        name = _get_text(author, "atom:name")
        if name:
            authors.append(name)

    abs_url = _get_text(entry, "atom:id")
    arxiv_id = _extract_arxiv_id(abs_url)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else ""
    year = 0
    if published:
        try:
            year = datetime.fromisoformat(published.replace("Z", "+00:00")).year
        except ValueError:
            year = 0
    latest_score, hot_score, influential_score, final_score = _compute_scores(year=year, cited_by_count=0)

    return Paper(
        id=f"arxiv:{arxiv_id}" if arxiv_id else "arxiv:unknown",
        title=title or "Untitled",
        authors=authors,
        venue="arXiv",
        year=year,
        abstract=abstract,
        cited_by_count=0,
        url=abs_url or f"https://arxiv.org/abs/{arxiv_id}",
        latest_score=latest_score,
        hot_score=hot_score,
        influential_score=influential_score,
        final_score=final_score,
        source_name="arxiv",
        source_id=arxiv_id,
        published_at=published,
        updated_at=updated,
        primary_category=primary_category,
        pdf_url=pdf_url,
    )


def fetch_arxiv_papers(query: str, limit: int = 20) -> list[Paper]:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("query cannot be empty")
    safe_limit = max(1, min(limit, settings.arxiv_max_results))
    params = {
        "search_query": f"all:{cleaned_query}",
        "start": 0,
        "max_results": safe_limit,
        "sortBy": settings.arxiv_sort_by,
        "sortOrder": settings.arxiv_sort_order,
    }
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(settings.arxiv_api_url, params=params)
            response.raise_for_status()
            root = ET.fromstring(response.text)
    except httpx.TimeoutException as exc:
        logger.warning("arxiv request timed out: %s", exc)
        return []
    except httpx.HTTPError as exc:
        logger.warning("arxiv request failed: %s", exc)
        return []
    except ET.ParseError as exc:
        logger.warning("arxiv xml parse failed: %s", exc)
        return []

    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        try:
            papers.append(_entry_to_paper(entry))
        except Exception as exc:
            logger.warning("arxiv entry parse failed: %s", exc)
            continue
    return papers
