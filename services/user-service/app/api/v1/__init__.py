"""API v1 router configuration."""

from app.api.v1.endpoints import auth, users
from fastapi import APIRouter

api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include user management endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])
