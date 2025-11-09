# 🚀 Sonraki Adımlar - Detaylı Rehber

## ✅ Tamamlanan İşlemler

- ✅ Git repository oluşturuldu
- ✅ Virtual environment hazır
- ✅ Dependencies yüklendi
- ✅ Kod tamamlandı
- ✅ Telegram bot token yapılandırıldı
- ✅ .env dosyası oluşturuldu

## 📋 Şimdi Yapılacaklar (Sırayla)

### ⚠️ ÖNEMLİ: Docker Desktop'ı Başlatın

**Docker Desktop çalışmıyor!**

1. Docker Desktop'ı açın
2. Tamamen başlamasını bekleyin (1-2 dakika)
3. Docker Desktop'ın sistem tray'inde göründüğünden emin olun
4. Test edin:
   ```powershell
   docker ps
   ```

**Docker Desktop başladıktan sonra devam edin.**

---

### Adım 1: .env Dosyasını Düzenleyin 📝

`.env` dosyası oluşturuldu. Şimdi düzenleyin:

1. `.env` dosyasını açın:
   ```powershell
   notepad .env
   ```

2. **ZORUNLU:** `OPENAI_API_KEY` değerini değiştirin:
   ```env
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

3. Dosyayı kaydedin ve kapatın.

---

### Adım 2: Docker Servislerini Başlatın 🐳

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

### Adım 3: pgvector Extension'ını Kurun 🔧

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

### Adım 4: Database Migrations 🗄️

Database tablolarını oluşturun:

```powershell
# Backend dizinine git
cd backend

# Virtual environment aktifleştir
.\venv\Scripts\Activate.ps1

# Environment variables yükle (root'taki .env dosyasından)
Get-Content ..\.env | ForEach-Object {
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

### Adım 5: Backend'i Başlatın 🚀

Backend'i başlatın:

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

### Adım 6: Backend'i Test Edin 🧪

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

### Adım 7: Telegram Webhook'u Ayarlayın 🤖

Backend çalışırken, webhook'u ayarlayın:

#### Lokal Test (ngrok)

```powershell
# 1. ngrok'u indirin ve çalıştırın
# https://ngrok.com/download
ngrok http 8000

# 2. ngrok URL'ini alın (örn: https://abc123.ngrok.io)

# 3. Webhook'u ayarlayın
$webhookUrl = "https://abc123.ngrok.io/v1/telegram/webhook"
curl -X POST http://localhost:8000/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"

# 4. Webhook bilgisini kontrol edin
curl http://localhost:8000/v1/telegram/webhook-info
```

#### Production (Railway)

```powershell
# Railway URL'inizi kullanın
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"
curl -X POST https://your-app.railway.app/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

---

### Adım 8: Bot'u Test Edin 🧪

1. Telegram'da @Sohbet_Admin_Bot'a mesaj gönderin
2. Bot yanıt vermeli
3. Backend loglarını kontrol edin

---

## 🎯 Hızlı Komutlar

### Tüm Adımları Tek Seferde

```powershell
# 1. Docker Desktop'ı başlatın (manuel)

# 2. .env dosyasını düzenleyin (manuel - OPENAI_API_KEY ekleyin)

# 3. Docker servislerini başlatın
cd infra
docker-compose up -d postgres redis
Start-Sleep -Seconds 15
cd ..

# 4. pgvector extension
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Database migrations
cd backend
.\venv\Scripts\Activate.ps1
Get-Content ..\.env | ForEach-Object { if ($_ -match '^([^#][^=]*)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process") } }
$env:DATABASE_URL = $env:DATABASE_URL -replace "postgresql\+asyncpg://", "postgresql://"
alembic upgrade head

# 6. Backend'i başlatın
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

### Telegram
- [ ] Webhook ayarlandı
- [ ] Webhook bilgisi kontrol edildi
- [ ] Bot'a mesaj gönderildi
- [ ] Bot yanıt verdi

---

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
1. Docker Desktop'ı başlatın
2. Docker Desktop'ın tamamen açılmasını bekleyin
3. Docker'ın çalıştığını kontrol edin: `docker ps`

### .env Dosyası Eksik
1. `.env` dosyasını oluşturun
2. `OPENAI_API_KEY` ekleyin
3. `TELEGRAM_BOT_TOKEN` zaten eklendi

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

### Telegram Bot Yanıt Vermiyor
1. Webhook kontrolü: `curl http://localhost:8000/v1/telegram/webhook-info`
2. Backend loglarını kontrol edin
3. Token kontrolü: .env dosyasında token doğru mu?

---

## 📚 İlgili Dokümantasyon

- [TELEGRAM_COMPLETE.md](TELEGRAM_COMPLETE.md) - Telegram bot kurulumu
- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Detaylı Telegram kurulum rehberi
- [HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md) - Hızlı başlangıç
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment

---

## 🎉 Başarılar!

Her adımı tamamladığınızda, bir sonraki adıma geçin. Sorun yaşarsanız, dokümantasyona bakın veya yardım isteyin.

**İyi çalışmalar! 🚀**

