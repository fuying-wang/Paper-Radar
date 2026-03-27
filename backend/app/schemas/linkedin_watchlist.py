from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


WatchlistEntityType = Literal["institution", "lab", "author", "company_page"]


class LinkedInWatchlistCreate(BaseModel):
    entity_type: WatchlistEntityType
    name: str = Field(min_length=1, max_length=255)
    linkedin_url: HttpUrl
    notes: str = ""
    is_active: bool = True


class LinkedInWatchlistItem(BaseModel):
    id: int
    entity_type: WatchlistEntityType
    name: str
    linkedin_url: str
    notes: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LinkedInWatchlistListResponse(BaseModel):
    items: list[LinkedInWatchlistItem]
