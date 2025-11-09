# 🚀 Hızlı Başlatma Rehberi

## ⚠️ ÖNEMLİ: Backend Başlatma

Admin panelinin çalışması için **backend'in çalışıyor olması gerekiyor**.

## 1. Backend'i Başlatın

### Windows:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Veya Batch Dosyası ile:
```bash
backend\start_backend.bat
```

## 2. Backend'in Çalıştığını Kontrol Edin

Tarayıcıda şu adresi açın:
```
http://localhost:8000/health
```

Veya:
```
http://localhost:8000/docs
```

## 3. Admin Panelini Açın

Backend çalıştıktan sonra admin panelini açın:

```
frontend/admin/login.html
```

Veya backend üzerinden:
```
http://localhost:8000/admin/login.html
```

## 4. Giriş Yapın

- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`

## Sorun Giderme

### "Failed to fetch" Hatası

1. **Backend çalışıyor mu?**
   ```bash
   # Kontrol edin
   curl http://localhost:8000/health
   ```

2. **Port 8000 kullanımda mı?**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. **CORS Sorunu mu?**
   - Backend'de `DEBUG=True` olmalı (varsayılan)
   - `.env` dosyasında `DEBUG=True` olduğundan emin olun

### Veritabanı Hatası

```bash
cd backend
alembic upgrade head
```

### Admin Kullanıcısı Yok

```bash
python scripts/create_admin.py
```

## Gereksinimler

- ✅ Python 3.11+
- ✅ PostgreSQL çalışıyor
- ✅ Redis çalışıyor (opsiyonel, cache için)
- ✅ Virtual environment aktif
- ✅ Bağımlılıklar yüklü (`pip install -r requirements.txt`)

## Hızlı Komutlar

```bash
# Backend başlat
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Admin kullanıcısı oluştur
python scripts/create_admin.py

# Migration çalıştır
cd backend && alembic upgrade head

# Health check
curl http://localhost:8000/health
```

