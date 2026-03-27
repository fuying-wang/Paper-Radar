from app.db.base import Base
from app.db.session import engine
from app.models import daily_digest, paper, research_topic, search_cache, topic_paper


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
