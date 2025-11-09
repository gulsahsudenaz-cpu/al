#!/bin/bash
# Aşama 4: Database Migrations

set -e

echo "🚀 Aşama 4: Database Migrations"
echo "==============================="

# Backend dizinine git
cd backend

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı. Lütfen önce setup_step2_local.sh çalıştırın."
    exit 1
fi

# Virtual environment'ı aktifleştir
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# .env dosyası kontrolü
if [ ! -f "../.env" ]; then
    echo "⚠️  .env dosyası bulunamadı. Lütfen önce .env dosyasını oluşturun."
    exit 1
fi

# Environment variables yükle
export $(cat ../.env | grep -v '^#' | xargs)

# DATABASE_URL kontrolü
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL environment variable'ı ayarlanmamış"
    echo "📝 Varsayılan DATABASE_URL kullanılıyor: postgresql://user:password@localhost:5432/chatbot"
    export DATABASE_URL="postgresql://user:password@localhost:5432/chatbot"
fi

# Alembic kontrolü
if ! command -v alembic &> /dev/null; then
    echo "📦 Alembic yükleniyor..."
    pip install alembic
fi

# Migrations çalıştır
echo "🔄 Database migrations çalıştırılıyor..."
alembic upgrade head

echo ""
echo "✅ Database migrations tamamlandı!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Backend'i başlatın: uvicorn app.main:app --reload --port 8000"
echo "2. Health check: curl http://localhost:8000/health"
echo "3. API docs: http://localhost:8000/docs"

