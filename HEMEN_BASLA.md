# ⚡ Hemen Başla - 3 Adımda Çalıştır

## 🎯 Hızlı Başlangıç

### ⚠️ ÖNEMLİ: Docker Desktop'ı Başlatın

**Docker Desktop çalışmıyor!** Önce Docker Desktop'ı başlatın.

---

## 📋 3 Adımda Çalıştır

### Adım 1: .env Dosyasını Düzenleyin (2 dakika)

```powershell
# .env dosyasını açın
notepad .env

# OPENAI_API_KEY değerini değiştirin
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Dosyayı kaydedin
```

---

### Adım 2: Docker Servislerini Başlatın (1 dakika)

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

### Adım 3: Backend'i Başlatın (1 dakika)

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

## 🤖 Telegram Webhook (Opsiyonel)

```powershell
# ngrok ile (lokal test)
ngrok http 8000

# Webhook'u ayarlayın
$webhookUrl = "https://your-ngrok-url.ngrok.io/v1/telegram/webhook"
curl -X POST http://localhost:8000/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

---

## 🆘 Sorun mu?

- Docker çalışmıyor? → Docker Desktop'ı başlatın
- .env dosyası yok? → `notepad .env` ile oluşturun
- Backend başlamıyor? → Virtual environment aktif mi kontrol edin

---

## 📚 Daha Fazla Bilgi

- [SONRAKI_ADIMLAR_DETAYLI.md](SONRAKI_ADIMLAR_DETAYLI.md) - Detaylı rehber
- [TELEGRAM_COMPLETE.md](TELEGRAM_COMPLETE.md) - Telegram kurulumu
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment

---

## 🎉 Hazırsınız!

**İyi çalışmalar! 🚀**

