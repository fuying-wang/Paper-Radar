from pydantic import BaseModel, Field


class TopicAssignment(BaseModel):
    primary_topic: str
    secondary_topics: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
