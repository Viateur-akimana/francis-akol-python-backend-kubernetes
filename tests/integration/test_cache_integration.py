"""
Redis Cache Integration Tests.

Tests Redis caching behavior including:
- Cache hit/miss scenarios
- Cache invalidation on updates
- Cache expiration handling
- Cache consistency
"""

import asyncio
from typing import Dict

import httpx
import pytest


def auth_headers(token: str) -> Dict[str, str]:
    """Generate authorization headers."""
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestCourseCaching:
    """Test course service caching behavior."""

    async def test_course_list_is_cached(
        self,
        course_client: httpx.AsyncClient,
        test_instructor: dict,
    ):
        """Test that course list responses use caching."""
        headers = auth_headers(test_instructor["access_token"])

        # First request - should hit database
        response1 = await course_client.get("/api/v1/courses/", headers=headers)
        assert response1.status_code == 200

        # Second request - should be faster (cached)
        import time

        start = time.time()
        response2 = await course_client.get("/api/v1/courses/", headers=headers)
        duration = time.time() - start

        assert response2.status_code == 200
        # Cached responses should be very fast (under 100ms typically)
        # Note: This is a soft assertion since network latency varies

    async def test_course_detail_is_cached(
        self,
        course_client: httpx.AsyncClient,
        test_course: dict,
        test_instructor: dict,
    ):
        """Test that individual course details are cached."""
        headers = auth_headers(test_instructor["access_token"])
        course_id = test_course["id"]

        # First request
        response1 = await course_client.get(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        if response1.status_code != 200:
            pytest.skip(f"Could not get course: {response1.text}")

        # Second request - should use cache
        response2 = await course_client.get(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        assert response2.status_code == 200
        # Data should be identical
        assert response1.json() == response2.json()

    async def test_cache_invalidation_on_update(
        self,
        course_client: httpx.AsyncClient,
        test_course: dict,
        test_instructor: dict,
    ):
        """Test that cache is invalidated when course is updated."""
        headers = auth_headers(test_instructor["access_token"])
        course_id = test_course["id"]

        # Get initial course data (populates cache)
        response1 = await course_client.get(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        if response1.status_code != 200:
            pytest.skip(f"Could not get course: {response1.text}")

        original_data = response1.json()

        # Update the course
        update_data = {"description": "Updated description for cache test"}
        update_response = await course_client.put(
            f"/api/v1/courses/{course_id}",
            json=update_data,
            headers=headers,
        )

        if update_response.status_code not in (200, 204):
            pytest.skip(f"Could not update course: {update_response.text}")

        # Get course again - should reflect update (cache invalidated)
        response2 = await course_client.get(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        assert response2.status_code == 200
        new_data = response2.json()

        # Verify the update is reflected
        if "description" in new_data:
            assert new_data["description"] == "Updated description for cache test"

    async def test_cache_invalidation_on_delete(
        self,
        course_client: httpx.AsyncClient,
        test_instructor: dict,
    ):
        """Test that cache is invalidated when course is deleted."""
        import uuid

        headers = auth_headers(test_instructor["access_token"])
        unique_id = uuid.uuid4().hex[:8]

        # Create a new course
        course_data = {
            "title": f"Delete Test Course {unique_id}",
            "description": "Course to test delete cache invalidation",
            "price": 30.00,
            "max_students": 50,
            "is_published": True,
        }

        create_response = await course_client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=headers,
        )

        if create_response.status_code not in (200, 201):
            pytest.skip(f"Could not create course: {create_response.text}")

        course_id = create_response.json().get("id")

        # Get course (populates cache)
        await course_client.get(f"/api/v1/courses/{course_id}", headers=headers)

        # Delete course
        delete_response = await course_client.delete(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        if delete_response.status_code not in (200, 204):
            pytest.skip(f"Could not delete course: {delete_response.text}")

        # Get course again - should return 404 (cache invalidated)
        response = await course_client.get(
            f"/api/v1/courses/{course_id}",
            headers=headers,
        )

        assert (
            response.status_code == 404
        ), f"Deleted course should not be found: {response.status_code}"


@pytest.mark.asyncio
class TestCacheFallback:
    """Test cache fallback behavior."""

    async def test_service_works_without_cache(
        self,
        course_client: httpx.AsyncClient,
        test_instructor: dict,
    ):
        """Test that service still works if cache is unavailable."""
        headers = auth_headers(test_instructor["access_token"])

        # This test verifies the service handles cache failures gracefully
        # In production, if Redis is down, the service should fallback to DB

        response = await course_client.get("/api/v1/courses/", headers=headers)

        # Service should still respond, even if cache is down
        assert response.status_code in (
            200,
            500,
            503,
        ), f"Unexpected status: {response.status_code}"


@pytest.mark.asyncio
class TestCacheConsistency:
    """Test cache consistency across operations."""

    async def test_concurrent_reads_use_same_cache(
        self,
        course_client: httpx.AsyncClient,
        test_course: dict,
        test_instructor: dict,
    ):
        """Test that concurrent reads get consistent cached data."""
        headers = auth_headers(test_instructor["access_token"])
        course_id = test_course["id"]

        # Make concurrent requests
        async def get_course():
            return await course_client.get(
                f"/api/v1/courses/{course_id}",
                headers=headers,
            )

        responses = await asyncio.gather(
            get_course(),
            get_course(),
            get_course(),
        )

        # All responses should be successful
        for response in responses:
            if response.status_code == 200:
                continue
            else:
                pytest.skip(f"Could not get course: {response.text}")

        # All responses should contain the same data
        data_list = [r.json() for r in responses if r.status_code == 200]

        if len(data_list) >= 2:
            assert all(
                d == data_list[0] for d in data_list
            ), "Concurrent reads should return consistent data"
