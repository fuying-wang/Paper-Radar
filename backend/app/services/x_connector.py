from __future__ import annotations

import logging

import httpx

from app.core.config import settings
from app.schemas.social import SocialMetrics, SocialPost


logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def _build_search_query(query: str) -> str:
    cleaned = query.strip()
    base = cleaned if cleaned else "ai"
    return f"({base}) lang:en -is:retweet -is:reply"


def _get_author_map(payload: dict) -> dict[str, str]:
    users = payload.get("includes", {}).get("users", [])
    author_map: dict[str, str] = {}
    if not isinstance(users, list):
        return author_map
    for user in users:
        user_id = str(user.get("id", "")).strip()
        if not user_id:
            continue
        username = str(user.get("username", "")).strip()
        name = str(user.get("name", "")).strip()
        author_map[user_id] = username or name or "unknown"
    return author_map


def fetch_x_recent_posts(query: str, limit: int = 10) -> list[SocialPost]:
    token = settings.x_bearer_token.strip()
    if not token:
        logger.warning("x bearer token is not configured")
        return []
    safe_limit = max(10, min(limit, settings.x_max_results, 100))
    params = {
        "query": _build_search_query(query),
        "max_results": safe_limit,
        "tweet.fields": "created_at,public_metrics,lang",
        "expansions": "author_id",
        "user.fields": "username,name",
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{settings.x_api_base_url}/tweets/search/recent"

    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        logger.warning("x recent search failed: %s", exc)
        return []
    except ValueError as exc:
        logger.warning("x payload json decode failed: %s", exc)
        return []

    data = payload.get("data", [])
    if not isinstance(data, list):
        return []
    author_map = _get_author_map(payload)
    posts: list[SocialPost] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        post_id = str(item.get("id", "")).strip()
        if not post_id:
            continue
        author_id = str(item.get("author_id", "")).strip()
        author = author_map.get(author_id, "unknown")
        metrics = item.get("public_metrics") or {}
        posts.append(
            SocialPost(
                id=post_id,
                text=str(item.get("text", "")).strip(),
                author=author,
                created_at=str(item.get("created_at", "")).strip(),
                public_metrics=SocialMetrics(
                    like_count=int(metrics.get("like_count") or 0),
                    retweet_count=int(metrics.get("retweet_count") or 0),
                    reply_count=int(metrics.get("reply_count") or 0),
                    quote_count=int(metrics.get("quote_count") or 0),
                    bookmark_count=int(metrics.get("bookmark_count") or 0),
                    impression_count=int(metrics.get("impression_count") or 0),
                ),
                post_url=f"https://x.com/{author}/status/{post_id}" if author != "unknown" else f"https://x.com/i/web/status/{post_id}",
            )
        )
    return posts
