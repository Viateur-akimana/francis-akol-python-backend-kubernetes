# CI/CD Pipeline Guide

This document describes the CI/CD pipeline configuration for the MLH platform.

## Overview

The pipeline uses GitHub Actions for continuous integration and deployment.

## CI Pipeline (`.github/workflows/ci.yml`)

### Triggers
- Push to: `development`, `main`, `feature/*`, `fix/*`
- Pull requests to: `development`, `main`

### Jobs

#### 1. Code Quality Checks
Runs on every push/PR:
- **Black** - Code formatting check
- **isort** - Import sorting check
- **flake8** - Linting (syntax errors, undefined names)
- **mypy** - Type checking

#### 2. Tests
Runs after code quality passes:
- User service tests with PostgreSQL and Redis
- Coverage reports uploaded to Codecov

#### 3. Docker Build
Builds images for all 4 services:
- `mlh-user-service`
- `mlh-course-service`
- `mlh-enrollment-service`
- `mlh-payment-service`

#### 4. Security Scan
Runs Bandit security scanner on all services.

## Running Locally

### Simulate CI checks
```bash
# Code formatting
black --check services/
isort --check-only services/ --profile=black

# Linting
flake8 services/ --select=E9,F63,F7,F82

# Type checking
mypy services/user-service/app --ignore-missing-imports
```

### Run tests
```bash
cd services/user-service
pytest tests/ -v --cov=app
```

## Workflow Configuration

```yaml
name: CI Pipeline

on:
  push:
    branches: [development, main, feature/*, fix/*]
  pull_request:
    branches: [development, main]

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: pip install black isort flake8
      - run: black --check services/
      - run: isort --check-only services/ --profile=black
      - run: flake8 services/
```

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `development` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `hotfix/*` | Critical production fixes |

## Deployment Process

1. Create feature branch from `development`
2. Implement changes
3. Create PR to `development`
4. CI runs automatically
5. Code review and approval
6. Merge to `development`
7. Create PR from `development` to `main` for release

## CD Pipeline (Future)

Planned CD workflow:
1. Trigger on merge to `main`
2. Build and push Docker images
3. Deploy to staging
4. Run smoke tests
5. Manual approval for production
6. Deploy to production
