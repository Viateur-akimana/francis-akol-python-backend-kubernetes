#!/bin/bash
# Entry script for Payment Service
# Runs migrations and starts the application

set -e

echo "🚀 Starting Payment Service..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U mlh_user -d mlh_db; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create database if it doesn't exist
echo "🔧 Ensuring database exists..."
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d mlh_db -c "CREATE DATABASE payment_db;" 2>/dev/null || echo "Database payment_db already exists or creation failed"
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d payment_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || echo "UUID extension already exists"

# Run database migrations
echo "🔄 Running database migrations..."
python -m alembic upgrade head
echo "✅ Migrations completed!"

# Start the application
echo "🏁 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
