from typing import Protocol

from app.schemas.linkedin_watchlist import LinkedInWatchlistItem
from app.schemas.social import SocialPost


class LinkedInConnectorInterface(Protocol):
    def fetch_updates(self, watchlists: list[LinkedInWatchlistItem], limit: int = 20) -> list[SocialPost]:
        raise NotImplementedError


class LinkedInConnectorPlaceholder:
    def fetch_updates(self, watchlists: list[LinkedInWatchlistItem], limit: int = 20) -> list[SocialPost]:
        return []
