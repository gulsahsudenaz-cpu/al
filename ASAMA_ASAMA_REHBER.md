# 🚀 Aşama Aşama Kurulum Rehberi

Bu rehber, projeyi sıfırdan kurmanız ve deploy etmeniz için adım adım talimatlar içerir.

## 📋 Genel Bakış

1. ✅ **Aşama 1**: Git Repository Hazırlığı
2. 🔄 **Aşama 2**: Lokal Geliştirme Ortamı
3. 🔄 **Aşama 3**: Docker Servisleri
4. 🔄 **Aşama 4**: Database Migrations
5. 🔄 **Aşama 5**: Testler
6. 🔄 **Aşama 6**: Railway Deployment
7. 🔄 **Aşama 7**: Monitoring Kurulumu
8. 🔄 **Aşama 8**: Production Optimizasyonu

---

## ✅ Aşama 1: Git Repository Hazırlığı (TAMAMLANDI)

Git repository oluşturuldu ve ilk commit yapıldı.

### Sonraki Adımlar:

1. **GitHub'da Repository Oluşturun**:
   - GitHub'a gidin: https://github.com
   - "New repository" butonuna tıklayın
   - Repository adı: `chatbot` (veya istediğiniz ad)
   - Public veya Private seçin
   - README, .gitignore, license **EKLEMEYIN** (zaten var)

2. **GitHub'a Push Edin**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
   git branch -M main
   git push -u origin main
   ```

3. **GitHub Secrets Ayarlayın**:
   - Repository Settings → Secrets and variables → Actions
   - "New repository secret" butonuna tıklayın
   - Şu secrets'ları ekleyin:
     - `OPENAI_API_KEY`: OpenAI API anahtarınız
     - `SECRET_KEY`: Güvenli bir secret key
     - `JWT_SECRET_KEY`: JWT için secret key

---

## 🔄 Aşama 2: Lokal Geliştirme Ortamı

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
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements/dev.txt
```

**Veya otomatik script ile:**
```bash
# Windows PowerShell:
.\scripts\setup_step2_local.sh

# Linux/Mac:
bash scripts/setup_step2_local.sh
```

### 2.2 Environment Variables

```bash
# Root dizinde .env dosyası oluştur
cp .env.example .env

# .env dosyasını düzenle
# Önemli değişkenler:
# - OPENAI_API_KEY=sk-your-key-here
# - SECRET_KEY=your-secret-key-here
# - JWT_SECRET_KEY=your-jwt-secret-key-here
# - DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
# - REDIS_URL=redis://localhost:6379/0
```

### 2.3 Kontrol

```bash
# Python version kontrolü
python --version  # Python 3.11+ olmalı

# Virtual environment aktif mi?
which python  # venv/bin/python veya venv\Scripts\python görmeli

# Dependencies yüklendi mi?
pip list | grep fastapi  # fastapi görünmeli
```

---

## 🔄 Aşama 3: Docker Servisleri

### 3.1 Docker Kontrolü

```bash
# Docker kurulu mu?
docker --version
docker-compose --version
```

### 3.2 Docker Servislerini Başlat

```bash
# Infra dizinine git
cd infra

# .env dosyasının root'ta olduğundan emin ol
# Docker servislerini başlat
docker-compose up -d postgres redis

# Servislerin çalışmasını bekle (10 saniye)
sleep 10

# Servisleri kontrol et
docker-compose ps
```

**Veya otomatik script ile:**
```bash
bash scripts/setup_step3_docker.sh
```

### 3.3 Servis Kontrolü

```bash
# PostgreSQL bağlantı testi
docker-compose exec postgres pg_isready -U user

# Redis bağlantı testi
docker-compose exec redis redis-cli ping

# pgvector extension
docker-compose exec postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## 🔄 Aşama 4: Database Migrations

### 4.1 Migrations Çalıştır

```bash
# Backend dizinine git
cd backend

# Virtual environment aktif mi kontrol et
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Environment variables yükle
# .env dosyası root'ta olmalı
export $(cat ../.env | grep -v '^#' | xargs)

# Migrations çalıştır
alembic upgrade head
```

**Veya otomatik script ile:**
```bash
bash scripts/setup_step4_migrations.sh
```

### 4.2 Kontrol

```bash
# Tablolar oluşturuldu mu?
docker-compose exec postgres psql -U user -d chatbot -c "\dt"
```

---

## 🔄 Aşama 5: Backend Başlatma ve Test

### 5.1 Backend Başlat

```bash
# Backend dizininde
cd backend

# Virtual environment aktif
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Backend'i başlat
uvicorn app.main:app --reload --port 8000
```

### 5.2 Kontrol

```bash
# Health check
curl http://localhost:8000/health

# API docs
# Tarayıcıda aç: http://localhost:8000/docs
```

### 5.3 Testler

```bash
# Unit tests
cd backend
pytest tests/ -v

# Coverage ile
pytest tests/ -v --cov=app --cov-report=html

