from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.digest import DailyDigestResponse
from app.schemas.paper import SearchPapersResponse
from app.schemas.summary import SearchTrendSummaryResponse
from app.services.daily_update import get_daily_digest
from app.services.search_service import search_papers_with_cache
from app.services.summarize import generate_trend_summary, summarize_papers


router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/search", response_model=SearchPapersResponse)
def search_papers(
    keyword: str = Query(..., min_length=1),
    sort_by: Literal["latest", "hot", "influential", "social_buzz"] = Query("latest"),
    source: Literal["all", "openalex", "semantic_scholar", "arxiv", "journal"] = Query("all"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SearchPapersResponse:
    papers = search_papers_with_cache(db=db, query=keyword, sort_by=sort_by, limit=limit, source=source)
    return SearchPapersResponse(keyword=keyword, papers=papers)


@router.get("/search/trend-summary", response_model=SearchTrendSummaryResponse)
def get_search_trend_summary(
    keyword: str = Query(..., min_length=1),
    source: Literal["all", "openalex", "semantic_scholar", "arxiv", "journal"] = Query("all"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SearchTrendSummaryResponse:
    papers = search_papers_with_cache(db=db, query=keyword, sort_by="hot", limit=limit, source=source)
    trend_summary = generate_trend_summary(papers)
    paper_summaries = summarize_papers(papers)
    return SearchTrendSummaryResponse(
        keyword=keyword,
        trend_summary=trend_summary,
        paper_summaries=paper_summaries,
    )


@router.get("/digest/daily", response_model=DailyDigestResponse)
def get_topic_daily_digest(
    topic: str = Query(..., min_length=1),
    digest_date: date | None = Query(None),
    db: Session = Depends(get_db),
) -> DailyDigestResponse:
    digest = get_daily_digest(db=db, topic_name=topic, digest_date=digest_date)
    if digest is None:
        return DailyDigestResponse(
            topic=topic,
            digest_date=digest_date or date.today(),
            new_paper_count=0,
            paper_ids=[],
            content=f"Daily Digest for {topic}: no records found.",
        )
    return DailyDigestResponse(
        topic=topic,
        digest_date=digest.digest_date,
        new_paper_count=digest.new_paper_count,
        paper_ids=digest.paper_ids,
        content=digest.content,
    )
