from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str
    title: str
    authors: list[str]
    venue: str
    year: int
    abstract: str
    cited_by_count: int
    url: str
    latest_score: float
    hot_score: float
    influential_score: float
    final_score: float
    source_name: str = "unknown"
    source_id: str = ""
    published_at: str = ""
    updated_at: str = ""
    journal_name: str = ""
    primary_category: str = ""
    pdf_url: str = ""
    primary_topic: str = "General AI"
    topic_tags: list[str] = Field(default_factory=list)


class SearchPapersResponse(BaseModel):
    keyword: str
    papers: list[Paper]
