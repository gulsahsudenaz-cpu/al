# 🚀 Sonraki Adımlar - Adım Adım İlerleme

## 📋 Mevcut Durum

✅ **Tamamlananlar:**
- Git repository oluşturuldu
- Virtual environment hazır
- Dependencies yüklendi
- Kod tamamlandı
- Dokümantasyon eklendi

⚠️ **Yapılması Gerekenler:**
- Docker Desktop başlatılmalı
- .env dosyası düzenlenmeli (OPENAI_API_KEY)
- Docker servisleri başlatılmalı
- Database migrations çalıştırılmalı
- Backend test edilmeli

## 🎯 Adım Adım İlerleme

### Adım 1: Docker Desktop'ı Başlatın ⚠️

**Docker Desktop çalışmıyor!**

1. Docker Desktop'ı açın
2. Tamamen başlamasını bekleyin (1-2 dakika)
3. Docker Desktop'ın sistem tray'inde göründüğünden emin olun
4. Şu komutu çalıştırarak test edin:
   ```powershell
   docker ps
   ```

**Docker Desktop başladıktan sonra devam edin.**

---

### Adım 2: .env Dosyasını Düzenleyin 📝

`.env` dosyası oluşturuldu. Şimdi düzenleyin:

1. `.env` dosyasını açın:
   ```powershell
   notepad .env
   ```

2. **ZORUNLU:** `OPENAI_API_KEY` değerini değiştirin:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

3. İsteğe bağlı olarak diğer değerleri de düzenleyebilirsiniz:
   - `SECRET_KEY`: Güvenli bir secret key
   - `JWT_SECRET_KEY`: JWT için secret key
   - `DATABASE_URL`: Eğer farklı bir database kullanıyorsanız
   - `REDIS_URL`: Eğer farklı bir Redis kullanıyorsanız

4. Dosyayı kaydedin ve kapatın.

---

### Adım 3: Docker Servislerini Başlatın 🐳

Docker Desktop başladıktan sonra:

```powershell
# Infra dizinine git
cd infra

# Servisleri başlat
docker-compose up -d postgres redis

# Servislerin başlamasını bekle (10-15 saniye)
Start-Sleep -Seconds 15

# Servisleri kontrol et
docker-compose ps
```

**Beklenen çıktı:**
```
NAME                STATUS
chatbot-postgres    Up
chatbot-redis       Up
```

---

### Adım 4: pgvector Extension'ını Kurun 🔧

PostgreSQL'de pgvector extension'ını aktifleştirin:

```powershell
# pgvector extension'ını kur
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Beklenen çıktı:**
```
CREATE EXTENSION
```

---

### Adım 5: Database Migrations 🗄️

Database tablolarını oluşturun:

```powershell
# Root dizine dön
cd ..

# Backend dizinine git
cd backend

# Virtual environment aktifleştir
.\venv\Scripts\Activate.ps1

# Environment variables yükle (root'taki .env dosyasından)
# PowerShell'de .env dosyasını yükle
Get-Content ..\env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Alembic için sync driver kullan (asyncpg değil)
$dbUrl = $env:DATABASE_URL
if ($dbUrl -like "*asyncpg*") {
    $dbUrl = $dbUrl -replace "postgresql\+asyncpg://", "postgresql://"
}
$env:DATABASE_URL = $dbUrl

# Migrations çalıştır
alembic upgrade head
```

**Beklenen çıktı:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration
```

---

### Adım 6: Backend'i Başlatın 🚀

Backend'i başlatın ve test edin:

```powershell
# Backend dizininde (virtual environment aktif)
uvicorn app.main:app --reload --port 8000
```

**Beklenen çıktı:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### Adım 7: Backend'i Test Edin 🧪

Yeni bir terminal açın ve test edin:

```powershell
# Health check
curl http://localhost:8000/health

# Beklenen çıktı:
# {"status":"ok"}
```

**Veya tarayıcıda:**
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

---

### Adım 8: GitHub'a Push Edin 📤

GitHub'da repository oluşturun ve push edin:

1. **GitHub'da repository oluşturun:**
   - https://github.com/new adresine gidin
   - Repository adı: `chatbot` (veya istediğiniz ad)
   - Public veya Private seçin
   - **ÖNEMLİ:** README, .gitignore, license **EKLEMEYIN** (zaten var)

2. **GitHub'a push edin:**
   ```powershell
   # Root dizinde
   git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
   git branch -M main
   git push -u origin main
   ```

3. **GitHub Secrets ayarlayın:**
   - Repository Settings → Secrets and variables → Actions
   - "New repository secret" butonuna tıklayın
   - Şu secrets'ları ekleyin:
     - `OPENAI_API_KEY`: OpenAI API anahtarınız
     - `SECRET_KEY`: Güvenli bir secret key
     - `JWT_SECRET_KEY`: JWT için secret key

---

### Adım 9: Railway Deployment 🚂

