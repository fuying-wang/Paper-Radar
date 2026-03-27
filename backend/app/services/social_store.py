from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.social_post import SocialPostModel
from app.schemas.social import SocialMetrics, SocialPost
from app.services.topic_taxonomy import classify_text_with_taxonomy


def _to_schema(model: SocialPostModel) -> SocialPost:
    return SocialPost(
        id=model.source_post_id,
        text=model.text,
        author=model.author,
        created_at=model.created_at,
        public_metrics=SocialMetrics.model_validate(model.public_metrics or {}),
        post_url=model.post_url,
        source_name=model.source_name,
        primary_topic=model.primary_topic,
        topic_tags=model.topic_tags,
    )


def upsert_social_posts(db: Session, query: str, posts: list[SocialPost]) -> list[SocialPost]:
    persisted: list[SocialPostModel] = []
    for post in posts:
        classification = classify_text_with_taxonomy(post.text)
        stmt = select(SocialPostModel).where(
            SocialPostModel.source_name == post.source_name,
            SocialPostModel.source_post_id == post.id,
        )
        existing = db.execute(stmt).scalars().first()
        if existing is None:
            existing = SocialPostModel(
                source_name=post.source_name,
                source_post_id=post.id,
                query=query,
                text=post.text,
                author=post.author,
                created_at=post.created_at,
                post_url=post.post_url,
                public_metrics=post.public_metrics.model_dump(),
                primary_topic=classification.primary_topic,
                topic_tags=classification.secondary_topics,
            )
            db.add(existing)
        else:
            existing.query = query
            existing.text = post.text
            existing.author = post.author
            existing.created_at = post.created_at
            existing.post_url = post.post_url
            existing.public_metrics = post.public_metrics.model_dump()
            existing.primary_topic = classification.primary_topic
            existing.topic_tags = classification.secondary_topics
        db.flush()
        persisted.append(existing)

    db.commit()
    return [_to_schema(item) for item in persisted]
