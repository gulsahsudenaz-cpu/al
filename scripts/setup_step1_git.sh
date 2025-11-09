#!/bin/bash
# Aşama 1: Git Repository Hazırlığı

set -e

echo "🚀 Aşama 1: Git Repository Hazırlığı"
echo "======================================"

# Git repository kontrolü
if [ ! -d ".git" ]; then
    echo "📦 Git repository oluşturuluyor..."
    git init
    echo "✅ Git repository oluşturuldu"
else
    echo "✅ Git repository zaten mevcut"
fi

# .gitignore kontrolü
if [ ! -f ".gitignore" ]; then
    echo "⚠️  .gitignore dosyası bulunamadı"
else
    echo "✅ .gitignore dosyası mevcut"
fi

# Dosyaları ekle
echo "📝 Dosyalar Git'e ekleniyor..."
git add .

# Commit
echo "💾 İlk commit oluşturuluyor..."
git commit -m "Initial commit: AI Chatbot System v2.0

- FastAPI backend with RAG and LLM integration
- Web Widget and Admin Panel frontend
- PostgreSQL with pgvector
- Redis for caching and queues
- WebSocket real-time communication
- Monitoring with OpenTelemetry and Prometheus
- CI/CD with GitHub Actions
- Railway deployment ready
- Comprehensive test suite
- Production-ready architecture"

echo "✅ Git repository hazır!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. GitHub'da yeni repository oluşturun"
echo "2. git remote add origin https://github.com/YOUR_USERNAME/chatbot.git"
echo "3. git push -u origin main"
echo ""
echo "Veya şu komutu çalıştırın:"
echo "  git remote add origin https://github.com/YOUR_USERNAME/chatbot.git"
echo "  git branch -M main"
echo "  git push -u origin main"

