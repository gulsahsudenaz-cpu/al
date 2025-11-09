# 🚂 Railway Deployment Rehberi

## 📋 Ön Hazırlık

1. **GitHub Repository Oluşturun**
   - https://github.com/new
   - Repository name: `chatbot`
   - README, .gitignore eklemeyin (zaten var)

2. **GitHub'a Push Edin**
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
   git branch -M main
   git push -u origin main
   ```

---

## 🚀 Railway Deployment

### Adım 1: Railway Hesabı ve Proje

1. **Railway'a gidin:** https://railway.app
2. **Hesap oluşturun:** GitHub ile login yapın
3. **Proje oluşturun:**
   - "New Project" → "Deploy from GitHub repo"
   - Repository'nizi seçin
   - "Deploy" butonuna tıklayın

### Adım 2: PostgreSQL Plugin

1. **PostgreSQL ekleyin:**
   - "+ New" → "Database" → "Add PostgreSQL"

2. **pgvector extension:**
   - PostgreSQL servisine tıklayın
   - "Query" sekmesine gidin
   - Şu SQL'i çalıştırın:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

### Adım 3: Redis Plugin

1. **Redis ekleyin:**
   - "+ New" → "Database" → "Add Redis"

### Adım 4: Environment Variables

Railway dashboard → Backend service → Variables:

```env
# Zorunlu
OPENAI_API_KEY=sk-your-openai-api-key
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Opsiyonel
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0
DEBUG=False
RAG_MIN_SIMILARITY=0.7
ENABLE_METRICS=True
```

**NOT:** `DATABASE_URL` ve `REDIS_URL` Railway tarafından otomatik sağlanır.

### Adım 5: Telegram Webhook

Deploy sonrası:

```powershell
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"
curl -X POST https://your-app.railway.app/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

---

## ✅ Kontrol

- Health: `https://your-app.railway.app/health`
- API Docs: `https://your-app.railway.app/docs`
- Webhook Info: `https://your-app.railway.app/v1/telegram/webhook-info`

---

## 🆘 Sorun Giderme

### Deploy Başarısız
- Logları kontrol edin: Railway dashboard → Deployments → Logs
- Dependencies eksik mi?
- Environment variables doğru mu?

### Database Bağlantı Hatası
- PostgreSQL servisi çalışıyor mu?
- `POSTGRES_URL` environment variable var mı?
- pgvector extension kurulu mu?

### Telegram Webhook Hatası
- Webhook URL HTTPS mi?
- Backend çalışıyor mu?
- `TELEGRAM_BOT_TOKEN` doğru mu?
