# Environment Variables

This document lists all environment variables used by the MLH platform.

## Common Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development`, `staging`, `production` |
| `DEBUG` | Enable debug mode | `true`, `false` |

## Database

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `DB_POOL_SIZE` | Connection pool size | `20` |
| `DB_MAX_OVERFLOW` | Max overflow connections | `10` |
| `DB_POOL_TIMEOUT` | Pool timeout (seconds) | `30` |
| `DB_POOL_RECYCLE` | Connection recycle time | `1800` |

## Redis

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `REDIS_CACHE_TTL` | Cache TTL (seconds) | `300` |

## Authentication

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | `your-secure-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |

## Celery

| Variable | Description | Example |
|----------|-------------|---------|
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Result backend URL | `redis://localhost:6379/1` |

## Inter-Service Communication

| Variable | Description | Example |
|----------|-------------|---------|
| `USER_SERVICE_URL` | User service URL | `http://localhost:8001` |
| `COURSE_SERVICE_URL` | Course service URL | `http://localhost:8002` |
| `ENROLLMENT_SERVICE_URL` | Enrollment service URL | `http://localhost:8003` |
| `PAYMENT_SERVICE_URL` | Payment service URL | `http://localhost:8004` |

## CORS

| Variable | Description | Example |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000,http://localhost:8000` |

## Service-Specific Ports

| Service | Port |
|---------|------|
| User Service | 8001 |
| Course Service | 8002 |
| Enrollment Service | 8003 |
| Payment Service | 8004 |

## Example .env File

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mlh_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# JWT
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Inter-service
USER_SERVICE_URL=http://localhost:8001
COURSE_SERVICE_URL=http://localhost:8002
ENROLLMENT_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Security Notes

⚠️ **Never commit `.env` files to version control**

- Use `.env.example` as a template
- Generate strong JWT secrets: `openssl rand -hex 32`
- Use different secrets per environment
- Store production secrets in secure vault (AWS Secrets Manager, HashiCorp Vault)
