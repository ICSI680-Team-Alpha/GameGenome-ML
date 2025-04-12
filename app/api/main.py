from fastapi import APIRouter

from app.api.routers import recommendation

api_router = APIRouter()
api_router.include_router(recommendation.router)