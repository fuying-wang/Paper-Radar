from app.schemas.digest import DailyDigestResponse
from app.schemas.linkedin_watchlist import (
    LinkedInWatchlistCreate,
    LinkedInWatchlistItem,
    LinkedInWatchlistListResponse,
)
from app.schemas.paper import Paper, SearchPapersResponse
from app.schemas.social import SearchSocialResponse, SocialMetrics, SocialPost
from app.schemas.summary import PaperSummary, SearchTrendSummaryResponse, TrendSummary
from app.schemas.topic import TopicAssignment

__all__ = [
    "Paper",
    "SearchPapersResponse",
    "LinkedInWatchlistCreate",
    "LinkedInWatchlistItem",
    "LinkedInWatchlistListResponse",
    "SocialPost",
    "SocialMetrics",
    "SearchSocialResponse",
    "DailyDigestResponse",
    "PaperSummary",
    "TrendSummary",
    "SearchTrendSummaryResponse",
    "TopicAssignment",
]
