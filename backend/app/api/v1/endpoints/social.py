from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.social import SearchSocialResponse
from app.services.social_service import search_social_buzz


router = APIRouter(prefix="/social", tags=["social"])


@router.get("/search", response_model=SearchSocialResponse)
def search_social(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SearchSocialResponse:
    posts = search_social_buzz(db=db, query=keyword, limit=limit)
    return SearchSocialResponse(keyword=keyword, posts=posts)
