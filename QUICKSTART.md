# ⚡ Hızlı Başlangıç

## 🎯 3 Adımda Çalıştır

### ⚠️ ÖNEMLİ: Docker Desktop'ı Başlatın

Docker Desktop'ı açın ve tamamen başlamasını bekleyin.

---

### Adım 1: .env Dosyasını Düzenleyin

```powershell
# .env dosyasını açın
notepad .env

# OPENAI_API_KEY değerini değiştirin
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Dosyayı kaydedin
```

---

### Adım 2: Docker Servislerini Başlatın

```powershell
# Docker Desktop'ın çalıştığından emin olun
docker ps

# Servisleri başlat
cd infra
docker-compose up -d postgres redis
Start-Sleep -Seconds 15

# pgvector extension
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Root'a dön
cd ..
```

---

### Adım 3: Backend'i Başlatın

```powershell
# Backend dizinine git
cd backend

# Virtual environment aktifleştir
.\venv\Scripts\Activate.ps1

# Environment variables yükle
Get-Content ..\.env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

# Alembic için sync driver
$env:DATABASE_URL = $env:DATABASE_URL -replace "postgresql\+asyncpg://", "postgresql://"

# Migrations çalıştır
alembic upgrade head

# Backend'i başlat
uvicorn app.main:app --reload --port 8000
```

---

## ✅ Test Edin

```powershell
# Yeni terminal açın
curl http://localhost:8000/health

# Tarayıcıda
# http://localhost:8000/docs
```

---

## 📚 Daha Fazla Bilgi

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detaylı kurulum rehberi
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment
- [TELEGRAM.md](TELEGRAM.md) - Telegram bot kurulumu

---

## 🆘 Sorun Giderme

- Docker çalışmıyor? → Docker Desktop'ı başlatın
- .env dosyası yok? → `notepad .env` ile oluşturun
- Backend başlamıyor? → Virtual environment aktif mi kontrol edin
