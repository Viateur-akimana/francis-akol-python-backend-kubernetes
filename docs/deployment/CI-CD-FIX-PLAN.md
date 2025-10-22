# CI/CD Fix and Enhancement Plan

**Date:** October 22, 2025  
**Status:** Planning Phase  
**Priority:** HIGH 

---

## 🔍 Current State Analysis

### Existing CI Pipeline (`.github/workflows/ci.yml`)
**Status:** ⚠️ DISABLED (Checks Failing)

**Current Issues:**
1. ❌ Lint checks failing
2. ❌ Type checking (mypy) issues
3. ❌ Test execution failures
4. ❌ Coverage reporting not configured
5. ❌ Multi-service testing not parallelized
6. ❌ No Docker image builds in CI
7. ❌ No security scanning (bandit, safety)

---

## 🎯 Fix Plan Overview

### Phase 1: Fix Existing CI Pipeline (Priority: CRITICAL)
**Estimated Time:** 2-3 hours

### Phase 2: Add Missing Test Suite (Priority: HIGH)
**Estimated Time:** 4-6 hours

### Phase 3: Enhance Observability (Priority: MEDIUM)
**Estimated Time:** 2-3 hours

### Phase 4: Add Deployment Artifacts (Priority: MEDIUM)
**Estimated Time:** 3-4 hours

---

## 📋 Phase 1: CI Pipeline Fixes

### 1.1 Fix Linting Issues
**Branch:** `fix/ci-linting`  
**Files to Fix:**
- All service files with linting errors
- Configuration: `.flake8`, `pyproject.toml` (black, isort)

**Actions:**
```bash
# Run locally first
cd services/user-service && flake8 app/ --max-line-length=120 --extend-ignore=E203,W503
cd services/course-service && flake8 app/ --max-line-length=120 --extend-ignore=E203,W503
cd services/enrollment-service && flake8 app/ --max-line-length=120 --extend-ignore=E203,W503
cd services/payment-service && flake8 app/ --max-line-length=120 --extend-ignore=E203,W503

# Fix all issues
black app/ --line-length=120
isort app/ --profile=black

# Re-run to verify
flake8 app/
```

**Commit:** `fix: resolve linting issues across all services`

---

### 1.2 Fix Type Checking (mypy)
**Branch:** `fix/ci-type-checking`  
**Configuration:** Add `mypy.ini` or `pyproject.toml` section

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin
```

**Actions:**
```bash
# Check each service
mypy services/user-service/app --ignore-missing-imports
mypy services/course-service/app --ignore-missing-imports
mypy services/enrollment-service/app --ignore-missing-imports
mypy services/payment-service/app --ignore-missing-imports

# Fix type hints incrementally
```

**Commit:** `fix: add proper type hints and mypy configuration`

---

### 1.3 Enhanced CI Workflow
**File:** `.github/workflows/ci.yml`  
**Branch:** `fix/ci-workflow-enhancement`

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, development, feature/*, fix/* ]
  pull_request:
    branches: [ main, development ]

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [user-service, course-service, enrollment-service, payment-service]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install flake8 black isort mypy
      
      - name: Run flake8
        run: |
          cd services/${{ matrix.service }}
          flake8 app/ --max-line-length=120 --extend-ignore=E203,W503
      
      - name: Check black formatting
        run: |
          cd services/${{ matrix.service }}
          black --check app/ --line-length=120
      
      - name: Check isort
        run: |
          cd services/${{ matrix.service }}
          isort --check-only app/ --profile=black
      
      - name: Run mypy
        run: |
          cd services/${{ matrix.service }}
          mypy app/ --ignore-missing-imports || true

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [user-service, course-service, enrollment-service, payment-service]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install security tools
        run: |
          pip install bandit safety
      
      - name: Run bandit
        run: |
          cd services/${{ matrix.service }}
          bandit -r app/ -ll -f json -o bandit-report.json || true
      
      - name: Check dependencies with safety
        run: |
          cd services/${{ matrix.service }}
          safety check --json || true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports-${{ matrix.service }}
          path: services/${{ matrix.service }}/*-report.json

  test:
    name: Unit & Integration Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [user-service, course-service, enrollment-service, payment-service]
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio httpx
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd services/${{ matrix.service }}
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=html
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: services/${{ matrix.service }}/coverage.xml
          flags: ${{ matrix.service }}
          name: ${{ matrix.service }}-coverage

  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [lint, test]
    strategy:
      matrix:
        service: [user-service, course-service, enrollment-service, payment-service]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build Docker image
        run: |
          cd services/${{ matrix.service }}
          docker build -t mlh-${{ matrix.service }}:${{ github.sha }} .
      
      - name: Save Docker image
        run: |
          docker save mlh-${{ matrix.service }}:${{ github.sha }} > ${{ matrix.service }}.tar
      
      - name: Upload image artifact
        uses: actions/upload-artifact@v3
        with:
          name: docker-images
          path: ${{ matrix.service }}.tar

  integration-test:
    name: Integration Tests (Docker Compose)
    runs-on: ubuntu-latest
    needs: [build]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services with docker-compose
        run: |
          docker-compose up -d
          sleep 30
      
      - name: Health checks
        run: |
          curl -f http://localhost:8001/health || exit 1
          curl -f http://localhost:8002/health || exit 1
          curl -f http://localhost:8003/health || exit 1
          curl -f http://localhost:8004/health || exit 1
      
      - name: Run integration tests
        run: |
          pip install pytest httpx
          pytest tests/integration/ -v
      
      - name: Show logs on failure
        if: failure()
        run: |
          docker-compose logs
      
      - name: Cleanup
        if: always()
        run: |
          docker-compose down -v
```

