from pydantic import BaseModel, Field


class SocialMetrics(BaseModel):
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    bookmark_count: int = 0
    impression_count: int = 0


class SocialPost(BaseModel):
    id: str
    text: str
    author: str
    created_at: str
    public_metrics: SocialMetrics = Field(default_factory=SocialMetrics)
    post_url: str
    source_name: str = "x"
    primary_topic: str = "General AI"
    topic_tags: list[str] = Field(default_factory=list)


class SearchSocialResponse(BaseModel):
    keyword: str
    posts: list[SocialPost]
