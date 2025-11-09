#!/bin/bash
# Railway startup script

set -e

echo "🚀 Starting AI Chatbot on Railway..."

# Run migrations
echo "Running database migrations..."
cd backend
alembic upgrade head || echo "Migrations failed, continuing..."

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT

