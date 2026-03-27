from sqlalchemy.orm import Session

from app.schemas.social import SocialPost
from app.services.social_store import upsert_social_posts
from app.services.x_connector import fetch_x_recent_posts


def search_social_buzz(db: Session, query: str, limit: int = 10) -> list[SocialPost]:
    posts = fetch_x_recent_posts(query=query, limit=limit)
    if not posts:
        return []
    return upsert_social_posts(db=db, query=query, posts=posts)
