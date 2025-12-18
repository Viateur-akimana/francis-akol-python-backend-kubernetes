"""
Integration Test Configuration and Fixtures.

This module provides shared fixtures for integration tests that run against
real service instances (via docker-compose).
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Generator

import httpx
import pytest
import pytest_asyncio

# Service URLs (from docker-compose)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
COURSE_SERVICE_URL = os.getenv("COURSE_SERVICE_URL", "http://localhost:8002")
ENROLLMENT_SERVICE_URL = os.getenv("ENROLLMENT_SERVICE_URL", "http://localhost:8003")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create a shared async HTTP client for all tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def user_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client configured for User Service."""
    async with httpx.AsyncClient(
        base_url=USER_SERVICE_URL,
        timeout=30.0,
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def course_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client configured for Course Service."""
    async with httpx.AsyncClient(
        base_url=COURSE_SERVICE_URL,
        timeout=30.0,
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def enrollment_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client configured for Enrollment Service."""
    async with httpx.AsyncClient(
        base_url=ENROLLMENT_SERVICE_URL,
        timeout=30.0,
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def payment_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client configured for Payment Service."""
    async with httpx.AsyncClient(
        base_url=PAYMENT_SERVICE_URL,
        timeout=30.0,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def test_user(user_client: httpx.AsyncClient) -> AsyncGenerator[Dict, None]:
    """Create a test user and return credentials."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "email": f"testuser_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPassword123!",
        "role": "STUDENT",
    }

    # Register user
    response = await user_client.post("/api/v1/auth/signup", json=user_data)

    if response.status_code == 201:
        result = response.json()
        yield {
            **user_data,
            "user_id": result.get("user", {}).get("id"),
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
        }
    else:
        # If registration fails, try login (user may exist)
        login_response = await user_client.post(
            "/api/v1/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        if login_response.status_code == 200:
            result = login_response.json()
            yield {
                **user_data,
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
            }
        else:
            pytest.skip(f"Could not create test user: {response.text}")


@pytest_asyncio.fixture
async def test_instructor(user_client: httpx.AsyncClient) -> AsyncGenerator[Dict, None]:
    """Create a test instructor and return credentials."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    instructor_data = {
        "email": f"instructor_{unique_id}@example.com",
        "username": f"instructor_{unique_id}",
        "password": "InstructorPass123!",
        "role": "INSTRUCTOR",
    }

    # Register instructor
    response = await user_client.post("/api/v1/auth/signup", json=instructor_data)

    if response.status_code == 201:
        result = response.json()
        yield {
            **instructor_data,
            "user_id": result.get("user", {}).get("id"),
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
        }
    else:
        pytest.skip(f"Could not create test instructor: {response.text}")


@pytest_asyncio.fixture
async def test_course(
    course_client: httpx.AsyncClient,
    test_instructor: Dict,
) -> AsyncGenerator[Dict, None]:
    """Create a test course and return its data."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    course_data = {
        "title": f"Test Course {unique_id}",
        "description": "A test course for integration testing",
        "price": 99.99,
        "max_students": 100,
        "is_published": True,
    }

    headers = {"Authorization": f"Bearer {test_instructor['access_token']}"}

    response = await course_client.post(
        "/api/v1/courses/",
        json=course_data,
        headers=headers,
    )

    if response.status_code in (200, 201):
        result = response.json()
        yield {
            **course_data,
            "id": result.get("id"),
            "instructor_id": test_instructor.get("user_id"),
        }
    else:
        pytest.skip(f"Could not create test course: {response.text}")


def auth_headers(token: str) -> Dict[str, str]:
    """Generate authorization headers."""
    return {"Authorization": f"Bearer {token}"}


# Service health check fixture
@pytest_asyncio.fixture(scope="session", autouse=True)
async def check_services_health(http_client: httpx.AsyncClient):
    """Check that all services are healthy before running tests."""
    services = [
        (USER_SERVICE_URL, "User Service"),
        (COURSE_SERVICE_URL, "Course Service"),
        (ENROLLMENT_SERVICE_URL, "Enrollment Service"),
        (PAYMENT_SERVICE_URL, "Payment Service"),
    ]

    for url, name in services:
        try:
            response = await http_client.get(f"{url}/health")
            if response.status_code != 200:
                pytest.skip(f"{name} is not healthy: {response.status_code}")
        except httpx.ConnectError:
            pytest.skip(
                f"{name} is not reachable at {url}. Start services with docker-compose."
            )
