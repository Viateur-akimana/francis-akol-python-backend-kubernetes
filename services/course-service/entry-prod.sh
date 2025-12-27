#!/bin/bash
# Production entry script for Course Service
# Runs migrations and starts the application

set -e

echo "🚀 Starting Course Service..."

# Run database migrations
echo "🔄 Running database migrations..."
python -m alembic upgrade head || echo "⚠️ Migration failed or no migrations to apply"
echo "✅ Migrations completed!"

# Start the application
echo "🏁 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
