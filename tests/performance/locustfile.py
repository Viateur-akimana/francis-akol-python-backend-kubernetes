"""Locust load tests for MLH Platform."""

import random
import string
from locust import HttpUser, task, between, SequentialTaskSet


def random_email():
    """Generate random email."""
    return f"test_{random.randint(1000, 9999)}@example.com"


def random_string(length=8):
    """Generate random string."""
    return "".join(random.choices(string.ascii_lowercase, k=length))


class UserBehavior(SequentialTaskSet):
    """Simulates typical user behavior."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None

    def on_start(self):
        """Sign up and login before tasks."""
        self.signup_and_login()

    def signup_and_login(self):
        """Create account and get auth token."""
        email = random_email()
        password = "TestPassword123!"

        # Signup
        response = self.client.post(
            "/api/v1/auth/signup",
            json={
                "email": email,
                "username": random_string(),
                "password": password,
                "first_name": "Test",
                "last_name": "User"
            }
        )

        if response.status_code == 201:
            # Login
            login_response = self.client.post(
                "/api/v1/auth/login",
                data={"username": email, "password": password}
            )
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")

    @property
    def headers(self):
        """Auth headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(3)
    def get_courses(self):
        """List courses (frequent operation)."""
        self.client.get("/api/v1/courses/", headers=self.headers)

    @task(2)
    def get_course_detail(self):
        """Get course detail."""
        course_id = random.randint(1, 10)
        self.client.get(f"/api/v1/courses/{course_id}", headers=self.headers)

    @task(2)
    def get_categories(self):
        """List categories."""
        self.client.get("/api/v1/categories/", headers=self.headers)

    @task(1)
    def search_courses(self):
        """Search courses."""
        queries = ["python", "web", "data", "machine", "cloud"]
        query = random.choice(queries)
        self.client.get(f"/api/v1/courses/?search={query}", headers=self.headers)

    @task(1)
    def get_profile(self):
        """Get current user profile."""
        self.client.get("/api/v1/users/me", headers=self.headers)

    @task(1)
    def get_recommendations(self):
        """Get AI course recommendations."""
        prompts = [
            "I want to learn Python programming",
            "Help me understand web development",
            "Data science courses for beginners",
            "Cloud computing fundamentals",
        ]
        self.client.post(
            "/api/v1/recommendations/",
            json={"prompt": random.choice(prompts), "max_results": 5},
            headers=self.headers
        )


class MLHUser(HttpUser):
    """MLH Platform user for load testing."""

    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "http://localhost:8001"


class CourseServiceUser(HttpUser):
    """Course Service focused load testing."""

    wait_time = between(0.5, 2)
    host = "http://localhost:8002"

    @task(5)
    def list_courses(self):
        """List courses - most common operation."""
        self.client.get("/api/v1/courses/")

    @task(3)
    def get_course(self):
        """Get single course."""
        self.client.get(f"/api/v1/courses/{random.randint(1, 20)}")

    @task(2)
    def list_categories(self):
        """List categories."""
        self.client.get("/api/v1/categories/")

    @task(1)
    def filtered_courses(self):
        """Filter courses by category."""
        self.client.get(f"/api/v1/courses/?category_id={random.randint(1, 5)}")

    @task(1)
    def health_check(self):
        """Health check endpoint."""
        self.client.get("/health")


class EnrollmentServiceUser(HttpUser):
    """Enrollment Service focused load testing."""

    wait_time = between(1, 3)
    host = "http://localhost:8003"

    def on_start(self):
        self.token = None
        # In real test, get auth token here

    @task(3)
    def list_enrollments(self):
        """List user enrollments."""
        self.client.get("/api/v1/enrollments/")

    @task(2)
    def get_enrollment(self):
        """Get enrollment details."""
        self.client.get(f"/api/v1/enrollments/{random.randint(1, 10)}")

    @task(1)
    def enrollment_stats(self):
        """Get enrollment statistics."""
        self.client.get("/api/v1/enrollments/stats")

    @task(1)
    def health_check(self):
        """Health check."""
        self.client.get("/health")


class PaymentServiceUser(HttpUser):
    """Payment Service focused load testing."""

    wait_time = between(2, 5)
    host = "http://localhost:8004"

    @task(3)
    def list_payments(self):
        """List payments."""
        self.client.get("/api/v1/payments/")

    @task(2)
    def get_payment(self):
        """Get payment details."""
        self.client.get(f"/api/v1/payments/{random.randint(1, 10)}")

    @task(1)
    def payment_stats(self):
        """Get payment statistics."""
        self.client.get("/api/v1/payments/stats")

    @task(1)
    def health_check(self):
        """Health check."""
        self.client.get("/health")
