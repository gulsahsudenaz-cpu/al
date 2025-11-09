# Aşama Aşama Kurulum Rehberi

Bu rehber, projeyi aşama aşama kurmanız ve deploy etmeniz için adım adım talimatlar içerir.

## Aşama 1: Git Repository Hazırlığı ✅

### 1.1 Git Repository Oluşturma

```bash
# Mevcut dizinde Git'i başlat
git init

# .gitignore kontrolü (zaten oluşturuldu)
# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: AI Chatbot System v2.0"

# GitHub'da yeni repository oluşturduktan sonra
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
git branch -M main
git push -u origin main
```

### 1.2 GitHub Repository Ayarları

1. GitHub'da yeni repository oluşturun
2. Repository adı: `chatbot` (veya istediğiniz ad)
3. Public veya Private seçin
4. README, .gitignore, license eklemeyin (zaten var)

### 1.3 GitHub Secrets Ayarlama

1. Repository Settings → Secrets and variables → Actions
2. "New repository secret" butonuna tıklayın
3. Şu secrets'ları ekleyin:
   - `OPENAI_API_KEY`: OpenAI API anahtarınız
   - `SECRET_KEY`: Güvenli bir secret key (production için)
   - `JWT_SECRET_KEY`: JWT için secret key

## Aşama 2: Lokal Geliştirme Ortamı 🛠️

### 2.1 Python Virtual Environment

```bash
# Backend dizinine git
cd backend

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı aktifleştir
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Dependencies yükle
pip install -r requirements.txt
pip install -r requirements/dev.txt
```

### 2.2 Environment Variables

```bash
# Root dizinde .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle
# Önemli değişkenler:
# - OPENAI_API_KEY
# - SECRET_KEY
# - JWT_SECRET_KEY
# - DATABASE_URL
# - REDIS_URL
```

### 2.3 Docker Servisleri

```bash
# Docker Compose ile servisleri başlat
cd infra
docker-compose up -d postgres redis

# Servislerin çalıştığını kontrol et
docker-compose ps
```

### 2.4 Database Migrations

```bash
# Backend dizinine git
cd ../backend

# Migrations çalıştır
alembic upgrade head

# Migration başarılı mı kontrol et
# PostgreSQL'e bağlan ve tabloları kontrol et
```

### 2.5 Backend Başlatma

```bash
# Backend'i development mode'da başlat
uvicorn app.main:app --reload --port 8000

# Tarayıcıda kontrol et
# http://localhost:8000/health
# http://localhost:8000/docs
```

## Aşama 3: Testler ve Doğrulama 🧪

### 3.1 Unit Tests

```bash
# Backend dizininde
cd backend

# Testleri çalıştır
pytest tests/ -v

# Coverage ile çalıştır
pytest tests/ -v --cov=app --cov-report=html

# Coverage raporunu aç
# htmlcov/index.html
```

### 3.2 E2E Tests

```bash
# Root dizinde
npm install

# Playwright kurulumu
npx playwright install

# E2E testleri çalıştır
npx playwright test

# UI mode'da çalıştır
npx playwright test --ui
```

### 3.3 API Testleri

```bash
# Health check
curl http://localhost:8000/health

# API docs
# http://localhost:8000/docs adresini tarayıcıda aç

# WebSocket test (browser console)
const ws = new WebSocket('ws://localhost:8000/v1/ws/chat?room_key=test');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.send(JSON.stringify({ type: 'client.message', text: 'Hello' }));
```

## Aşama 4: Railway Deployment 🚀

### 4.1 Railway Hesabı ve Proje

