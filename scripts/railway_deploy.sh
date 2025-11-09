#!/bin/bash
# Railway deployment helper script

set -e

echo "🚀 Railway Deployment Helper"
echo "============================"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm i -g @railway/cli || {
        echo "⚠️  npm not found. Please install Railway CLI manually:"
        echo "   npm i -g @railway/cli"
        echo "   or"
        echo "   brew install railway"
        exit 1
    }
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Check if project is linked
if [ ! -f .railway/project.json ]; then
    echo "📦 Linking Railway project..."
    railway link
fi

# Set environment variables
echo "📝 Setting environment variables..."
echo "Please set these in Railway dashboard:"
echo "  - OPENAI_API_KEY"
echo "  - SECRET_KEY"
echo "  - JWT_SECRET_KEY"
echo "  - MODEL (optional, default: gpt-4-turbo)"
echo ""
read -p "Press Enter to continue..."

# Run migrations
echo "🔄 Running database migrations..."
railway run cd backend && alembic upgrade head

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Check your Railway dashboard for the deployed URL"

