# 📖 Adım Adım Rehber - Şimdi Ne Yapmalıyım?

## 🎯 Mevcut Durum

✅ **Tamamlandı:**
- Git repository hazır
- Virtual environment hazır
- Dependencies yüklendi
- Kod tamamlandı
- .env dosyası oluşturuldu

⚠️ **Şimdi Yapılacaklar:**
1. Docker Desktop'ı başlatın
2. .env dosyasını düzenleyin (OPENAI_API_KEY)
3. Docker servislerini başlatın
4. Database migrations çalıştırın
5. Backend'i başlatın

---

## 🚀 Hızlı Başlangıç (5 Dakika)

### 1. Docker Desktop'ı Başlatın

**ÖNEMLİ:** Docker Desktop çalışmıyor!

1. Docker Desktop'ı açın
2. Başlamasını bekleyin (1-2 dakika)
3. Test edin:
   ```powershell
   docker ps
   ```

### 2. .env Dosyasını Düzenleyin

```powershell
# .env dosyasını açın
notepad .env

# OPENAI_API_KEY değerini değiştirin
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Dosyayı kaydedin
```

### 3. Complete Setup Script'ini Çalıştırın

```powershell
# Tüm adımları otomatik olarak gerçekleştirir
.\scripts\complete_setup.ps1
```

**Veya manuel olarak:**

### 4. Docker Servislerini Başlatın

```powershell
cd infra
docker-compose up -d postgres redis
Start-Sleep -Seconds 15
docker-compose ps
```

### 5. pgvector Extension

```powershell
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 6. Database Migrations

```powershell
cd ..\backend
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

### 7. Backend'i Başlatın

```powershell
# Backend dizininde (virtual environment aktif)
uvicorn app.main:app --reload --port 8000
```

### 8. Test Edin

```powershell
# Yeni terminal açın
curl http://localhost:8000/health

# Veya tarayıcıda
# http://localhost:8000/docs
```

---

## 📋 Detaylı Adımlar

### Adım 1: Docker Desktop ⚠️

**Docker Desktop çalışmıyor!**

1. Docker Desktop'ı açın
2. Başlamasını bekleyin
3. Test edin: `docker ps`

### Adım 2: .env Dosyası 📝

`.env` dosyası oluşturuldu. Şimdi düzenleyin:

1. `.env` dosyasını açın: `notepad .env`
2. `OPENAI_API_KEY` değerini değiştirin
3. Dosyayı kaydedin

### Adım 3: Docker Servisleri 🐳

```powershell
cd infra
docker-compose up -d postgres redis
```

### Adım 4: pgvector Extension 🔧

```powershell
docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Adım 5: Database Migrations 🗄️

```powershell
cd ..\backend
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

### Adım 6: Backend 🚀

```powershell
uvicorn app.main:app --reload --port 8000
```

### Adım 7: Test 🧪

```powershell
curl http://localhost:8000/health
```

---

## ✅ Kontrol Listesi

- [ ] Docker Desktop başlatıldı
- [ ] .env dosyası düzenlendi (OPENAI_API_KEY)
- [ ] Docker servisleri başlatıldı
- [ ] pgvector extension kuruldu
- [ ] Database migrations çalıştırıldı
- [ ] Backend başlatıldı
- [ ] Health check çalışıyor
- [ ] API docs erişilebilir

---

## 🆘 Sorun Giderme

### Docker Desktop Çalışmıyor
- Docker Desktop'ı başlatın
- Başlamasını bekleyin
- `docker ps` ile test edin

### .env Dosyası Eksik
- `.env` dosyasını oluşturun
- `OPENAI_API_KEY` ekleyin

### Database Bağlantı Hatası
- Docker servislerinin çalıştığını kontrol edin
- `DATABASE_URL` doğru mu kontrol edin

### Migrations Hatası
- Database URL'i kontrol edin
- PostgreSQL'in çalıştığından emin olun
- pgvector extension'ını kurun

---

## 📚 Daha Fazla Bilgi

- [SONRAKI_ADIMLAR.md](SONRAKI_ADIMLAR.md) - Detaylı sonraki adımlar
- [HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md) - Hızlı başlangıç
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment
- [TAMAMLANDI.md](TAMAMLANDI.md) - Kurulum tamamlandı

---

## 🎉 Başarılar!

Her adımı tamamladığınızda, bir sonraki adıma geçin. Sorun yaşarsanız, dokümantasyona bakın.

**İyi çalışmalar! 🚀**

