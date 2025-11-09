# 🚂 Railway Deployment - Adım Adım Rehber

## 📋 Ön Hazırlık

### ✅ Tamamlananlar
- ✅ Git repository oluşturuldu
- ✅ Tüm kodlar commit edildi
- ✅ Railway configuration dosyaları hazır
- ✅ Telegram bot token yapılandırıldı

### ⚠️ Yapılması Gerekenler
- [ ] GitHub repository oluşturuldu
- [ ] GitHub'a push edildi
- [ ] Railway hesabı oluşturuldu
- [ ] Railway'de proje oluşturuldu

---

## 🚀 Railway Deployment Adımları

### Adım 1: GitHub Repository Oluşturun

1. **GitHub'a gidin:**
   - https://github.com/new

2. **Repository oluşturun:**
   - Repository name: `chatbot` (veya istediğiniz ad)
   - Description: "AI Chatbot System with RAG, LLM, Telegram"
   - Public veya Private seçin
   - **ÖNEMLİ:** README, .gitignore, license **EKLEMEYIN** (zaten var)

3. **Repository oluştur butonuna tıklayın**

---

### Adım 2: GitHub'a Push Edin

```powershell
# GitHub remote ekleyin (YOUR_USERNAME'i değiştirin)
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git

# Branch'i main olarak ayarlayın
git branch -M main

# GitHub'a push edin
git push -u origin main
```

**Beklenen çıktı:**
```
Enumerating objects: ...
Writing objects: ...
To https://github.com/YOUR_USERNAME/chatbot.git
 * [new branch]      main -> main
```

---

### Adım 3: Railway Hesabı Oluşturun

1. **Railway'a gidin:**
   - https://railway.app

2. **Hesap oluşturun:**
   - "Start a New Project" butonuna tıklayın
   - GitHub ile login yapın
   - Railway'ın GitHub repository'nize erişim izni verin

---

### Adım 4: Railway'de Proje Oluşturun

1. **Yeni proje oluşturun:**
   - Railway dashboard'da "New Project" butonuna tıklayın
   - "Deploy from GitHub repo" seçin
   - Repository'nizi seçin (`chatbot`)
   - "Deploy" butonuna tıklayın

2. **Railway otomatik olarak:**
   - Repository'yi clone eder
   - Build işlemini başlatır
   - Deploy eder

---

### Adım 5: PostgreSQL Plugin Ekleyin

1. **PostgreSQL ekleyin:**
   - Railway dashboard'da "+ New" butonuna tıklayın
   - "Database" → "Add PostgreSQL" seçin
   - PostgreSQL servisi oluşturulacak

2. **pgvector extension'ını aktifleştirin:**
   - PostgreSQL servisine tıklayın
   - "Query" sekmesine gidin
   - Şu SQL'i çalıştırın:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

3. **Database URL'i not edin:**
   - PostgreSQL servisinde "Variables" sekmesine gidin
   - `DATABASE_URL` veya `POSTGRES_URL` değerini not edin
   - Railway otomatik olarak `POSTGRES_URL` environment variable'ını ekler

---

### Adım 6: Redis Plugin Ekleyin

1. **Redis ekleyin:**
   - Railway dashboard'da "+ New" butonuna tıklayın
   - "Database" → "Add Redis" seçin
   - Redis servisi oluşturulacak

2. **Redis URL'i not edin:**
   - Redis servisinde "Variables" sekmesine gidin
   - `REDIS_URL` veya `REDISCLOUD_URL` değerini not edin
   - Railway otomatik olarak `REDISCLOUD_URL` environment variable'ını ekler

---

### Adım 7: Environment Variables Ayarlayın

Railway dashboard'da backend servisine tıklayın → "Variables" sekmesine gidin:

#### Zorunlu Variables

```env
# OpenAI (ZORUNLU)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Telegram (ZORUNLU)
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8

# Security
SECRET_KEY=your-secure-secret-key-change-in-production
JWT_SECRET_KEY=your-secure-jwt-secret-key-change-in-production
```

#### Opsiyonel Variables

```env
# Model
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0

# RAG
RAG_MIN_SIMILARITY=0.7
RAG_MAX_DOCUMENTS=5

# Monitoring
ENABLE_METRICS=True
DEBUG=False
```

**NOT:** `DATABASE_URL` ve `REDIS_URL` Railway tarafından otomatik sağlanır.

---

### Adım 8: Deploy ve Kontrol

1. **Deploy durumunu kontrol edin:**
   - Railway dashboard'da "Deployments" sekmesine gidin
   - Deploy loglarını kontrol edin
   - Başarılı deploy'u bekleyin

2. **Health check:**
   - Railway dashboard'da backend servisine tıklayın
   - "Settings" → "Domains" sekmesine gidin
   - Domain'i not edin (örn: `your-app.railway.app`)
   - Health check: `https://your-app.railway.app/health`

3. **API docs:**
   - `https://your-app.railway.app/docs`

---

### Adım 9: Telegram Webhook Ayarlayın

Backend deploy edildikten sonra:

```powershell
# Railway URL'inizi kullanın
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"

# Webhook'u ayarlayın
curl -X POST https://your-app.railway.app/v1/telegram/set-webhook `
  -H "Content-Type: application/json" `
  -d "{\"webhook_url\": \"$webhookUrl\"}"

# Webhook bilgisini kontrol edin
curl https://your-app.railway.app/v1/telegram/webhook-info
```

---

## 🔧 Railway Configuration

### Procfile

```
web: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && python -m rq worker --url $REDIS_URL
```

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### nixpacks.toml

```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r backend/requirements.txt"]

[start]
cmd = "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

---

## 📊 Monitoring

### Railway Metrics

- Railway dashboard'da "Metrics" sekmesine gidin
- CPU, Memory, Network kullanımını görüntüleyin
- Logları kontrol edin

### Health Check

```powershell
# Health check endpoint
curl https://your-app.railway.app/health

# Metrics endpoint
curl https://your-app.railway.app/metrics
```

---

## 🆘 Sorun Giderme

### Deploy Başarısız

1. **Logları kontrol edin:**
   - Railway dashboard → Deployments → Logs

2. **Build hatası:**
   - Dependencies eksik mi?
   - Python version doğru mu?
   - Requirements.txt doğru mu?

3. **Runtime hatası:**
   - Environment variables doğru mu?
   - Database bağlantısı çalışıyor mu?
   - Redis bağlantısı çalışıyor mu?

### Database Bağlantı Hatası

1. **PostgreSQL kontrolü:**
   - PostgreSQL servisi çalışıyor mu?
   - `POSTGRES_URL` environment variable var mı?
   - pgvector extension kurulu mu?

2. **Redis kontrolü:**
   - Redis servisi çalışıyor mu?
   - `REDISCLOUD_URL` environment variable var mı?

### Telegram Webhook Hatası

1. **Webhook kontrolü:**
   - Webhook URL doğru mu?
   - HTTPS kullanılıyor mu?
   - Backend çalışıyor mu?

2. **Token kontrolü:**
   - `TELEGRAM_BOT_TOKEN` doğru mu?
   - Environment variable ayarlı mı?

---

## 📚 İlgili Dokümantasyon

- [DEPLOYMENT.md](DEPLOYMENT.md) - Genel deployment rehberi
- [README.md](README.md) - Proje dokümantasyonu
- [TELEGRAM_COMPLETE.md](TELEGRAM_COMPLETE.md) - Telegram kurulumu

---

## 🎉 Başarılar!

Railway deployment tamamlandı! Artık production'da çalışıyor.

**İyi çalışmalar! 🚀**

