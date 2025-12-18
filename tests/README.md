# Testing Guide

This directory contains comprehensive tests for all MLH microservices.

## Test Structure

```
tests/
├── integration/                    # End-to-end integration tests
│   ├── conftest.py                 # Shared fixtures (service clients, test users)
│   ├── test_auth_flow.py           # JWT auth, RBAC, cross-service auth
│   ├── test_enrollment_flow.py     # Full enrollment flow, quota, concurrency
│   └── test_cache_integration.py   # Redis cache behavior
├── performance/                    # Load and performance tests
│   ├── locustfile.py               # Locust load test definitions
│   └── README.md                   # Performance test guide
└── services/
    ├── user-service/tests/         # User authentication & profile tests
    ├── course-service/tests/       # Course CRUD & caching tests
    ├── enrollment-service/tests/   # Enrollment workflow tests
    └── payment-service/tests/      # Payment processing tests
```


## Prerequisites

- Python 3.11+
- pytest, pytest-asyncio, pytest-cov
- Running Docker containers (PostgreSQL, Redis)

## Running Tests

### All Services
```bash
# From project root
./scripts/run-tests.sh
```

### Individual Service
```bash
# From service directory
cd services/user-service
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_auth_api.py -v
```

### Specific Test Function
```bash
pytest tests/test_auth_api.py::test_user_signup -v
```

## Test Categories

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Fast execution

```bash
pytest tests/unit/ -v
```

### API Tests
- Test HTTP endpoints
- Use httpx AsyncClient
- Validate request/response schemas

```bash
pytest tests/api/ -v
```

### Integration Tests
- Test with real database
- Verify transactions and rollbacks
- Test inter-service communication

```bash
pytest tests/integration/ -v
```

## Coverage Reports

Generate HTML coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

Generate XML for CI:
```bash
pytest tests/ --cov=app --cov-report=xml
```

## CI Integration

Tests run automatically on:
- Push to `development`, `main`, `feature/*`, `fix/*`
- Pull requests

See `.github/workflows/ci.yml` for configuration.

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- `client` - Async HTTP client
- `db_session` - Database session with rollback
- `sample_*_data` - Sample test data

## Writing Tests

### Async Test Example
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
```

### Mock External Service
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    with patch("app.services.external_call", new_callable=AsyncMock) as mock:
        mock.return_value = {"status": "ok"}
        # Test code here
```

## Environment Variables

Tests use these environment variables:
- `DATABASE_URL` - Test database connection
- `REDIS_URL` - Redis for testing
- `JWT_SECRET_KEY` - JWT signing key

Set in `.env.test` or export before running tests.
