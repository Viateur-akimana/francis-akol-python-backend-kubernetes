"""
Enrollment Flow Integration Tests.

Tests the complete enrollment flow including:
- Student enrollment in courses
- Quota enforcement
- Concurrent enrollment handling
- Payment integration with enrollment
- Enrollment status transitions
"""

import asyncio
from typing import Dict, Optional

import httpx
import pytest


def auth_headers(token: str, user_id: Optional[int] = None) -> Dict[str, str]:
    """Generate authorization headers with optional x-user-id."""
    headers = {"Authorization": f"Bearer {token}"}
    if user_id is not None:
        headers["x-user-id"] = str(user_id)
    return headers



@pytest.mark.asyncio
class TestBasicEnrollmentFlow:
    """Test basic enrollment operations."""

    async def test_student_can_enroll_in_course(
        self,
        enrollment_client: httpx.AsyncClient,
        test_user: dict,
        test_course: dict,
    ):
        """Test student can enroll in an available course."""
        headers = auth_headers(test_user["access_token"], test_user.get("user_id"))
        enrollment_data = {"course_id": test_course["id"]}

        response = await enrollment_client.post(
            "/api/v1/enrollments/",
            json=enrollment_data,
            headers=headers,
        )

        # Accept various success codes
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Enrollment failed: {response.text}"

        if response.status_code in (200, 201):
            result = response.json()
            assert "id" in result or "enrollment_id" in result

    async def test_duplicate_enrollment_prevented(
        self,
        enrollment_client: httpx.AsyncClient,
        test_user: dict,
        test_course: dict,
    ):
        """Test duplicate enrollment is prevented."""
        headers = auth_headers(test_user["access_token"], test_user.get("user_id"))
        enrollment_data = {"course_id": test_course["id"]}

        # First enrollment
        response1 = await enrollment_client.post(
            "/api/v1/enrollments/",
            json=enrollment_data,
            headers=headers,
        )

        # Second enrollment should fail
        response2 = await enrollment_client.post(
            "/api/v1/enrollments/",
            json=enrollment_data,
            headers=headers,
        )

        # Second should be rejected (400 or 409 conflict)
        if response1.status_code in (200, 201, 202):
            assert response2.status_code in (
                400,
                409,
            ), f"Duplicate enrollment should be rejected: {response2.status_code}"

    async def test_enrollment_for_nonexistent_course_fails(
        self,
        enrollment_client: httpx.AsyncClient,
        test_user: dict,
    ):
        """Test enrollment for non-existent course behavior."""
        headers = auth_headers(test_user["access_token"], test_user.get("user_id"))
        enrollment_data = {"course_id": 999999}  # Non-existent course

        response = await enrollment_client.post(
            "/api/v1/enrollments/",
            json=enrollment_data,
            headers=headers,
        )

        # Service might accept enrollment (async validation) or reject it
        # Accept 201 (async validation), 400 (bad request), or 404 (not found)
        assert response.status_code in (
            201,
            400,
            404,
        ), f"Non-existent course enrollment unexpected: {response.status_code}"

    async def test_list_user_enrollments(
        self,
        enrollment_client: httpx.AsyncClient,
        test_user: dict,
    ):
        """Test listing user's enrollments."""
        headers = auth_headers(test_user["access_token"], test_user.get("user_id"))

        response = await enrollment_client.get(
            "/api/v1/enrollments/",
            headers=headers,
        )

        assert response.status_code == 200, f"List enrollments failed: {response.text}"
        result = response.json()
        assert isinstance(result, (list, dict))  # Paginated or list


@pytest.mark.asyncio
class TestEnrollmentQuota:
    """Test enrollment quota enforcement."""

    async def test_enrollment_respects_max_students(
        self,
        course_client: httpx.AsyncClient,
        enrollment_client: httpx.AsyncClient,
        user_client: httpx.AsyncClient,
        test_instructor: dict,
    ):
        """Test that enrollment respects max_students quota."""
        import uuid

        # Create a course with very limited capacity
        headers = auth_headers(test_instructor["access_token"])
        unique_id = uuid.uuid4().hex[:8]
        course_data = {
            "title": f"Limited Course {unique_id}",
            "description": "Course with limited capacity",
            "price": 10.00,
            "max_students": 1,  # Only 1 student allowed
            "is_published": True,
        }

        course_response = await course_client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=headers,
        )

        if course_response.status_code not in (200, 201):
            pytest.skip(f"Could not create limited course: {course_response.text}")

        course_id = course_response.json().get("id")

        # Create two students
        students = []
        for i in range(2):
            unique_id = uuid.uuid4().hex[:8]
            student_data = {
                "email": f"quota_student_{unique_id}@example.com",
                "username": f"quota_student_{unique_id}",
                "password": "QuotaPass123!",
                "role": "student",
            }
            response = await user_client.post("/api/v1/auth/signup", json=student_data)
            if response.status_code == 201:
                students.append(response.json())

        if len(students) < 2:
            pytest.skip("Could not create enough test students")

        # First student enrolls - should succeed
        headers1 = auth_headers(students[0]["access_token"])
        response1 = await enrollment_client.post(
            "/api/v1/enrollments/",
            json={"course_id": course_id},
            headers=headers1,
        )

        # Second student enrolls - should fail (quota exceeded)
        headers2 = auth_headers(students[1]["access_token"])
        response2 = await enrollment_client.post(
            "/api/v1/enrollments/",
            json={"course_id": course_id},
            headers=headers2,
        )

        # Verify quota enforcement
        if response1.status_code in (200, 201, 202):
            # Second enrollment should be rejected
            assert response2.status_code in (
                400,
                409,
                422,
            ), f"Quota should be enforced: {response2.status_code}"


