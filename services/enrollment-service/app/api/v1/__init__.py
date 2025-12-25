"""API v1 router configuration."""

from app.api.v1.endpoints import enrollments
from fastapi import APIRouter

api_router = APIRouter()

# Include enrollment endpoints
api_router.include_router(
    enrollments.router, prefix="/enrollments", tags=["Enrollments"]
)