1. [Railway.app](https://railway.app) hesabı oluşturun
2. "New Project" butonuna tıklayın
3. "Deploy from GitHub repo" seçin
4. Repository'nizi seçin
5. "Deploy" butonuna tıklayın

### 4.2 PostgreSQL Plugin

1. Railway dashboard'da "+ New" butonuna tıklayın
2. "Database" → "Add PostgreSQL" seçin
3. PostgreSQL servisi oluşturulacak
4. **ÖNEMLİ**: PostgreSQL'de pgvector extension'ını aktifleştirin:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 4.3 Redis Plugin

1. "+ New" butonuna tıklayın
2. "Database" → "Add Redis" seçin
3. Redis servisi oluşturulacak

### 4.4 Environment Variables

Railway dashboard'da "Variables" sekmesine gidin ve ekleyin:

```env
# ZORUNLU
OPENAI_API_KEY=sk-your-openai-api-key
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key

# OPSIYONEL
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0
DEBUG=False
RAG_MIN_SIMILARITY=0.7
ENABLE_METRICS=True

# Telegram (Opsiyonel)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/v1/telegram/webhook

# CORS
CORS_ORIGINS=https://your-frontend-domain.com
```

**Not**: `DATABASE_URL` ve `REDIS_URL` Railway tarafından otomatik sağlanır.

### 4.5 Deploy ve Kontrol

1. Railway otomatik olarak deploy edecek
2. Deploy loglarını kontrol edin
3. Health check: `https://your-app.railway.app/health`
4. API docs: `https://your-app.railway.app/docs`

### 4.6 Custom Domain (Opsiyonel)

1. Railway dashboard'da "Settings" → "Networking"
2. "Generate Domain" veya kendi domain'inizi ekleyin
3. SSL otomatik olarak sağlanır

## Aşama 5: Monitoring Kurulumu 📊

### 5.1 Lokal Monitoring

```bash
# Monitoring servislerini başlat
cd infra
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Servisleri kontrol et
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Metrics: http://localhost:8000/metrics
```

### 5.2 Grafana Dashboard

1. Grafana'ya giriş yapın (http://localhost:3000)
2. Default credentials: admin/admin
3. Data source olarak Prometheus'u ekleyin
4. Dashboard'ları import edin (opsiyonel)

### 5.3 Railway'de Monitoring

Railway'de monitoring için:
1. Railway Metrics kullanın (built-in)
2. Veya external monitoring service kullanın (DataDog, New Relic, etc.)

## Aşama 6: Production Optimizasyonu 🎯

### 6.1 Performance Tuning

```bash
# Database connection pool ayarları
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis connection pool
REDIS_MAX_CONNECTIONS=100

# Worker processes
WORKERS=4
```

### 6.2 Security Hardening

1. `SECRET_KEY` ve `JWT_SECRET_KEY` güvenli olmalı
2. CORS origins doğru ayarlanmalı
3. Rate limiting aktif olmalı
4. PII redaction aktif olmalı

### 6.3 Backup Strategy

1. Database backup: Railway otomatik backup sağlar
2. Manual backup: `pg_dump` ile backup alın
3. Backup schedule ayarlayın

## Aşama 7: Frontend Deployment 🌐

### 7.1 Widget Deployment

Widget'ı static hosting'e deploy edin:
- Netlify
- Vercel
- GitHub Pages
- Railway (static files)

### 7.2 Admin Panel Deployment

Admin paneli deploy edin:
- Netlify
- Vercel
- Railway
- Kendi domain'inizde

### 7.3 CORS Ayarları

Frontend domain'lerini CORS'a ekleyin:
```env
CORS_ORIGINS=https://your-widget-domain.com,https://your-admin-domain.com
```

## Aşama 8: Worker Service 👷

### 8.1 Worker Deployment

Railway'de worker service oluşturun:
1. "+ New" → "Empty Service"
2. GitHub repository'yi bağlayın
3. Start Command: `cd backend && python -m app.workers.indexer`
4. Environment variables'ları ayarlayın

### 8.2 Worker Monitoring

Worker'ı monitor edin:
- Railway logs
- Prometheus metrics
- Error tracking

## Aşama 9: Testing ve Validation ✅

### 9.1 Smoke Tests

```bash
# Health check
curl https://your-app.railway.app/health

# API test
curl https://your-app.railway.app/v1/chat/chats

# Metrics test
curl https://your-app.railway.app/metrics
```

### 9.2 Load Testing

```bash
# Load test tool kullan (örn: k6, locust)
# veya Railway metrics'i kullan
```

### 9.3 End-to-End Testing

```bash
# E2E testleri production URL ile çalıştır
BASE_URL=https://your-app.railway.app npx playwright test
```

## Aşama 10: Documentation ve Runbook 📚

### 10.1 API Documentation

- Swagger UI: `https://your-app.railway.app/docs`
- ReDoc: `https://your-app.railway.app/redoc`

### 10.2 Runbook

Runbook oluşturun:
- Troubleshooting guide
- Common issues
- Emergency procedures
- Contact information

## Sorun Giderme 🔧

### Database Connection Error

```bash
# Database URL'i kontrol et
railway variables

# Connection test et
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

### Redis Connection Error

```bash
# Redis URL'i kontrol et
railway variables

# Connection test et
railway run redis-cli -u $REDIS_URL ping
```

### Migrations Failed

```bash
# Manuel olarak çalıştır
railway run cd backend && alembic upgrade head
```

### Worker Not Working

```bash
# Worker logs'u kontrol et
railway logs worker

# Worker'ı manuel başlat
railway run cd backend && python -m app.workers.indexer
```

## Checklist ✅

### Lokal Geliştirme
- [ ] Git repository oluşturuldu
- [ ] Virtual environment kuruldu
- [ ] Dependencies yüklendi
- [ ] Environment variables ayarlandı
- [ ] Docker servisleri çalışıyor
- [ ] Database migrations çalıştırıldı
- [ ] Backend başarıyla başlatıldı
- [ ] Tests başarıyla çalıştı

### Railway Deployment
- [ ] Railway hesabı oluşturuldu
- [ ] GitHub repository bağlandı
- [ ] PostgreSQL plugin eklendi
- [ ] Redis plugin eklendi
- [ ] Environment variables ayarlandı
- [ ] Deploy başarılı
- [ ] Health check çalışıyor
- [ ] Custom domain ayarlandı (opsiyonel)

### Monitoring
- [ ] Monitoring servisleri kuruldu
- [ ] Prometheus çalışıyor
- [ ] Grafana çalışıyor
- [ ] Metrics endpoint çalışıyor
- [ ] Dashboard'lar yapılandırıldı

### Production
- [ ] Security hardening yapıldı
- [ ] Performance tuning yapıldı
- [ ] Backup strategy oluşturuldu
- [ ] Frontend deploy edildi
- [ ] Worker service deploy edildi
- [ ] Testing tamamlandı
- [ ] Documentation tamamlandı

## Sonraki Adımlar 🚀

1. **Monitoring Dashboard**: Grafana dashboard'ları oluşturun
2. **Alerting**: Alert rules yapılandırın
3. **Scaling**: Auto-scaling ayarlayın
4. **CI/CD**: GitHub Actions workflow'ları optimize edin
5. **Documentation**: API documentation'ı genişletin
6. **Testing**: Test coverage'ı artırın
7. **Performance**: Performance optimization yapın
8. **Security**: Security audit yapın

## Destek 📞

Sorularınız için:
- GitHub Issues
- Documentation
- Railway Support
- Community Forum

