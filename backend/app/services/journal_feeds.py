from __future__ import annotations

import logging
import math
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx

from app.core.config import settings
from app.schemas.paper import Paper


logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _strip_html(value: str) -> str:
    return _clean_text(re.sub(r"<[^>]+>", " ", value))


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _find_child_text(item: ET.Element, child_local_name: str) -> str:
    for child in list(item):
        if _local_name(child.tag) == child_local_name:
            return _clean_text(child.text)
    return ""


def _parse_date(value: str) -> datetime | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    try:
        return parsedate_to_datetime(cleaned)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except ValueError:
        return None


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


def _match_query(query: str, title: str, summary: str, journal_name: str) -> bool:
    tokens = [token.strip().lower() for token in query.split() if token.strip()]
    if not tokens:
        return True
    text = f"{title} {summary} {journal_name}".lower()
    return any(token in text for token in tokens)


def _build_paper(
    journal_name: str,
    source_id: str,
    title: str,
    summary: str,
    published_at: str,
    article_url: str,
) -> Paper:
    published_date = _parse_date(published_at)
    year = published_date.year if published_date else 0
    latest_score, hot_score, influential_score, final_score = _compute_scores(year=year, cited_by_count=0)
    return Paper(
        id=f"journal:{source_id}",
        title=title or "Untitled",
        authors=[],
        venue=journal_name,
        year=year,
        abstract=summary,
        cited_by_count=0,
        url=article_url,
        latest_score=latest_score,
        hot_score=hot_score,
        influential_score=influential_score,
        final_score=final_score,
        source_name="journal",
        source_id=source_id,
        published_at=published_at,
        journal_name=journal_name,
    )


def _parse_rss_items(root: ET.Element, journal_name: str, query: str) -> list[Paper]:
    papers: list[Paper] = []
    for item in root.iter():
        if _local_name(item.tag) != "item":
            continue
        title = _find_child_text(item, "title")
        summary = _strip_html(_find_child_text(item, "description"))
        published_at = _find_child_text(item, "pubDate") or _find_child_text(item, "date")
        article_url = _find_child_text(item, "link")
        source_id = article_url.rsplit("/", 1)[-1] or title.lower().replace(" ", "-")
        if not _match_query(query, title, summary, journal_name):
            continue
        papers.append(
            _build_paper(
                journal_name=journal_name,
                source_id=source_id,
                title=title,
                summary=summary,
                published_at=published_at,
                article_url=article_url,
            )
        )
    return papers


def _parse_atom_entries(root: ET.Element, journal_name: str, query: str) -> list[Paper]:
    papers: list[Paper] = []
    for entry in root.findall(".//atom:entry", ATOM_NS):
        title = _clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
        summary = _strip_html(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
        published_at = _clean_text(entry.findtext("atom:published", default="", namespaces=ATOM_NS))
        link_elements = entry.findall("atom:link", ATOM_NS)
        article_url = ""
        for link in link_elements:
            href = _clean_text(link.attrib.get("href"))
            if href:
                article_url = href
                break
        source_id = (
            _clean_text(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
            or article_url.rsplit("/", 1)[-1]
            or title.lower().replace(" ", "-")
        )
        if not _match_query(query, title, summary, journal_name):
            continue
        papers.append(
            _build_paper(
                journal_name=journal_name,
                source_id=source_id,
                title=title,
                summary=summary,
                published_at=published_at,
                article_url=article_url,
            )
        )
    return papers


def fetch_nature_journal_papers(query: str, limit: int = 20) -> list[Paper]:
    cleaned_query = query.strip()
    papers: list[Paper] = []
    for journal_name, feed_url in settings.nature_feeds.items():
        try:
            with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
                response = client.get(feed_url)
                response.raise_for_status()
                root = ET.fromstring(response.text)
        except (httpx.HTTPError, ET.ParseError) as exc:
            logger.warning("journal feed fetch failed for %s: %s", journal_name, exc)
            continue

        current_items = _parse_rss_items(root, journal_name=journal_name, query=cleaned_query)
        if not current_items:
            current_items = _parse_atom_entries(root, journal_name=journal_name, query=cleaned_query)
        papers.extend(current_items)

    papers.sort(key=lambda item: item.published_at, reverse=True)
    max_items = max(1, min(limit, settings.journal_feed_max_items))
    return papers[:max_items]
