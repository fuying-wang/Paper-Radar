from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.linkedin_watchlist import (
    LinkedInWatchlistCreate,
    LinkedInWatchlistItem,
    LinkedInWatchlistListResponse,
)
from app.services.linkedin_watchlist_store import (
    create_linkedin_watchlist,
    delete_linkedin_watchlist,
    list_linkedin_watchlists,
)


router = APIRouter(prefix="/watchlists/linkedin", tags=["linkedin-watchlist"])


@router.get("", response_model=LinkedInWatchlistListResponse)
def get_linkedin_watchlists(db: Session = Depends(get_db)) -> LinkedInWatchlistListResponse:
    items = list_linkedin_watchlists(db)
    return LinkedInWatchlistListResponse(items=items)


@router.post("", response_model=LinkedInWatchlistItem, status_code=status.HTTP_201_CREATED)
def add_linkedin_watchlist(payload: LinkedInWatchlistCreate, db: Session = Depends(get_db)) -> LinkedInWatchlistItem:
    return create_linkedin_watchlist(db=db, payload=payload)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_linkedin_watchlist(watchlist_id: int, db: Session = Depends(get_db)) -> None:
    deleted = delete_linkedin_watchlist(db=db, watchlist_id=watchlist_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="watchlist item not found")


@router.get("/connector-spec")
def get_linkedin_connector_spec() -> dict:
    return {
        "phase": "phase_2",
        "status": "placeholder_only",
        "connector_interface": "LinkedInConnectorInterface.fetch_updates(watchlists, limit)",
        "expected_input": {
            "watchlists": ["institution", "lab", "author", "company_page"],
            "limit": "int",
        },
        "expected_output_fields": [
            "id",
            "text",
            "author",
            "created_at",
            "public_metrics",
            "post_url",
            "primary_topic",
            "topic_tags",
        ],
        "notes": "No automated LinkedIn fetch is enabled in current phase.",
    }
