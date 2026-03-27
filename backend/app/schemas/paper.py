from pydantic import BaseModel


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


class SearchPapersResponse(BaseModel):
    keyword: str
    papers: list[Paper]
