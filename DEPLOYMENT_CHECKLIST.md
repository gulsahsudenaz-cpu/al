# ✅ Railway Deployment Checklist

## 🚀 GitHub'a Yükleme (Tamamlandı)

- [x] Git repository hazırlandı
- [x] Tüm dosyalar commit edildi
- [x] GitHub'a push yapıldı
- [x] Repository: https://github.com/gulsahsudenaz-cpu/al

## 🚂 Railway Deployment Adımları

### 1. Railway'a Giriş
- [ ] https://railway.app adresine git
- [ ] GitHub hesabınla giriş yap
- [ ] "New Project" butonuna tıkla

### 2. Repository'yi Bağla
- [ ] "Deploy from GitHub repo" seç
- [ ] Repository: `gulsahsudenaz-cpu/al`
- [ ] Branch: `main`
- [ ] "Deploy" butonuna tıkla

### 3. Servisleri Ekle

#### PostgreSQL
- [ ] "New" → "Database" → "PostgreSQL"
- [ ] Servis adı: `postgres` (veya otomatik)
- [ ] `POSTGRES_URL` environment variable'ı otomatik eklenecek

#### Redis
- [ ] "New" → "Database" → "Redis"
- [ ] Servis adı: `redis` (veya otomatik)
- [ ] `REDISCLOUD_URL` environment variable'ı otomatik eklenecek

#### Backend
- [ ] Backend servisi otomatik oluşturulacak
- [ ] Root directory: `/` (root)
- [ ] Build command: Otomatik (nixpacks)
- [ ] Start command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. Environment Variables

Backend servisine aşağıdaki environment variable'ları ekle:

#### Zorunlu
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=your-production-secret-key-minimum-32-characters`
- [ ] `DATABASE_URL=${{Postgres.DATABASE_URL}}`
- [ ] `POSTGRES_URL=${{Postgres.DATABASE_URL}}`
- [ ] `REDIS_URL=${{Redis.REDISCLOUD_URL}}`
- [ ] `REDISCLOUD_URL=${{Redis.REDISCLOUD_URL}}`
- [ ] `OPENAI_API_KEY=sk-your-openai-api-key`
- [ ] `MODEL=gpt-4-turbo`

#### Opsiyonel
- [ ] `LLM_DAILY_COST_LIMIT=50.0`
- [ ] `RAG_MIN_SIMILARITY=0.7`
- [ ] `JWT_SECRET_KEY=${{SECRET_KEY}}`
- [ ] `CORS_ORIGINS=https://your-app.railway.app`
- [ ] `ENABLE_METRICS=True`
- [ ] `TELEGRAM_BOT_TOKEN=your-telegram-bot-token` (opsiyonel)
- [ ] `TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/v1/telegram/webhook` (opsiyonel)

### 5. Build ve Deploy
- [ ] Build başarılı
- [ ] Migration'lar çalıştı (`alembic upgrade head`)
- [ ] Backend başlatıldı
- [ ] Health check başarılı (`/health`)

### 6. Migration'ları Kontrol Et
- [ ] Migration'lar otomatik çalıştı
- [ ] Hata yoksa devam et
- [ ] Hata varsa logs'u kontrol et

### 7. Admin Kullanıcısı Oluştur
- [ ] Railway console'dan: `python scripts/create_admin.py`
- [ ] Veya Railway dashboard'dan "Run Command"
- [ ] Admin kullanıcısı oluşturuldu
- [ ] Varsayılan bilgiler:
  - Username: `admin`
  - Password: `admin123`

### 8. Domain Ayarla
- [ ] Backend servisi → "Settings" → "Networking"
- [ ] "Generate Domain" ile Railway domain'i oluştur
- [ ] Veya "Custom Domain" ile kendi domain'inizi ekleyin
- [ ] SSL sertifikası otomatik sağlanacak

### 9. Test Et
- [ ] Health check: `https://your-app.railway.app/health`
- [ ] API docs: `https://your-app.railway.app/docs`
- [ ] Admin panel: `https://your-app.railway.app/admin/login.html`
- [ ] Login test: Username `admin`, Password `admin123`

### 10. Worker Servisi (Opsiyonel)
- [ ] "New" → "GitHub Repo"
- [ ] Aynı repository'yi seç
- [ ] Start command: `cd backend && python -m rq worker --url $REDISCLOUD_URL`
- [ ] Environment variables'ı backend ile aynı yap

## 🔧 Troubleshooting

### Build Hatası
- [ ] `requirements.txt` doğru mu?
- [ ] Build logs'u kontrol et
- [ ] Python version 3.11+ mı?

### Database Hatası
- [ ] `DATABASE_URL` doğru mu?
- [ ] PostgreSQL servisi çalışıyor mu?
- [ ] Migration'lar çalıştı mı?

### Redis Hatası
- [ ] `REDIS_URL` veya `REDISCLOUD_URL` doğru mu?
- [ ] Redis servisi çalışıyor mu?

### Port Hatası
- [ ] `PORT` environment variable'ı var mı?
- [ ] Backend `$PORT` kullanıyor mu?

## ✅ Deployment Sonrası

- [ ] Health check çalışıyor
- [ ] API docs erişilebilir
- [ ] Admin panel çalışıyor
- [ ] Login başarılı
- [ ] Database bağlantısı çalışıyor
- [ ] Redis bağlantısı çalışıyor
- [ ] RAG sistemi çalışıyor
- [ ] LLM entegrasyonu çalışıyor

## 📊 Monitoring

- [ ] Metrics: `https://your-app.railway.app/metrics`
- [ ] Health: `https://your-app.railway.app/health`
- [ ] Logs: Railway dashboard → Backend servisi → Logs
- [ ] Metrics: Railway dashboard → Backend servisi → Metrics

## 🔐 Güvenlik

- [ ] `SECRET_KEY` değiştirildi
- [ ] `DEBUG=False` production'da
- [ ] `CORS_ORIGINS` doğru domain'lerle ayarlandı
- [ ] Admin şifresi değiştirildi (production'da)
- [ ] `.env` dosyası GitHub'a push edilmedi

## 🎯 Sonraki Adımlar

- [ ] Custom domain ayarla (opsiyonel)
- [ ] SSL sertifikası kontrol et
- [ ] Monitoring kurulumu (opsiyonel)
- [ ] Backup stratejisi (opsiyonel)
- [ ] Auto-scaling ayarları (opsiyonel)

---

**Deployment tamamlandığında tüm checkbox'ları işaretleyin! ✅**