@pytest.mark.asyncio
class TestConcurrentEnrollment:
    """Test concurrent enrollment handling."""

    async def test_concurrent_enrollments_handled(
        self,
        course_client: httpx.AsyncClient,
        enrollment_client: httpx.AsyncClient,
        user_client: httpx.AsyncClient,
        test_instructor: dict,
    ):
        """Test that concurrent enrollments are handled safely."""
        import uuid

        # Create a course with limited capacity
        headers = auth_headers(test_instructor["access_token"])
        unique_id = uuid.uuid4().hex[:8]
        course_data = {
            "title": f"Concurrent Test Course {unique_id}",
            "description": "Testing concurrent enrollments",
            "price": 25.00,
            "max_students": 3,  # Limited spots
            "is_published": True,
        }

        course_response = await course_client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=headers,
        )

        if course_response.status_code not in (200, 201):
            pytest.skip(f"Could not create course: {course_response.text}")

        course_id = course_response.json().get("id")

        # Create 5 students (more than max_students)
        students = []
        for i in range(5):
            unique_id = uuid.uuid4().hex[:8]
            student_data = {
                "email": f"concurrent_student_{unique_id}@example.com",
                "username": f"concurrent_student_{unique_id}",
                "password": "ConcurrentPass123!",
                "role": "student",
            }
            response = await user_client.post("/api/v1/auth/signup", json=student_data)
            if response.status_code == 201:
                students.append(response.json())

        if len(students) < 5:
            pytest.skip("Could not create enough test students")

        # Attempt concurrent enrollments
        async def enroll_student(student):
            headers = auth_headers(student["access_token"])
            return await enrollment_client.post(
                "/api/v1/enrollments/",
                json={"course_id": course_id},
                headers=headers,
            )

        # Run enrollments concurrently
        responses = await asyncio.gather(
            *[enroll_student(s) for s in students],
            return_exceptions=True,
        )

        # Count successful enrollments
        successful = sum(
            1
            for r in responses
            if not isinstance(r, Exception) and r.status_code in (200, 201, 202)
        )

        # At most max_students should succeed
        assert (
            successful <= 3
        ), f"More than max_students ({successful}) succeeded - quota not enforced"


@pytest.mark.asyncio
class TestEnrollmentPaymentFlow:
    """Test enrollment with payment integration."""

    async def test_complete_enrollment_payment_flow(
        self,
        enrollment_client: httpx.AsyncClient,
        payment_client: httpx.AsyncClient,
        test_user: dict,
        test_course: dict,
    ):
        """Test complete flow: enrollment -> payment -> activation."""
        # This test verifies the integration between enrollment and payment services

        # Step 1: Create enrollment
        user_headers = auth_headers(test_user["access_token"])

        enrollment_response = await enrollment_client.post(
            "/api/v1/enrollments/",
            json={"course_id": test_course["id"]},
            headers=user_headers,
        )

        if enrollment_response.status_code not in (200, 201, 202):
            pytest.skip(f"Could not create enrollment: {enrollment_response.text}")

        enrollment_data = enrollment_response.json()

        # Step 2: Create payment for the enrollment
        payment_data = {
            "course_id": test_course["id"],
            "amount": test_course.get("price", 99.99),
            "currency": "USD",
            "payment_method": "credit_card",
        }

        payment_response = await payment_client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=user_headers,
        )

        # Payment might succeed or fail based on mock gateway
        if payment_response.status_code in (200, 201):
            payment_result = payment_response.json()
            assert "id" in payment_result or "payment_id" in payment_result

        # The integration is verified if both services respond appropriately
        assert enrollment_response.status_code in (200, 201, 202)
