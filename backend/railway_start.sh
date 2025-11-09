#!/bin/bash
# Railway startup script

set -e

echo "🚀 Starting AI Chatbot on Railway..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h $PGHOST -p $PGPORT -U $PGUSER; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
until redis-cli -u $REDIS_URL ping; do
  sleep 1
done
echo "Redis is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head || echo "Migrations failed, continuing..."

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

