# ⚡ Hızlı Başlangıç - 5 Dakikada Çalıştırma

## 🎯 Hızlı Kurulum (Windows)

### 1. Docker Desktop'ı Başlatın
- Docker Desktop'ı açın
- Tamamen başlamasını bekleyin

### 2. Setup Script'ini Çalıştırın

```powershell
# PowerShell'de (Admin değil, normal kullanıcı)
.\scripts\setup_windows.ps1
```

Bu script otomatik olarak:
- ✅ Docker kontrolü yapar
- ✅ Virtual environment oluşturur
- ✅ Dependencies yükler
- ✅ Docker servislerini başlatır
- ✅ Database migrations çalıştırır

### 3. .env Dosyasını Düzenleyin

```powershell
# .env dosyasını açın ve düzenleyin
notepad .env
```

**ZORUNLU değişkenler:**
- `OPENAI_API_KEY=sk-your-key-here`
- `SECRET_KEY=your-secret-key-here`
- `JWT_SECRET_KEY=your-jwt-secret-key-here`

### 4. Backend'i Başlatın

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### 5. Test Edin

```powershell
# Yeni terminal açın
curl http://localhost:8000/health

# Veya tarayıcıda açın
# http://localhost:8000/docs
```

## 🐳 Docker ile Hızlı Başlangıç

### Tüm Servisleri Başlat

```powershell
cd infra
docker-compose up -d
```

### Servisleri Kontrol Et

```powershell
docker-compose ps
```

### Logları Görüntüle

```powershell
docker-compose logs -f backend
```

## 📱 Frontend'i Test Et

### Widget

```powershell
# Widget'ı açın
# frontend/widget/index.html dosyasını tarayıcıda açın
```

### Admin Panel

```powershell
# Admin panel'i açın
# frontend/admin/index.html dosyasını tarayıcıda açın
```

## 🔧 Sorun Giderme

### Docker Çalışmıyor
```powershell
# Docker Desktop'ı başlatın
# Docker'ın çalıştığını kontrol edin
docker ps
```

### Port Kullanımda
```powershell
# Port 8000'i kullanan process'i bulun
netstat -ano | findstr :8000

# Process'i durdurun (PID'yi kullanarak)
taskkill /PID <PID> /F
```

### Database Bağlantı Hatası
```powershell
# PostgreSQL container'ının çalıştığını kontrol edin
docker ps --filter "name=postgres"

# Container'ı yeniden başlatın
docker restart chatbot-postgres
```

## 🚀 Railway Deployment

### Hızlı Deploy

1. GitHub'da repository oluşturun
2. Railway'a gidin: https://railway.app
3. "New Project" → "Deploy from GitHub repo"
4. Repository'nizi seçin
5. PostgreSQL ve Redis plugin'lerini ekleyin
6. Environment variables ayarlayın
7. Deploy!

Detaylı rehber: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 Daha Fazla Bilgi

- [ASAMA_ASAMA_REHBER.md](ASAMA_ASAMA_REHBER.md) - Detaylı adım adım rehber
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Kapsamlı kurulum rehberi
- [NEXT_STEPS.md](NEXT_STEPS.md) - Şimdi ne yapmalıyım?
- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç kılavuzu

## ✅ Başarı Kriterleri

Kurulum başarılı olduğunda:
- ✅ Backend çalışıyor: http://localhost:8000/health
- ✅ API docs erişilebilir: http://localhost:8000/docs
- ✅ PostgreSQL çalışıyor
- ✅ Redis çalışıyor
- ✅ Widget çalışıyor
- ✅ Admin panel çalışıyor

## 🎉 Hazırsınız!

Kurulum tamamlandı! Şimdi:
1. Backend'i başlatın
2. Frontend'i test edin
3. Railway'a deploy edin
4. Production'da kullanın!

