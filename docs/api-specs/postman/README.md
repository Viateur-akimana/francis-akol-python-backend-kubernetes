# MLH Platform - Postman Collection

This directory contains the Postman collection for testing the MLH Platform APIs.

## Collection Overview

The collection covers all 4 microservices:

| Service | Port | Description |
|---------|------|-------------|
| User Service | 8001 | Authentication & User Management |
| Course Service | 8002 | Course Management with Redis Caching |
| Enrollment Service | 8003 | Enrollment Processing with Celery |
| Payment Service | 8004 | Payment Processing & Transactions |

## Importing the Collection

1. Open Postman
2. Click **Import** → **File**
3. Select `MLH_Platform_API.postman_collection.json`
4. The collection will appear in your sidebar

## Collection Variables

The collection uses these variables (auto-populated by test scripts):

| Variable | Description |
|----------|-------------|
| `user_service_url` | User service base URL (default: http://localhost:8001) |
| `course_service_url` | Course service base URL (default: http://localhost:8002) |
| `enrollment_service_url` | Enrollment service base URL (default: http://localhost:8003) |
| `payment_service_url` | Payment service base URL (default: http://localhost:8004) |
| `access_token` | JWT access token (set after login/signup) |
| `refresh_token` | JWT refresh token (set after login/signup) |
| `user_id` | Current user ID |
| `course_id` | Last created/selected course ID |
| `enrollment_id` | Last created enrollment ID |
| `payment_id` | Last created payment ID |

## Test Categories

### Happy Path Tests
- User signup and login
- Course CRUD operations
- Enrollment creation and management
- Payment processing

### Error Scenario Tests
- Invalid credentials
- Missing authentication
- Invalid tokens
- Unauthorized access

### E2E Flows
- Complete course enrollment flow (signup → browse → enroll → pay → verify)

## Running with Newman (CLI)

```bash
# Install Newman
npm install -g newman

# Run the full collection
newman run MLH_Platform_API.postman_collection.json

# Run with environment variables
newman run MLH_Platform_API.postman_collection.json \
  --env-var "user_service_url=http://localhost:8001" \
  --env-var "course_service_url=http://localhost:8002" \
  --env-var "enrollment_service_url=http://localhost:8003" \
  --env-var "payment_service_url=http://localhost:8004"

# Run specific folder
newman run MLH_Platform_API.postman_collection.json --folder "User Service"

# Generate HTML report
newman run MLH_Platform_API.postman_collection.json -r html
```

## Prerequisites

Before running tests, ensure all services are running:

```bash
docker-compose up -d
```

Verify services are healthy:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```
