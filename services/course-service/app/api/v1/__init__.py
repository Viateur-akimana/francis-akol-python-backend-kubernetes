"""API v1 router configuration."""

from app.api.v1.endpoints import categories, courses, recommendations
from fastapi import APIRouter

api_router = APIRouter()

# Include course endpoints
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])

# Include category endpoints
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])

# Include AI recommendations endpoints
api_router.include_router(recommendations.router)
