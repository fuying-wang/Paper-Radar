import json
import os


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/paper_retrieval",
        )
        self.cache_ttl_minutes = int(os.getenv("CACHE_TTL_MINUTES", "60"))
        self.daily_update_hour = int(os.getenv("DAILY_UPDATE_HOUR", "2"))
        self.daily_update_minute = int(os.getenv("DAILY_UPDATE_MINUTE", "0"))
        self.daily_update_limit = int(os.getenv("DAILY_UPDATE_LIMIT", "30"))
        self.default_topics = os.getenv(
            "DEFAULT_TOPICS",
            "machine learning,natural language processing,computer vision",
        )
        self.run_daily_update_on_startup = os.getenv("RUN_DAILY_UPDATE_ON_STARTUP", "false").lower() == "true"
        self.arxiv_api_url = os.getenv("ARXIV_API_URL", "https://export.arxiv.org/api/query")
        self.arxiv_max_results = int(os.getenv("ARXIV_MAX_RESULTS", "50"))
        self.arxiv_sort_by = os.getenv("ARXIV_SORT_BY", "submittedDate")
        self.arxiv_sort_order = os.getenv("ARXIV_SORT_ORDER", "descending")
        self.http_user_agent = os.getenv("HTTP_USER_AGENT", "paper-radar/0.1 (research)")
        self.semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
        default_nature_feeds = {
            "Nature": "https://www.nature.com/nature.rss",
            "Nature Medicine": "https://www.nature.com/nm.rss",
            "Nature Biotechnology": "https://www.nature.com/nbt.rss",
            "Nature Machine Intelligence": "https://www.nature.com/natmachintell.rss",
            "Nature Biomedical Engineering": "https://www.nature.com/natbiomedeng.rss",
            "npj Digital Medicine": "https://www.nature.com/npjdigitalmed.rss",
            "Nature Reviews Drug Discovery": "https://www.nature.com/nrd.rss",
            "Nature Reviews Genetics": "https://www.nature.com/nrg.rss",
            "Nature Reviews Cancer": "https://www.nature.com/nrc.rss",
        }
        feeds_json = os.getenv("NATURE_FEEDS_JSON", json.dumps(default_nature_feeds))
        self.nature_feeds = json.loads(feeds_json)
        self.journal_feed_max_items = int(os.getenv("JOURNAL_FEED_MAX_ITEMS", "30"))
        self.x_api_base_url = os.getenv("X_API_BASE_URL", "https://api.x.com/2")
        self.x_bearer_token = os.getenv("X_BEARER_TOKEN", "")
        self.x_max_results = int(os.getenv("X_MAX_RESULTS", "30"))


settings = Settings()
