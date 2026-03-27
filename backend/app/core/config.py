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


settings = Settings()
