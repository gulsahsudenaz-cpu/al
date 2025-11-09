#!/bin/bash
# Aşama 3: Docker Servisleri

set -e

echo "🚀 Aşama 3: Docker Servisleri"
echo "=============================="

# Docker kontrolü
if ! command -v docker &> /dev/null; then
    echo "❌ Docker bulunamadı. Lütfen Docker'ı yükleyin."
    exit 1
fi

echo "✅ Docker mevcut: $(docker --version)"

# Docker Compose kontrolü
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose bulunamadı. Lütfen Docker Compose'u yükleyin."
    exit 1
fi

echo "✅ Docker Compose mevcut: $(docker-compose --version)"

# Infra dizinine git
cd infra

# .env dosyası kontrolü
if [ ! -f "../.env" ]; then
    echo "⚠️  .env dosyası bulunamadı. Lütfen önce .env dosyasını oluşturun."
    exit 1
fi

echo "✅ .env dosyası mevcut"

# Docker servislerini başlat
echo "🐳 Docker servisleri başlatılıyor..."
docker-compose up -d postgres redis

# Servislerin çalışmasını bekle
echo "⏳ Servislerin başlaması bekleniyor..."
sleep 10

# Servisleri kontrol et
echo "🔍 Servisler kontrol ediliyor..."
docker-compose ps

# PostgreSQL bağlantı testi
echo "🔍 PostgreSQL bağlantı testi..."
until docker-compose exec -T postgres pg_isready -U user; do
    echo "⏳ PostgreSQL başlatılıyor..."
    sleep 2
done
echo "✅ PostgreSQL hazır"

# Redis bağlantı testi
echo "🔍 Redis bağlantı testi..."
until docker-compose exec -T redis redis-cli ping; do
    echo "⏳ Redis başlatılıyor..."
    sleep 2
done
echo "✅ Redis hazır"

# pgvector extension kontrolü
echo "🔍 pgvector extension kontrolü..."
docker-compose exec -T postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;" || echo "⚠️  pgvector extension kurulumu başarısız"

echo ""
echo "✅ Docker servisleri hazır!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Database migrations çalıştırın: cd backend && alembic upgrade head"
echo "2. Backend'i başlatın: uvicorn app.main:app --reload --port 8000"
echo "3. Health check: curl http://localhost:8000/health"

