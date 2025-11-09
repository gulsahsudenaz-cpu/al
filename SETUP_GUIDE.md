# 📖 Detaylı Kurulum Rehberi

## 🎯 Genel Bakış

Bu rehber, projeyi sıfırdan kurmanız için adım adım talimatlar içerir.

---

## 📋 Gereksinimler

- Python 3.11+
- Docker Desktop
- PostgreSQL 15+ (pgvector)
- Redis 7+
- OpenAI API Key
- Telegram Bot Token

---

## 🚀 Kurulum Adımları

### 1. Git Repository

```powershell
# Git repository zaten oluşturuldu
# GitHub'a push etmek için:
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
git branch -M main
git push -u origin main
```

### 2. Lokal Geliştirme Ortamı

```powershell
# Backend dizinine git
cd backend

# Virtual environment oluştur
python -m venv venv

# Aktifleştir (Windows)
.\venv\Scripts\Activate.ps1

# Dependencies yükle
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Root'a dön
cd ..
```

### 3. Environment Variables

```powershell
# .env dosyasını oluştur (zaten var)
notepad .env

# ZORUNLU değişkenler:
# - OPENAI_API_KEY=sk-your-key-here
# - TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
# - SECRET_KEY=your-secret-key
# - JWT_SECRET_KEY=your-jwt-secret-key
```

### 4. Docker Servisleri

```powershell
# Docker Desktop'ı başlatın (manuel)

# Servisleri başlat
cd infra
docker-compose up -d postgres redis

# Servislerin başlamasını bekle
Start-Sleep -Seconds 15

# pgvector extension
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Kontrol et
docker-compose ps

cd ..
```

### 5. Database Migrations

```powershell
# Backend dizinine git
cd backend

# Virtual environment aktif
.\venv\Scripts\Activate.ps1

# Environment variables yükle
Get-Content ..\.env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Alembic için sync driver
$env:DATABASE_URL = $env:DATABASE_URL -replace "postgresql\+asyncpg://", "postgresql://"

# Migrations çalıştır
alembic upgrade head

cd ..
```

### 6. Backend'i Başlat

```powershell
# Backend dizininde (virtual environment aktif)
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### 7. Test Et

```powershell
# Health check
curl http://localhost:8000/health

# API docs
# http://localhost:8000/docs
```

---

## 🧪 Test

### Unit Tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

### E2E Tests

```powershell
npx playwright test
```

---

## 📚 Sonraki Adımlar

1. İlk admin kullanıcısını oluşturun
2. Knowledge base dokümanları ekleyin
3. RAG sistemini test edin
4. Telegram webhook'u ayarlayın
5. Railway'a deploy edin

---

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
- Docker Desktop'ı başlatın
- Tamamen açılmasını bekleyin
- `docker ps` ile test edin

### Database Bağlantı Hatası
- Docker servislerinin çalıştığını kontrol edin
- `DATABASE_URL` doğru mu kontrol edin
- PostgreSQL container'ın sağlıklı olduğunu kontrol edin

### Migrations Hatası
- Database URL'i kontrol edin
- PostgreSQL'in çalıştığından emin olun
- pgvector extension'ını manuel kurun

### Backend Başlamıyor
- Virtual environment aktif mi kontrol edin
- Dependencies yüklendi mi kontrol edin
- Environment variables doğru mu kontrol edin
- Port 8000 kullanımda mı kontrol edin

---

## 📚 İlgili Dokümantasyon

- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment
- [TELEGRAM.md](TELEGRAM.md) - Telegram bot kurulumu
