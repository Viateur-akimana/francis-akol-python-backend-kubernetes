# Local Development Setup

This guide covers setting up the MLH platform for local development.

## Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **Git**

## Quick Start

### 1. Clone Repository
```bash
git clone git@github.com:franakol/francis-akol-python-backend-assessment.git
cd francis-akol-python-backend-assessment
```

### 2. Start Infrastructure
```bash
docker-compose up -d postgres redis mongodb
```

### 3. Setup Each Service

```bash
# User Service
cd services/user-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Repeat for other services on ports 8002, 8003, 8004.

### 4. Start All Services (Docker)
```bash
docker-compose up -d
```

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| User Service | 8001 | http://localhost:8001 |
| Course Service | 8002 | http://localhost:8002 |
| Enrollment Service | 8003 | http://localhost:8003 |
| Payment Service | 8004 | http://localhost:8004 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

## API Documentation

Each service exposes Swagger docs:
- User: http://localhost:8001/docs
- Course: http://localhost:8002/docs
- Enrollment: http://localhost:8003/docs
- Payment: http://localhost:8004/docs

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Running Tests

```bash
cd services/user-service
pytest tests/ -v --cov=app
```

## Troubleshooting

### Database Connection Failed
- Ensure PostgreSQL is running: `docker ps`
- Check DATABASE_URL in .env

### Redis Connection Failed
- Ensure Redis is running: `docker ps`
- Check REDIS_URL in .env

### Port Already in Use
- Find process: `lsof -i :8001`
- Kill process: `kill -9 <PID>`
