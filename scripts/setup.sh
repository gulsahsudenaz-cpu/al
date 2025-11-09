#!/bin/bash
# Setup Script - Automated Installation

set -e

echo "🚀 Starting AI Chatbot Setup..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Start Docker services
echo "Starting Docker services..."
cd infra
docker-compose up -d postgres redis
cd ..

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
cd backend
alembic upgrade head
cd ..

# Create initial admin user
echo "Creating initial admin user..."
python3 scripts/create_admin.py

echo "✅ Setup complete!"
echo "Run 'docker-compose up' in the infra directory to start all services"

