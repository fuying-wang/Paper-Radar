from __future__ import annotations

from app.schemas.paper import Paper
from app.schemas.topic import TopicAssignment
from app.services.topic_taxonomy import classify_text_with_taxonomy


def classify_paper_topics(paper: Paper) -> TopicAssignment:
    text_for_classification = " ".join(
        [
            paper.title,
            " ".join(paper.authors),
            paper.venue,
            paper.abstract,
        ]
    )
    classification = classify_text_with_taxonomy(text_for_classification)
    return TopicAssignment(
        primary_topic=classification.primary_topic,
        secondary_topics=classification.secondary_topics,
        matched_keywords=classification.matched_keywords,
    )
