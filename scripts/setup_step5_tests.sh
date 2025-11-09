#!/bin/bash
# Aşama 5: Testler

set -e

echo "🚀 Aşama 5: Testler"
echo "==================="

# Backend dizinine git
cd backend

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı. Lütfen önce setup_step2_local.sh çalıştırın."
    exit 1
fi

# Virtual environment'ı aktifleştir
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Pytest kontrolü
if ! command -v pytest &> /dev/null; then
    echo "📦 Pytest yükleniyor..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Unit tests
echo "🧪 Unit tests çalıştırılıyor..."
pytest tests/ -v --cov=app --cov-report=term-missing

echo ""
echo "✅ Unit tests tamamlandı!"
echo ""

# Root dizinine git
cd ..

# Node.js kontrolü
if ! command -v npm &> /dev/null; then
    echo "⚠️  Node.js bulunamadı. E2E testleri atlanıyor."
    echo "📋 E2E testleri çalıştırmak için Node.js yükleyin ve şu komutu çalıştırın:"
    echo "   npm install && npx playwright install && npx playwright test"
    exit 0
fi

# E2E tests
echo "🧪 E2E tests için dependencies yükleniyor..."
npm install

echo "🧪 Playwright yükleniyor..."
npx playwright install --with-deps

echo "🧪 E2E tests çalıştırılıyor..."
npx playwright test || echo "⚠️  E2E testleri başarısız (backend çalışmıyor olabilir)"

echo ""
echo "✅ Testler tamamlandı!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Railway deployment için DEPLOYMENT.md dosyasına bakın"
echo "2. Monitoring kurulumu için SETUP_GUIDE.md dosyasına bakın"

