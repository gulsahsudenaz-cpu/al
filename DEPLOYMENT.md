# Railway Deployment Guide

## Railway'a Deploy Etme

### 1. Git Repository Hazırlığı

```bash
# Git repository'yi başlat
git init
git add .
git commit -m "Initial commit: AI Chatbot System"

# GitHub'a push et
git remote add origin https://github.com/yourusername/chatbot.git
git push -u origin main
```

### 2. Railway Projesi Oluşturma

1. [Railway](https://railway.app) hesabı oluşturun
2. "New Project" butonuna tıklayın
3. "Deploy from GitHub repo" seçin
4. Repository'nizi seçin
5. "Deploy" butonuna tıklayın

### 3. PostgreSQL Plugin Ekleme

1. Railway dashboard'da projenize gidin
2. "+ New" butonuna tıklayın
3. "Database" → "Add PostgreSQL" seçin
4. PostgreSQL servisi oluşturulacak

**Önemli**: PostgreSQL servisinde `pgvector` extension'ını aktifleştirin:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Redis Plugin Ekleme

1. "+ New" butonuna tıklayın
2. "Database" → "Add Redis" seçin
3. Redis servisi oluşturulacak

### 5. Environment Variables Ayarlama

Railway dashboard'da "Variables" sekmesine gidin ve şunları ekleyin:

```env
# Application
DEBUG=False
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key

# OpenAI (ZORUNLU)
OPENAI_API_KEY=sk-your-openai-api-key
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0

# Database (Otomatik - Railway tarafından sağlanır)
# DATABASE_URL veya POSTGRES_URL otomatik ayarlanır

# Redis (Otomatik - Railway tarafından sağlanır)
# REDIS_URL veya REDISCLOUD_URL otomatik ayarlanır

# RAG
RAG_MIN_SIMILARITY=0.7
RAG_MAX_DOCUMENTS=5
RAG_EMBEDDING_MODEL=text-embedding-3-small

# Telegram (Opsiyonel)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/v1/telegram/webhook

# CORS
CORS_ORIGINS=https://your-frontend-domain.com,https://your-admin-domain.com

# Monitoring (Opsiyonel)
OTEL_EXPORTER_OTLP_ENDPOINT=
ENABLE_METRICS=True
```

### 6. Build ve Deploy Ayarları

Railway otomatik olarak:
- `nixpacks.toml` veya `railway.json` dosyasını kullanır
- Python 3.11'i algılar
- `backend/requirements.txt` dosyasından bağımlılıkları yükler
- `backend/railway_start.sh` script'ini çalıştırır (varsa)

**Manuel Build Command** (gerekirse):
```bash
cd backend && pip install -r requirements.txt && alembic upgrade head
```

**Start Command**:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 7. Database Migrations

Railway deploy edildikten sonra migrations çalıştırın:

**Option 1: Railway CLI**
```bash
railway run alembic upgrade head
```

**Option 2: Railway Shell**
```bash
railway shell
cd backend
alembic upgrade head
```

**Option 3: Automatic (railway_start.sh içinde)**
Migrations otomatik olarak `railway_start.sh` script'inde çalıştırılır.

### 8. Health Check

Railway otomatik olarak `/health` endpoint'ini kontrol eder:
- Health check path: `/health`
- Timeout: 100 seconds

### 9. Custom Domain (Opsiyonel)

1. Railway dashboard'da "Settings" → "Networking" sekmesine gidin
2. "Generate Domain" butonuna tıklayın
3. Veya kendi domain'inizi ekleyin
4. SSL otomatik olarak sağlanır (Let's Encrypt)

### 10. Worker Service (Opsiyonel)

Background worker'ları çalıştırmak için:

1. "+ New" butonuna tıklayın
2. "Empty Service" seçin
3. GitHub repository'nizi bağlayın
4. "Settings" → "Deploy" sekmesinde:
   - Start Command: `cd backend && rq worker --url $REDIS_URL`

### 11. Environment Variables - Railway Otomatik

Railway otomatik olarak şu değişkenleri sağlar:
- `PORT`: Uygulama portu (Railway tarafından sağlanır)
- `POSTGRES_URL` veya `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL` veya `REDISCLOUD_URL`: Redis connection string

### 12. Logs ve Monitoring

- **Logs**: Railway dashboard'da "Logs" sekmesinden görüntüleyebilirsiniz
- **Metrics**: Railway dashboard'da "Metrics" sekmesinden görüntüleyebilirsiniz
- **Health Checks**: Otomatik olarak `/health` endpoint'i kontrol edilir

### 13. Troubleshooting

#### Database Connection Error
```bash
# PostgreSQL URL'i kontrol et
railway variables

# Connection test et
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

#### Redis Connection Error
```bash
# Redis URL'i kontrol et
railway variables

# Connection test et
railway run redis-cli -u $REDIS_URL ping
```

#### Migrations Failed
```bash
# Manuel olarak çalıştır
railway run cd backend && alembic upgrade head
```

#### Port Error
- Railway otomatik olarak `$PORT` environment variable'ını sağlar
- Uygulamanın `0.0.0.0:$PORT` üzerinde dinlemesi gerekir

### 14. Production Checklist

- [ ] Environment variables ayarlandı
- [ ] PostgreSQL pgvector extension aktif
- [ ] Redis bağlantısı test edildi
- [ ] Database migrations çalıştırıldı
- [ ] OpenAI API key ayarlandı
- [ ] Health check çalışıyor
- [ ] Custom domain yapılandırıldı (opsiyonel)
- [ ] SSL sertifikası aktif
- [ ] Worker service ayarlandı (opsiyonel)
- [ ] Monitoring yapılandırıldı
- [ ] Backup stratejisi oluşturuldu

### 15. Railway CLI Kurulumu

```bash
# npm ile
npm i -g @railway/cli

# veya brew ile
brew install railway

# Login
railway login

# Projeyi bağla
railway link

# Deploy
railway up
```

### 16. Continuous Deployment

Railway otomatik olarak:
- GitHub'a push yaptığınızda deploy eder
- Pull request'lerde preview deployment oluşturur
- Branch bazlı environment'lar oluşturabilirsiniz

### 17. Scaling

Railway'de scaling:
1. "Settings" → "Scaling" sekmesine gidin
2. Instance sayısını artırın
3. Resource limitlerini ayarlayın

### 18. Backup

Railway PostgreSQL için otomatik backup sağlar:
1. "Settings" → "Backups" sekmesine gidin
2. Backup schedule ayarlayın
3. Backup'ları indirebilirsiniz

## Örnek Railway Configuration

### railway.toml
```toml
[build]
builder = "nixpacks"
buildCommand = "cd backend && pip install -r requirements.txt && alembic upgrade head"

[deploy]
startCommand = "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
```

### Environment Variables Template
```env
DEBUG=False
SECRET_KEY=change-me-in-production
OPENAI_API_KEY=sk-...
MODEL=gpt-4-turbo
```

## Destek

Sorularınız için:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: GitHub Issues

