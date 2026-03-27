from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.linkedin_watchlist import router as linkedin_watchlist_router
from app.api.v1.endpoints.papers import router as papers_router
from app.api.v1.endpoints.social import router as social_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(papers_router)
api_router.include_router(social_router)
api_router.include_router(linkedin_watchlist_router)