# E2E tests (backend çalışıyor olmalı)
cd ..
npm install
npx playwright install
npx playwright test
```

**Veya otomatik script ile:**
```bash
bash scripts/setup_step5_tests.sh
```

---

## 🔄 Aşama 6: Railway Deployment

### 6.1 Railway Hesabı

1. [Railway.app](https://railway.app) hesabı oluşturun
2. GitHub ile login yapın

### 6.2 Proje Oluşturma

1. "New Project" butonuna tıklayın
2. "Deploy from GitHub repo" seçin
3. Repository'nizi seçin
4. "Deploy" butonuna tıklayın

### 6.3 PostgreSQL Plugin

1. "+ New" butonuna tıklayın
2. "Database" → "Add PostgreSQL" seçin
3. PostgreSQL servisi oluşturulacak
4. **ÖNEMLİ**: PostgreSQL'de pgvector extension'ını aktifleştirin:
   - Railway dashboard'da PostgreSQL servisine tıklayın
   - "Query" sekmesine gidin
   - Şu SQL'i çalıştırın:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

### 6.4 Redis Plugin

1. "+ New" butonuna tıklayın
2. "Database" → "Add Redis" seçin
3. Redis servisi oluşturulacak

### 6.5 Environment Variables

Railway dashboard'da "Variables" sekmesine gidin:

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
```

**Not**: `DATABASE_URL` ve `REDIS_URL` Railway tarafından otomatik sağlanır.

### 6.6 Deploy ve Kontrol

1. Railway otomatik olarak deploy edecek
2. Deploy loglarını kontrol edin
3. Health check: `https://your-app.railway.app/health`
4. API docs: `https://your-app.railway.app/docs`

Detaylı rehber: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔄 Aşama 7: Monitoring Kurulumu

### 7.1 Lokal Monitoring

```bash
# Monitoring servislerini başlat
cd infra
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Servisleri kontrol et
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Metrics: http://localhost:8000/metrics
```

### 7.2 Grafana Dashboard

1. Grafana'ya giriş yapın (http://localhost:3000)
2. Default credentials: admin/admin
3. Data source olarak Prometheus'u ekleyin
4. Dashboard'ları import edin (opsiyonel)

---

## 🔄 Aşama 8: Production Optimizasyonu

### 8.1 Performance Tuning

```env
# Database connection pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis connection pool
REDIS_MAX_CONNECTIONS=100

# Worker processes
WORKERS=4
```

### 8.2 Security Hardening

1. `SECRET_KEY` ve `JWT_SECRET_KEY` güvenli olmalı
2. CORS origins doğru ayarlanmalı
3. Rate limiting aktif olmalı
4. PII redaction aktif olmalı

### 8.3 Backup Strategy

1. Database backup: Railway otomatik backup sağlar
2. Manual backup: `pg_dump` ile backup alın
3. Backup schedule ayarlayın

---

## 📊 İlerleme Takibi

### Tamamlanan ✅
- [x] Aşama 1: Git Repository Hazırlığı
- [ ] Aşama 2: Lokal Geliştirme Ortamı
- [ ] Aşama 3: Docker Servisleri
- [ ] Aşama 4: Database Migrations
- [ ] Aşama 5: Testler
- [ ] Aşama 6: Railway Deployment
- [ ] Aşama 7: Monitoring Kurulumu
- [ ] Aşama 8: Production Optimizasyonu

---

## 🆘 Sorun Giderme

### Python Virtual Environment Hatası
```bash
# Virtual environment'ı yeniden oluştur
rm -rf backend/venv
cd backend
python -m venv venv
source venv/bin/activate  # veya venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### Docker Servisleri Çalışmıyor
```bash
# Docker servislerini yeniden başlat
cd infra
docker-compose down
docker-compose up -d postgres redis
```

### Database Migration Hatası
```bash
# Migration'ları sıfırla ve yeniden çalıştır
cd backend
alembic downgrade base
alembic upgrade head
```

### Railway Deployment Hatası
- Railway loglarını kontrol edin
- Environment variables'ları kontrol edin
- Database URL'i kontrol edin
- Redis URL'i kontrol edin

---

## 📚 İlgili Dokümantasyon

- [README.md](README.md) - Genel proje dokümantasyonu
- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç rehberi
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment rehberi
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detaylı kurulum rehberi
- [kurulum.md](kurulum.md) - Teknik kurulum detayları

---

## 🎯 Sonraki Adımlar

1. **Aşama 2'yi tamamlayın**: Lokal geliştirme ortamını kurun
2. **Aşama 3'ü tamamlayın**: Docker servislerini başlatın
3. **Aşama 4'ü tamamlayın**: Database migrations'ı çalıştırın
4. **Aşama 5'i tamamlayın**: Testleri çalıştırın
5. **Aşama 6'yı tamamlayın**: Railway'a deploy edin

Her aşamayı tamamladıktan sonra bir sonraki aşamaya geçin!

