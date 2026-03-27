from app.db.base import Base
from app.db.session import engine
from app.models import daily_digest, linkedin_watchlist, paper, research_topic, search_cache, social_post, topic_paper


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
