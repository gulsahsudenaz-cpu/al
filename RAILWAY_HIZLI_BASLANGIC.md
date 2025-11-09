# 🚂 Railway Deployment - Hızlı Başlangıç

## ✅ GitHub'a Yüklendi!

Repository: https://github.com/gulsahsudenaz-cpu/al

## 🚀 Railway'de Deploy Etme (5 Dakika)

### 1. Railway'a Giriş

1. https://railway.app adresine git
2. "Start a New Project" butonuna tıkla
3. GitHub hesabınla giriş yap (eğer yoksa)

### 2. Repository'yi Bağla

1. "Deploy from GitHub repo" seçeneğini seç
2. Repository'yi seç: `gulsahsudenaz-cpu/al`
3. Branch: `main`
4. "Deploy" butonuna tıkla

### 3. Servisleri Ekle

#### 3.1 PostgreSQL (Database)

1. "New" butonuna tıkla
2. "Database" → "PostgreSQL" seç
3. Railway otomatik olarak:
   - PostgreSQL instance oluşturur
   - `POSTGRES_URL` environment variable'ı ekler
   - pgvector extension'ı destekler

#### 3.2 Redis (Cache)

1. "New" butonuna tıkla
2. "Database" → "Redis" seç
3. Railway otomatik olarak:
   - Redis instance oluşturur
   - `REDISCLOUD_URL` environment variable'ı ekler

### 4. Environment Variables Ayarla

Backend servisine tıkla → "Variables" sekmesi → Aşağıdaki değişkenleri ekle:

#### Zorunlu Değişkenler

```env
# Application
DEBUG=False
SECRET_KEY=your-super-secret-key-minimum-32-characters-change-this

# Database (Railway otomatik ekler, kontrol et)
DATABASE_URL=${{Postgres.DATABASE_URL}}
POSTGRES_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway otomatik ekler, kontrol et)
REDIS_URL=${{Redis.REDISCLOUD_URL}}
REDISCLOUD_URL=${{Redis.REDISCLOUD_URL}}

# OpenAI (ZORUNLU)
OPENAI_API_KEY=sk-your-openai-api-key-here
MODEL=gpt-4-turbo
```

#### Opsiyonel Değişkenler

```env
# LLM Settings
LLM_DAILY_COST_LIMIT=50.0
LLM_MAX_TOKENS_PER_REQUEST=512
LLM_CACHE_TTL=86400

# RAG Settings
RAG_MIN_SIMILARITY=0.7
RAG_MAX_DOCUMENTS=5
RAG_EMBEDDING_MODEL=text-embedding-3-small

# Security
JWT_SECRET_KEY=${{SECRET_KEY}}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Railway domain'inizi ekleyin)
CORS_ORIGINS=https://your-app.railway.app

# Monitoring
ENABLE_METRICS=True

# Telegram (Opsiyonel)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/v1/telegram/webhook
```

### 5. Build ve Deploy

Railway otomatik olarak:
- ✅ Repository'den kodu çeker
- ✅ `nixpacks.toml` ile build yapar
- ✅ `requirements.txt`'den bağımlılıkları yükler
- ✅ Migration'ları çalıştırır (`alembic upgrade head`)
- ✅ Backend'i başlatır
- ✅ Health check yapar (`/health`)

### 6. Migration'ları Çalıştır

1. Backend servisine tıkla
2. "Deployments" sekmesi → En son deployment'a tıkla
3. "View Logs" ile logları kontrol et
4. Migration'lar otomatik çalışacak, ancak hata olursa:

```bash
# Railway CLI ile (opsiyonel)
railway run cd backend && alembic upgrade head
```

### 7. Admin Kullanıcısı Oluştur

Railway console'dan:

```bash
# Railway CLI kurulumu (opsiyonel)
npm i -g @railway/cli

# Railway'a bağlan
railway login
railway link

# Admin kullanıcısı oluştur
railway run python scripts/create_admin.py
```

Veya Railway dashboard'dan:

1. Backend servisine tıkla
2. "Settings" → "Service Settings"
3. "Deploy" sekmesi → "Run Command"
4. Komut: `python scripts/create_admin.py`

### 8. Domain Ayarla

1. Backend servisine tıkla
2. "Settings" → "Networking"
3. "Generate Domain" ile Railway domain'i oluştur
   - Örnek: `your-app.railway.app`
4. Veya "Custom Domain" ile kendi domain'inizi ekleyin
5. Railway otomatik SSL sertifikası sağlar

### 9. Test Et

1. Health check:
   ```
   https://your-app.railway.app/health
   ```

2. API docs:
   ```
   https://your-app.railway.app/docs
   ```

3. Admin panel:
   ```
   https://your-app.railway.app/admin/login.html
   ```
   - Username: `admin`
   - Password: `admin123`

### 10. Worker Servisi (Opsiyonel)

Background worker için:

1. "New" → "GitHub Repo"
2. Aynı repository'yi seç: `gulsahsudenaz-cpu/al`
3. "Settings" → "Service Settings"
4. "Deploy" sekmesi → "Start Command":
   ```
   cd backend && rq worker --url $REDISCLOUD_URL
   ```
5. Environment variables'ı backend ile aynı yap

## 🔧 Troubleshooting

### Build Hatası

- `requirements.txt` dosyasının doğru olduğundan emin olun
- Build logs'u kontrol edin
- Python version'ının 3.11+ olduğundan emin olun

### Database Hatası

- `DATABASE_URL` environment variable'ının doğru olduğundan emin olun
- PostgreSQL servisinin çalıştığından emin olun
- Migration'ların çalıştığından emin olun

### Redis Hatası

- `REDIS_URL` veya `REDISCLOUD_URL` environment variable'ının doğru olduğundan emin olun
- Redis servisinin çalıştığından emin olun

### Port Hatası

- `PORT` environment variable'ının Railway tarafından otomatik ayarlandığından emin olun
- Backend'in `$PORT` variable'ını kullandığından emin olun

## ✅ Deployment Checklist

- [ ] GitHub repository bağlandı
- [ ] PostgreSQL servisi eklendi
- [ ] Redis servisi eklendi
- [ ] Environment variables ayarlandı
- [ ] Build başarılı
- [ ] Migration'lar çalıştı
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Health check başarılı
- [ ] Domain ayarlandı
- [ ] SSL sertifikası aktif
- [ ] API docs erişilebilir
- [ ] Admin panel çalışıyor

## 📊 Monitoring

- **Metrics**: https://your-app.railway.app/metrics
- **Health**: https://your-app.railway.app/health
- **Logs**: Railway dashboard → Backend servisi → Logs
- **Metrics**: Railway dashboard → Backend servisi → Metrics

## 🔗 Useful Links

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Documentation](https://docs.railway.app)
- [GitHub Repository](https://github.com/gulsahsudenaz-cpu/al)

## 🎯 Sonraki Adımlar

1. ✅ Railway'de deploy et
2. ✅ Environment variables ayarla
3. ✅ Admin kullanıcısı oluştur
4. ✅ Domain ayarla
5. ✅ Test et
6. ✅ Production'a geç!

---

**Başarılar! 🚀**

