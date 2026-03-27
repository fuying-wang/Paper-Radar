from datetime import date

from pydantic import BaseModel


class DailyDigestResponse(BaseModel):
    topic: str
    digest_date: date
    new_paper_count: int
    paper_ids: list[int]
    content: str
