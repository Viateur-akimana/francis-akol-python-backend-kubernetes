# Railway Deployment Guide

This guide explains how to deploy the MLH Platform microservices to Railway.

## Architecture on Railway

```
Railway Project: mlh-platform
├── PostgreSQL (shared database with multiple schemas)
├── Redis (shared cache & broker)
├── user-service (port 8001)
├── course-service (port 8002)
├── enrollment-service (port 8003)
└── payment-service (port 8004)
```

## Prerequisites

1. A Railway account ([railway.app](https://railway.app))
2. GitHub repository connected to Railway

## Step-by-Step Deployment

### 1. Create a New Project on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Empty Project"**

### 2. Add PostgreSQL Database

1. In your project, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will provision PostgreSQL automatically
3. Copy the connection URL from the PostgreSQL service variables

### 3. Add Redis

1. Click **"+ New"** → **"Database"** → **"Add Redis"**
2. Copy the Redis URL for cache configuration

### 4. Deploy Each Microservice

For each service (user, course, enrollment, payment):

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository: `francis-akol-python-backend-assessment`
3. In service settings, set **Root Directory**:
   - user-service: `services/user-service`
   - course-service: `services/course-service`
   - enrollment-service: `services/enrollment-service`
   - payment-service: `services/payment-service`

### 5. Configure Environment Variables

For each service, add these variables in Railway:

#### Common Variables (All Services)
```
ENVIRONMENT=production
DEBUG=false
```

#### user-service
```
DATABASE_URL=${{Postgres.DATABASE_URL}}/user_db
REDIS_URL=${{Redis.REDIS_URL}}
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
PORT=8001
```

#### course-service
```
DATABASE_URL=${{Postgres.DATABASE_URL}}/course_db
REDIS_URL=${{Redis.REDIS_URL}}
USER_SERVICE_URL=${{user-service.RAILWAY_PUBLIC_DOMAIN}}
PORT=8002
```

#### enrollment-service
```
DATABASE_URL=${{Postgres.DATABASE_URL}}/enrollment_db
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}/1
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}/2
USER_SERVICE_URL=${{user-service.RAILWAY_PUBLIC_DOMAIN}}
COURSE_SERVICE_URL=${{course-service.RAILWAY_PUBLIC_DOMAIN}}
PORT=8003
```

#### payment-service
```
DATABASE_URL=${{Postgres.DATABASE_URL}}/payment_db
USER_SERVICE_URL=${{user-service.RAILWAY_PUBLIC_DOMAIN}}
COURSE_SERVICE_URL=${{course-service.RAILWAY_PUBLIC_DOMAIN}}
ENROLLMENT_SERVICE_URL=${{enrollment-service.RAILWAY_PUBLIC_DOMAIN}}
PAYMENT_GATEWAY_API_KEY=<your-api-key>
PORT=8004
```

### 6. Generate Domains

For each service:
1. Go to service **Settings** → **Networking**
2. Click **"Generate Domain"** to get a public URL

### 7. Verify Deployment

Test each service health endpoint:
```bash
curl https://user-service-xxx.up.railway.app/health
curl https://course-service-xxx.up.railway.app/health
curl https://enrollment-service-xxx.up.railway.app/health
curl https://payment-service-xxx.up.railway.app/health
```

## Free Tier Limits

Railway's free tier includes:
- $5/month in credits
- ~500 hours of execution time
- Containers sleep after inactivity

## Troubleshooting

### Database Migrations
Services run migrations on startup via `entry.sh`. Check logs if migrations fail.

### Service Communication
Ensure environment variables reference the correct Railway internal URLs.

### Build Failures
Check that the Dockerfile builds correctly locally before deploying.
