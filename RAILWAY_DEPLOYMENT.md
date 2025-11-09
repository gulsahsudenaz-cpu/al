# 🚂 Railway Deployment Guide

## Adım Adım Railway Deployment

### 1. GitHub Repository Hazırlığı

✅ Repository: https://github.com/gulsahsudenaz-cpu/al

### 2. Railway'de Proje Oluşturma

1. **Railway'a Giriş Yap**
   - https://railway.app adresine git
   - GitHub hesabınla giriş yap

2. **Yeni Proje Oluştur**
   - "New Project" butonuna tıkla
   - "Deploy from GitHub repo" seçeneğini seç
   - Repository'yi seç: `gulsahsudenaz-cpu/al`
   - Branch: `main`

### 3. Servisleri Ekle

#### 3.1 PostgreSQL Servisi

1. "New" → "Database" → "PostgreSQL"
2. Railway otomatik olarak:
   - PostgreSQL instance oluşturur
   - `POSTGRES_URL` environment variable'ı ekler
   - pgvector extension'ı destekler

#### 3.2 Redis Servisi

1. "New" → "Database" → "Redis"
2. Railway otomatik olarak:
   - Redis instance oluşturur
   - `REDISCLOUD_URL` environment variable'ı ekler

#### 3.3 Backend Servisi

1. "New" → "GitHub Repo"
2. Repository: `gulsahsudenaz-cpu/al`
3. Root Directory: `/` (root)
4. Build Command: Railway otomatik algılayacak (nixpacks)
5. Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Environment Variables Ayarlama

Backend servisine aşağıdaki environment variable'ları ekle:

```env
# Application
DEBUG=False
SECRET_KEY=your-production-secret-key-minimum-32-characters-long
API_V1_PREFIX=/v1

# Database (Railway otomatik ekler)
DATABASE_URL=${{Postgres.DATABASE_URL}}
POSTGRES_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway otomatik ekler)
REDIS_URL=${{Redis.REDISCLOUD_URL}}
REDISCLOUD_URL=${{Redis.REDISCLOUD_URL}}

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here
MODEL=gpt-4-turbo
OPENAI_BASE_URL=

# LLM Settings
LLM_DAILY_COST_LIMIT=50.0
LLM_MAX_TOKENS_PER_REQUEST=512
LLM_CACHE_TTL=86400

# RAG Settings
RAG_MIN_SIMILARITY=0.7
RAG_MAX_DOCUMENTS=5
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_HYBRID_WEIGHTS={"semantic": 0.7, "keyword": 0.3}

# Security
JWT_SECRET_KEY=${{SECRET_KEY}}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
OTP_LENGTH=6
OTP_TTL=300

# Rate Limiting
MAX_MESSAGES_PER_MINUTE=30
MAX_SESSIONS_PER_USER=3
MAX_MEDIA_SIZE_MB=15

# CORS (Production domain'inizi ekleyin)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring
ENABLE_METRICS=True
OTEL_EXPORTER_OTLP_ENDPOINT=

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-railway-domain.railway.app/v1/telegram/webhook

# Media Storage (Optional - S3/MinIO)
S3_ENDPOINT_URL=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET_NAME=
USE_MINIO=False

# Port (Railway otomatik ayarlar)
PORT=${{PORT}}
```

### 5. Build ve Deploy Ayarları

Railway otomatik olarak:
- `nixpacks.toml` dosyasını kullanarak build yapar
- `railway.json` dosyasındaki ayarları uygular
- Health check'i `/health` endpoint'inde yapar
- Migration'ları çalıştırır (`alembic upgrade head`)

### 6. Migration'ları Çalıştırma

Migration'lar otomatik çalışacak, ancak manuel olarak da çalıştırabilirsiniz:

1. Backend servisinde "Settings" → "Service Settings"
2. "Deploy" sekmesinde "Run Command" kullan:
   ```bash
   cd backend && alembic upgrade head
   ```

### 7. Admin Kullanıcısı Oluşturma

Railway console'dan veya local'den:

```bash
# Railway console'dan
railway run python scripts/create_admin.py

# Veya local'den (Railway CLI ile)
railway connect
railway run python scripts/create_admin.py
```

### 8. Domain Ayarlama

1. Backend servisinde "Settings" → "Networking"
2. "Generate Domain" ile Railway domain'i oluştur
3. Veya "Custom Domain" ile kendi domain'inizi ekleyin
4. Railway otomatik SSL sertifikası sağlar

### 9. Worker Servisi (Opsiyonel)

Background worker için:

1. "New" → "GitHub Repo"
2. Aynı repository'yi seç
3. Root Directory: `/`
4. Start Command: `cd backend && rq worker --url $REDISCLOUD_URL`
5. Environment variables'ı backend ile aynı yap

### 10. Health Check

Deployment sonrası kontrol:

```bash
# Health check
curl https://your-railway-domain.railway.app/health

# API docs
https://your-railway-domain.railway.app/docs
```

### 11. Monitoring

- **Metrics**: https://your-railway-domain.railway.app/metrics
- **Health**: https://your-railway-domain.railway.app/health
- **Railway Dashboard**: Railway dashboard'undan logs ve metrics'i görüntüleyin

## 🔧 Troubleshooting

### Database Connection Error

- `DATABASE_URL` environment variable'ının doğru olduğundan emin olun
- PostgreSQL servisinin çalıştığından emin olun
- Migration'ların çalıştığından emin olun

### Redis Connection Error

- `REDIS_URL` veya `REDISCLOUD_URL` environment variable'ının doğru olduğundan emin olun
- Redis servisinin çalıştığından emin olun

### Build Error

- `requirements.txt` dosyasının doğru olduğundan emin olun
- Python version'ının 3.11+ olduğundan emin olun
- Build logs'u kontrol edin

### Migration Error

- Database bağlantısının çalıştığından emin olun
- `alembic.ini` dosyasının doğru yapılandırıldığından emin olun
- Migration dosyalarının doğru olduğundan emin olun

### Port Error

- `PORT` environment variable'ının Railway tarafından otomatik ayarlandığından emin olun
- `$PORT` variable'ını kullandığınızdan emin olun

## 📊 Railway CLI Kullanımı

### Railway CLI Kurulumu

```bash
npm i -g @railway/cli
```

### Railway'a Bağlanma

```bash
railway login
railway link
```

### Logs Görüntüleme

```bash
railway logs
```

### Environment Variables

```bash
# List
railway variables

# Add
railway variables set KEY=value

# Get
railway variables get KEY
```

### Deployment

```bash
# Deploy
railway up

# Run command
railway run python scripts/create_admin.py
```

## 🎯 Success Checklist

- [ ] PostgreSQL servisi çalışıyor
- [ ] Redis servisi çalışıyor
- [ ] Backend servisi deployed
- [ ] Environment variables ayarlandı
- [ ] Migration'lar çalıştı
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Health check başarılı
- [ ] Domain ayarlandı
- [ ] SSL sertifikası aktif
- [ ] API docs erişilebilir
- [ ] Admin panel çalışıyor

## 🔗 Useful Links

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

---

**Happy Deploying! 🚀**

