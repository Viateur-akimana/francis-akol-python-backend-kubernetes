"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user signup."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "role": "student",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"
    assert data["user"]["role"] == "student"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    """Test signup with duplicate email fails."""
    # Create first user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "SecurePass123!",
        },
    )

    # Try to create another user with same email
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_duplicate_username(client: AsyncClient):
    """Test signup with duplicate username fails."""
    # Create first user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test1@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
        },
    )

    # Try to create another user with same username
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test2@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Create user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password fails."""
    # Create user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
        },
    )

    # Try to login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent email fails."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint."""
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
