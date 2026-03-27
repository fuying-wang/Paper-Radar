from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.linkedin_watchlist import LinkedInWatchlistModel
from app.schemas.linkedin_watchlist import LinkedInWatchlistCreate, LinkedInWatchlistItem


def _to_schema(model: LinkedInWatchlistModel) -> LinkedInWatchlistItem:
    return LinkedInWatchlistItem(
        id=model.id,
        entity_type=model.entity_type,
        name=model.name,
        linkedin_url=model.linkedin_url,
        notes=model.notes,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def list_linkedin_watchlists(db: Session) -> list[LinkedInWatchlistItem]:
    stmt = select(LinkedInWatchlistModel).order_by(LinkedInWatchlistModel.created_at.desc())
    rows = db.execute(stmt).scalars().all()
    return [_to_schema(row) for row in rows]


def create_linkedin_watchlist(db: Session, payload: LinkedInWatchlistCreate) -> LinkedInWatchlistItem:
    item = LinkedInWatchlistModel(
        entity_type=payload.entity_type,
        name=payload.name,
        linkedin_url=str(payload.linkedin_url),
        notes=payload.notes,
        is_active=payload.is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_schema(item)


def delete_linkedin_watchlist(db: Session, watchlist_id: int) -> bool:
    stmt = delete(LinkedInWatchlistModel).where(LinkedInWatchlistModel.id == watchlist_id)
    result = db.execute(stmt)
    db.commit()
    return (result.rowcount or 0) > 0