Railway'a deploy edin:

1. **Railway'a gidin:**
   - https://railway.app adresine gidin
   - GitHub ile login yapın

2. **Proje oluşturun:**
   - "New Project" butonuna tıklayın
   - "Deploy from GitHub repo" seçin
   - Repository'nizi seçin
   - "Deploy" butonuna tıklayın

3. **PostgreSQL plugin ekleyin:**
   - "+ New" butonuna tıklayın
   - "Database" → "Add PostgreSQL" seçin
   - PostgreSQL servisi oluşturulacak
   - **ÖNEMLİ:** PostgreSQL'de pgvector extension'ını aktifleştirin:
     - Railway dashboard'da PostgreSQL servisine tıklayın
     - "Query" sekmesine gidin
     - Şu SQL'i çalıştırın:
       ```sql
       CREATE EXTENSION IF NOT EXISTS vector;
       ```

4. **Redis plugin ekleyin:**
   - "+ New" butonuna tıklayın
   - "Database" → "Add Redis" seçin
   - Redis servisi oluşturulacak

5. **Environment variables ayarlayın:**
   - Railway dashboard'da "Variables" sekmesine gidin
   - Şu variables'ları ekleyin:
     ```env
     OPENAI_API_KEY=sk-your-openai-api-key
     SECRET_KEY=your-secret-key
     JWT_SECRET_KEY=your-jwt-secret-key
     MODEL=gpt-4-turbo
     LLM_DAILY_COST_LIMIT=50.0
     DEBUG=False
     RAG_MIN_SIMILARITY=0.7
     ENABLE_METRICS=True
     ```
   - **NOT:** `DATABASE_URL` ve `REDIS_URL` Railway tarafından otomatik sağlanır.

6. **Deploy ve kontrol:**
   - Railway otomatik olarak deploy edecek
   - Deploy loglarını kontrol edin
   - Health check: `https://your-app.railway.app/health`
   - API docs: `https://your-app.railway.app/docs`

Detaylı rehber: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎯 Hızlı Komutlar

### Tüm Adımları Tek Seferde Çalıştır

```powershell
# 1. Docker Desktop'ı başlatın (manuel)

# 2. .env dosyasını düzenleyin (manuel)

# 3. Complete setup script'ini çalıştırın
.\scripts\complete_setup.ps1

# 4. Backend'i başlatın
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

---

## ✅ Kontrol Listesi

### Hazırlık
- [ ] Docker Desktop başlatıldı
- [ ] .env dosyası düzenlendi (OPENAI_API_KEY eklendi)
- [ ] Docker servisleri başlatıldı
- [ ] pgvector extension kuruldu
- [ ] Database migrations çalıştırıldı

### Backend
- [ ] Backend başlatıldı
- [ ] Health check çalışıyor
- [ ] API docs erişilebilir

### GitHub
- [ ] GitHub repository oluşturuldu
- [ ] GitHub'a push edildi
- [ ] GitHub Secrets ayarlandı

### Railway
- [ ] Railway hesabı oluşturuldu
- [ ] Proje oluşturuldu
- [ ] PostgreSQL plugin eklendi
- [ ] Redis plugin eklendi
- [ ] pgvector extension kuruldu
- [ ] Environment variables ayarlandı
- [ ] Deploy başarılı

---

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
1. Docker Desktop'ı başlatın
2. Docker Desktop'ın tamamen açılmasını bekleyin
3. Docker'ın çalıştığını kontrol edin: `docker ps`

### .env Dosyası Eksik
1. `.env` dosyasını oluşturun
2. `OPENAI_API_KEY` ekleyin
3. Diğer değişkenleri ayarlayın

### Database Bağlantı Hatası
1. Docker servislerinin çalıştığını kontrol edin
2. `DATABASE_URL` doğru mu kontrol edin
3. PostgreSQL container'ın sağlıklı olduğunu kontrol edin

### Migrations Hatası
1. Database URL'i kontrol edin
2. PostgreSQL'in çalıştığından emin olun
3. pgvector extension'ını manuel kurun:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Backend Başlamıyor
1. Virtual environment aktif mi kontrol edin
2. Dependencies yüklendi mi kontrol edin: `pip list`
3. Environment variables doğru mu kontrol edin
4. Port 8000 kullanımda mı kontrol edin

---

## 📚 İlgili Dokümantasyon

- [TAMAMLANDI.md](TAMAMLANDI.md) - Kurulum tamamlandı
- [HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md) - 5 dakikada çalıştırma
- [ASAMA_ASAMA_REHBER.md](ASAMA_ASAMA_REHBER.md) - Detaylı adım adım rehber
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment rehberi
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Kapsamlı kurulum rehberi

---

## 🎉 Başarılar!

Her adımı tamamladığınızda, bir sonraki adıma geçin. Sorun yaşarsanız, dokümantasyona bakın veya yardım isteyin.

**İyi çalışmalar! 🚀**

