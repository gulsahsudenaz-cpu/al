# 📊 Mevcut Durum ve Sonraki Adımlar

## ✅ Tamamlananlar

- ✅ Git repository oluşturuldu
- ✅ Virtual environment hazır
- ✅ Dependencies yüklendi
- ✅ Kod tamamlandı
- ✅ Telegram bot token yapılandırıldı
- ✅ .env dosyası oluşturuldu

## ⚠️ Yapılması Gerekenler

### 1. Docker Desktop'ı Başlatın (ZORUNLU)

**Docker Desktop şu anda çalışmıyor!**

```powershell
# Docker Desktop'ı açın ve başlatın
# Tamamen başlamasını bekleyin (1-2 dakika)

# Test edin:
docker ps
```

**Beklenen çıktı:** Container listesi (boş olabilir, önemli değil)

---

### 2. .env Dosyasını Düzenleyin (ZORUNLU)

**OPENAI_API_KEY henüz ayarlanmamış!**

```powershell
# .env dosyasını açın
notepad .env

# Şu satırı bulun:
OPENAI_API_KEY=your-openai-api-key-here

# Şu şekilde değiştirin:
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Dosyayı kaydedin
```

---

### 3. Docker Servislerini Başlatın

Docker Desktop başladıktan sonra:

```powershell
# Infra dizinine git
cd infra

# Servisleri başlat
docker-compose up -d postgres redis

# Servislerin başlamasını bekle (15 saniye)
Start-Sleep -Seconds 15

# Servisleri kontrol et
docker-compose ps

# pgvector extension
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Root'a dön
cd ..
```

**Beklenen çıktı:**
```
NAME                STATUS
chatbot-postgres    Up
chatbot-redis       Up
```

---

### 4. Database Migrations

```powershell
# Backend dizinine git
cd backend

# Virtual environment aktifleştir
.\venv\Scripts\Activate.ps1

# Environment variables yükle
Get-Content ..\.env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Alembic için sync driver
$env:DATABASE_URL = $env:DATABASE_URL -replace "postgresql\+asyncpg://", "postgresql://"

# Migrations çalıştır
alembic upgrade head
```

**Beklenen çıktı:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration
```

---

### 5. Backend'i Başlatın

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

### 6. Test Edin

Yeni bir terminal açın:

```powershell
# Health check
curl http://localhost:8000/health

# Beklenen çıktı:
# {"status":"ok"}
```

**Veya tarayıcıda:**
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

---

## 🎯 Hızlı Komutlar (Tüm Adımlar)

```powershell
# 1. Docker Desktop'ı başlatın (manuel)

# 2. .env dosyasını düzenleyin (manuel - OPENAI_API_KEY)

# 3. Docker servislerini başlatın
cd infra
docker-compose up -d postgres redis
Start-Sleep -Seconds 15
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"
cd ..

# 4. Database migrations
cd backend
.\venv\Scripts\Activate.ps1
Get-Content ..\.env | ForEach-Object { if ($_ -match '^([^#][^=]*)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process") } }
$env:DATABASE_URL = $env:DATABASE_URL -replace "postgresql\+asyncpg://", "postgresql://"
alembic upgrade head

# 5. Backend'i başlatın
uvicorn app.main:app --reload --port 8000
```

---

## ✅ Kontrol Listesi

### Hazırlık
- [x] .env dosyası oluşturuldu
- [x] Telegram bot token yapılandırıldı
- [ ] Docker Desktop başlatıldı ⚠️
- [ ] .env dosyası düzenlendi (OPENAI_API_KEY) ⚠️

### Servisler
- [ ] Docker servisleri başlatıldı
- [ ] pgvector extension kuruldu
- [ ] Database migrations çalıştırıldı

### Backend
- [ ] Backend başlatıldı
- [ ] Health check çalışıyor
- [ ] API docs erişilebilir

### Telegram
- [ ] Webhook ayarlandı
- [ ] Bot test edildi

---

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
1. Docker Desktop'ı açın
2. Tamamen başlamasını bekleyin
3. `docker ps` ile test edin

### .env Dosyası Eksik
1. `.env` dosyasını oluşturun
2. `OPENAI_API_KEY` ekleyin
3. `TELEGRAM_BOT_TOKEN` zaten var

### Database Bağlantı Hatası
1. Docker servislerinin çalıştığını kontrol edin
2. `DATABASE_URL` doğru mu kontrol edin
3. PostgreSQL container'ın sağlıklı olduğunu kontrol edin

### Migrations Hatası
1. Database URL'i kontrol edin
2. PostgreSQL'in çalıştığından emin olun
3. pgvector extension'ını manuel kurun

---

## 📚 İlgili Dokümantasyon

- [HEMEN_BASLA.md](HEMEN_BASLA.md) - Hızlı başlangıç
- [SONRAKI_ADIMLAR_DETAYLI.md](SONRAKI_ADIMLAR_DETAYLI.md) - Detaylı rehber
- [TELEGRAM_COMPLETE.md](TELEGRAM_COMPLETE.md) - Telegram kurulumu

---

## 🎉 Başarılar!

Her adımı tamamladığınızda, bir sonraki adıma geçin. Sorun yaşarsanız, dokümantasyona bakın.

**İyi çalışmalar! 🚀**

