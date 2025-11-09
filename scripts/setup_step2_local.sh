#!/bin/bash
# Aşama 2: Lokal Geliştirme Ortamı

set -e

echo "🚀 Aşama 2: Lokal Geliştirme Ortamı"
echo "===================================="

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 bulunamadı. Lütfen Python 3.11+ yükleyin."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Backend dizinine git
cd backend

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3 -m venv venv
    echo "✅ Virtual environment oluşturuldu"
else
    echo "✅ Virtual environment zaten mevcut"
fi

# Virtual environment'ı aktifleştir
echo "🔧 Virtual environment aktifleştiriliyor..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Dependencies yükle
echo "📦 Dependencies yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements/dev.txt

echo "✅ Dependencies yüklendi"

# .env dosyası kontrolü
cd ..
if [ ! -f ".env" ]; then
    echo "📝 .env dosyası oluşturuluyor..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env dosyası oluşturuldu (.env.example'dan)"
        echo "⚠️  Lütfen .env dosyasını düzenleyin ve gerekli değişkenleri ayarlayın"
    else
        echo "⚠️  .env.example dosyası bulunamadı"
    fi
else
    echo "✅ .env dosyası mevcut"
fi

echo ""
echo "✅ Lokal geliştirme ortamı hazır!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. .env dosyasını düzenleyin (OPENAI_API_KEY, SECRET_KEY, etc.)"
echo "2. Docker servislerini başlatın: cd infra && docker-compose up -d postgres redis"
echo "3. Database migrations çalıştırın: cd backend && alembic upgrade head"
echo "4. Backend'i başlatın: uvicorn app.main:app --reload --port 8000"

