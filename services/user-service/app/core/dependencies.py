"""FastAPI dependencies for dependency injection."""

from typing import Generator, Optional

from app.core.security import decode_token, verify_token_type
from app.db.session import async_session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession


# Security scheme
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency to get current authenticated user ID from JWT token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_token(token)
    verify_token_type(payload, "access")

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency to get current authenticated user email from JWT token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        User email from token

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = decode_token(token)
    verify_token_type(payload, "access")

    email: Optional[str] = payload.get("email")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return email


def require_role(allowed_roles: list[str]):
    """
    Dependency factory to check if user has required role.

    Args:
        allowed_roles: List of allowed roles

    Returns:
        Dependency function
    """

    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> dict:
        token = credentials.credentials
        payload = decode_token(token)
        verify_token_type(payload, "access")

        user_role: Optional[str] = payload.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}",
            )

        return payload

    return role_checker
