#!/bin/bash
# Entry script for Course Service
# Runs migrations and starts the application

set -e

echo "🚀 Starting Course Service..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U mlh_user -d mlh_db; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create database if it doesn't exist
echo "🔧 Ensuring database exists..."
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d mlh_db -c "CREATE DATABASE course_db;" 2>/dev/null || echo "Database course_db already exists or creation failed"
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d course_db -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || echo "UUID extension already exists"
PGPASSWORD=mlh_secure_password psql -h postgres -U mlh_user -d course_db -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";" 2>/dev/null || echo "pg_trgm extension already exists"

# Wait for MongoDB using Python
echo "⏳ Waiting for MongoDB..."
python3 -c "
import pymongo
import time
import os

# Use MONGODB_URL from environment or fallback to default
mongodb_url = os.environ.get('MONGODB_URL', 'mongodb://mlh_mongo_user:mlh_mongo_password@mongodb:27017/mlh_content_db?authSource=admin')

while True:
    try:
        client = pymongo.MongoClient(mongodb_url)
        client.admin.command('ping')
        print('✅ MongoDB is ready!')
        break
    except Exception as e:
        print(f'MongoDB is unavailable - sleeping ({e})')
        time.sleep(2)
"

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
exec uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
