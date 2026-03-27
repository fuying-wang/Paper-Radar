from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.paper import Paper
from app.services.aggregator import aggregate_papers
from app.services.paper_store import get_cached_papers, save_search_cache


def search_papers_with_cache(
    db: Session,
    query: str,
    sort_by: str = "latest",
    limit: int = 20,
    source: str = "all",
) -> list[Paper]:
    cache_query = query if source == "all" else f"{query}::source={source}"
    cached = get_cached_papers(
        db=db,
        query=cache_query,
        sort_by=sort_by,
        ttl_minutes=settings.cache_ttl_minutes,
        limit=limit,
    )
    if cached:
        return cached
    fetched = aggregate_papers(query=query, limit=limit, sort_by=sort_by, source=source)
    if not fetched:
        return []
    return save_search_cache(db=db, query=cache_query, sort_by=sort_by, papers=fetched)
