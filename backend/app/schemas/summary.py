from pydantic import BaseModel


class PaperSummary(BaseModel):
    paper_id: str
    research_problem: str
    method: str
    main_contribution: str
    three_sentence_summary: str


class TrendSummary(BaseModel):
    hottest_directions: list[str]
    high_frequency_keywords: list[str]
    common_methods: list[str]


class SearchTrendSummaryResponse(BaseModel):
    keyword: str
    trend_summary: TrendSummary
    paper_summaries: list[PaperSummary]
