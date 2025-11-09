# Backend Başlatma Rehberi

## Hızlı Başlatma

### Windows
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Veya `start_backend.bat` dosyasını çalıştırın:
```bash
backend\start_backend.bat
```

### Linux/Mac
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Veya `start_backend.sh` dosyasını çalıştırın:
```bash
chmod +x backend/start_backend.sh
./backend/start_backend.sh
```

## Gereksinimler

1. **Python 3.11+** yüklü olmalı
2. **Virtual Environment** aktif olmalı:
   ```bash
   # Windows
   backend\venv\Scripts\activate
   
   # Linux/Mac
   source backend/venv/bin/activate
   ```
3. **Bağımlılıklar** yüklü olmalı:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. **Veritabanı** çalışıyor olmalı (PostgreSQL)
5. **Redis** çalışıyor olmalı

## Ortam Değişkenleri

Backend'i başlatmadan önce `.env` dosyasını oluşturun:

```bash
# backend/.env
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
```

## Docker ile Başlatma

Tüm servisleri (PostgreSQL, Redis, Backend) Docker ile başlatmak için:

```bash
cd infra
docker-compose up -d
```

## Sorun Giderme

### Port 8000 zaten kullanımda
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Veritabanı bağlantı hatası
- PostgreSQL'in çalıştığından emin olun
- `DATABASE_URL` değişkeninin doğru olduğundan emin olun
- Migration'ları çalıştırın:
  ```bash
  cd backend
  alembic upgrade head
  ```

### Redis bağlantı hatası
- Redis'in çalıştığından emin olun
- `REDIS_URL` değişkeninin doğru olduğundan emin olun

### CORS hatası
- `DEBUG=True` olarak ayarlandığından emin olun
- Backend'in `http://localhost:8000` adresinde çalıştığından emin olun

## Admin Kullanıcısı Oluşturma

Backend başlatıldıktan sonra admin kullanıcısını oluşturun:

```bash
python scripts/create_admin.py
```

Varsayılan bilgiler:
- Kullanıcı Adı: `admin`
- Şifre: `admin123`

## Test

Backend'in çalıştığını test etmek için:

```bash
curl http://localhost:8000/health
```

Veya tarayıcıda:
```
http://localhost:8000/docs
```

## Admin Panel Bağlantısı

Backend başlatıldıktan sonra admin paneli şu adresten erişilebilir:

```
http://localhost:8000/admin/index.html
```

Veya frontend klasöründen direkt açabilirsiniz:
```
frontend/admin/index.html
```

Backend `http://localhost:8000` adresinde çalışıyorsa, admin panel otomatik olarak bağlanacaktır.

