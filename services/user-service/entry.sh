#!/bin/bash
# Entry script for User Service
# Runs migrations and starts the application

set -e

echo "🚀 Starting User Service..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U mlh_user -d mlh_db; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create database if it doesn't exist
echo "🔧 Ensuring database exists..."
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d mlh_db -c "CREATE DATABASE user_db;" 2>/dev/null || echo "Database user_db already exists or creation failed"
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d user_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || echo "UUID extension already exists"
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d user_db -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";" 2>/dev/null || echo "pg_trgm extension already exists"

# Wait for Redis
echo "⏳ Waiting for Redis..."
# Extract password from REDIS_URL or use default
REDIS_PASS=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/:\([^@]*\)@.*/\1/p')
REDIS_PASS=${REDIS_PASS:-mlh_redis_password}
while ! redis-cli -h redis -a "$REDIS_PASS" ping 2>/dev/null | grep -q PONG; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python -m alembic upgrade head
echo "✅ Migrations completed!"

# Start the application
echo "🏁 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
