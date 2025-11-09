# 🚀 Kurulum Durumu ve Sonraki Adımlar

## ✅ Tamamlananlar

### Aşama 1: Git Repository ✅
- [x] Git repository oluşturuldu
- [x] İlk commit yapıldı
- [x] Tüm dosyalar commit edildi

### Aşama 2: Lokal Geliştirme Ortamı ✅
- [x] Python 3.13.9 kurulu
- [x] Virtual environment oluşturuldu (`backend/venv`)
- [x] Temel dependencies yüklendi:
  - FastAPI, Uvicorn
  - SQLAlchemy, AsyncPG, Alembic
  - Redis, RQ
  - OpenAI, HTTP clients
  - Prometheus client
  - pgvector, Pillow
  - Security (JWT, bcrypt, cryptography)

## ⚠️ Yapılması Gerekenler

### 1. Docker Desktop'ı Başlatın

Docker Desktop çalışmıyor. Lütfen:

1. Docker Desktop'ı başlatın
2. Docker Desktop'ın tamamen açılmasını bekleyin
3. Docker'ın çalıştığını kontrol edin: `docker ps`

### 2. Environment Variables (.env)

`.env` dosyasını oluşturun ve düzenleyin:

```bash
# Root dizinde
cp .env.example .env
```

**.env dosyasında ayarlanması gerekenler:**
- `OPENAI_API_KEY`: OpenAI API anahtarınız (ZORUNLU)
- `SECRET_KEY`: Güvenli bir secret key
- `JWT_SECRET_KEY`: JWT için secret key
- `DATABASE_URL`: PostgreSQL connection string (Docker için: `postgresql://user:password@localhost:5432/chatbot`)
- `REDIS_URL`: Redis connection string (Docker için: `redis://localhost:6379/0`)

### 3. Docker Servislerini Başlat

Docker Desktop başladıktan sonra:

```bash
# Infra dizinine git
cd infra

# Servisleri başlat
docker-compose up -d postgres redis

# Servislerin başlamasını bekle (10-15 saniye)
# Kontrol et
docker-compose ps
```

### 4. Database Migrations

```bash
# Backend dizinine git
cd backend

# Virtual environment aktifleştir
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Environment variables yükle (root'taki .env dosyasından)
# Migrations çalıştır
alembic upgrade head
```

### 5. Backend'i Başlat ve Test Et

```bash
# Backend dizininde (virtual environment aktif)
uvicorn app.main:app --reload --port 8000

# Yeni terminal aç ve test et
curl http://localhost:8000/health
# veya tarayıcıda: http://localhost:8000/docs
```

### 6. GitHub'a Push

```bash
# GitHub'da repository oluşturun
# https://github.com/new

# GitHub'a push edin
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
git branch -M main
git push -u origin main
```

### 7. Railway Deployment

1. Railway'a gidin: https://railway.app
2. GitHub ile login yapın
3. "New Project" → "Deploy from GitHub repo"
4. Repository'nizi seçin
5. PostgreSQL plugin ekleyin
6. Redis plugin ekleyin
7. Environment variables ayarlayın
8. Deploy!

## 📋 Hızlı Komutlar

### Tüm Adımları Sırayla Çalıştır

```powershell
# 1. Docker Desktop'ı başlatın (manuel)

# 2. .env dosyasını oluştur ve düzenle
Copy-Item .env.example .env
# .env dosyasını düzenleyin

# 3. Docker servislerini başlat
cd infra
docker-compose up -d postgres redis
Start-Sleep -Seconds 10

# 4. pgvector extension
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Database migrations
cd ..\backend
.\venv\Scripts\Activate.ps1
alembic upgrade head

# 6. Backend'i başlat
uvicorn app.main:app --reload --port 8000
```

## 🔍 Kontrol Listesi

### Docker
- [ ] Docker Desktop çalışıyor
- [ ] `docker ps` komutu çalışıyor
- [ ] PostgreSQL container çalışıyor
- [ ] Redis container çalışıyor

### Environment
- [ ] `.env` dosyası oluşturuldu
- [ ] `OPENAI_API_KEY` ayarlandı
- [ ] `SECRET_KEY` ayarlandı
- [ ] `DATABASE_URL` doğru
- [ ] `REDIS_URL` doğru

### Database
- [ ] Migrations çalıştırıldı
- [ ] Tablolar oluşturuldu
- [ ] pgvector extension aktif

### Backend
- [ ] Backend başlatıldı
- [ ] Health check çalışıyor (`/health`)
- [ ] API docs erişilebilir (`/docs`)

### GitHub
- [ ] GitHub repository oluşturuldu
- [ ] GitHub'a push edildi
- [ ] GitHub Secrets ayarlandı

### Railway
- [ ] Railway hesabı oluşturuldu
- [ ] Proje oluşturuldu
- [ ] PostgreSQL plugin eklendi
- [ ] Redis plugin eklendi
- [ ] Environment variables ayarlandı
- [ ] Deploy başarılı

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
1. Docker Desktop'ı başlatın
2. Docker Desktop'ın tamamen açılmasını bekleyin
3. Docker'ın çalıştığını kontrol edin: `docker ps`

### Database Connection Error
- Docker servislerinin çalıştığından emin olun
- `DATABASE_URL` environment variable'ını kontrol edin
- PostgreSQL container'ın sağlıklı olduğunu kontrol edin: `docker ps`

### Migrations Failed
- Database URL'i kontrol edin
- PostgreSQL'in çalıştığından emin olun
- pgvector extension'ını manuel olarak kurun:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

### Backend Başlamıyor
- Virtual environment aktif mi kontrol edin
- Dependencies yüklendi mi kontrol edin: `pip list`
- Environment variables doğru mu kontrol edin
- Port 8000 kullanımda mı kontrol edin

## 📚 İlgili Dokümantasyon

- [ASAMA_ASAMA_REHBER.md](ASAMA_ASAMA_REHBER.md) - Detaylı adım adım rehber
- [NEXT_STEPS.md](NEXT_STEPS.md) - Şimdi ne yapmalıyım?
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment rehberi
- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç

## 🎯 Sonraki Adım

**Şimdi yapmanız gereken:**
1. Docker Desktop'ı başlatın
2. `.env` dosyasını oluşturun ve düzenleyin
3. Docker servislerini başlatın
4. Database migrations çalıştırın
5. Backend'i başlatın ve test edin

Her adımı tamamladıktan sonra bir sonraki adıma geçin!