**Commit:** `feat: comprehensive CI pipeline with parallel testing and security scanning`

---

## 📋 Phase 2: Add Missing Test Suite

### 2.1 Unit Tests (Per Service)
**Branch:** `feature/unit-tests`  
**Target Coverage:** Comprehensive

**File Structure:**
```
services/{service}/tests/
├── __init__.py
├── conftest.py  # Fixtures
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_repositories.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── performance/
    └── test_load.py
```

**Example: User Service Unit Tests**

`tests/conftest.py`:
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.core.config import settings

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()
```

`tests/unit/test_services.py`:
```python
import pytest
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user(db_session):
    # Arrange
    repo = UserRepository(db_session)
    service = UserService(repo)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="SecurePass123!",
        role="STUDENT"
    )
    
    # Act
    user = await service.create_user(user_data)
    
    # Assert
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password != "SecurePass123!"  # Should be hashed
```

**Commit per service:**
- `test: add comprehensive unit tests for user-service`
- `test: add comprehensive unit tests for course-service`
- `test: add comprehensive unit tests for enrollment-service`
- `test: add comprehensive unit tests for payment-service`

---

### 2.2 Integration Tests
**Branch:** `feature/integration-tests`

`tests/integration/test_user_flow.py`:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_signup_login_flow():
    async with AsyncClient(base_url="http://localhost:8001") as client:
        # Signup
        signup_response = await client.post("/api/v1/auth/signup", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "role": "STUDENT"
        })
        assert signup_response.status_code == 201
        
        # Login
        login_response = await client.post("/api/v1/auth/login", data={
            "username": "newuser",
            "password": "SecurePass123!"
        })
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
```

**Commit:** `test: add end-to-end integration tests for core workflows`

---

### 2.3 Performance Tests (Locust)
**Branch:** `feature/performance-tests`

**File:** `tests/performance/locustfile.py`
```python
from locust import HttpUser, task, between

class MLHUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "TestPass123!"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def list_courses(self):
        self.client.get("/api/v1/courses/", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(2)
    def get_course_details(self):
        self.client.get("/api/v1/courses/1", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def enroll_in_course(self):
        self.client.post("/api/v1/enrollments/", json={
            "course_id": 1
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })
```

**Run:**
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8001 --users=100 --spawn-rate=10
```

**Commit:** `test: add Locust performance tests with 100 concurrent users`

---

## 📋 Phase 3: Kubernetes Manifests

### 3.1 Create K8s Deployment Files
**Branch:** `feature/kubernetes-deployment`

**File Structure:**
```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml
├── postgres-statefulset.yaml
├── redis-deployment.yaml
├── mongodb-statefulset.yaml
├── user-service/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── course-service/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── enrollment-service/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── payment-service/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
└── ingress.yaml
```

**Example:** `k8s/user-service/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: mlh-platform
  labels:
    app: user-service
    version: v1.0.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1.0.0
    spec:
      containers:
      - name: user-service
        image: mlh-user-service:latest
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mlh-secrets
              key: user-db-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: mlh-secrets
              key: jwt-secret
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: mlh-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: mlh-platform
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8001
    name: http
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
  namespace: mlh-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Commit:** `feat: add complete Kubernetes manifests with HPA and StatefulSets`

---

## 📋 Phase 4: CI Badges & Documentation

### 4.1 Add CI Badge to README
**File:** `README.md`

```markdown
# Modular Learning Hub (MLH)

![CI](https://img.shields.io/badge/CI-GitHub%20Actions-blue)
![Coverage](https://img.shields.io/badge/coverage-check-green)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
```

---