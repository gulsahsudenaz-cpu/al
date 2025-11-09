# Hızlı Başlangıç Kılavuzu

## 1. Gereksinimler

- Python 3.11+
- PostgreSQL 15+ (pgvector extension)
- Redis 7+
- Docker & Docker Compose

## 2. Kurulum

### Adım 1: Repository'yi klonlayın
```bash
git clone <repository-url>
cd chatbot
```

### Adım 2: Environment variables
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

### Adım 3: Docker servislerini başlatın
```bash
cd infra
docker-compose up -d postgres redis
cd ..
```

### Adım 4: Python bağımlılıklarını yükleyin
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Adım 5: Veritabanı migrations
```bash
cd backend
alembic upgrade head
cd ..
```

### Adım 6: Backend'i başlatın
```bash
cd backend
uvicorn app.main:app --reload
```

Backend şu adreste çalışacak: http://localhost:8000

## 3. Test

### API Health Check
```bash
curl http://localhost:8000/health
```

### WebSocket Test
Browser console'da:
```javascript
const ws = new WebSocket('ws://localhost:8000/v1/ws/chat?room_key=test');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.send(JSON.stringify({ type: 'client.message', text: 'Merhaba' }));
```

## 4. Frontend

### Widget
`frontend/widget/index.html` dosyasını bir web server'da açın.

### Admin Panel
`frontend/admin/index.html` dosyasını açın ve admin kullanıcı ile giriş yapın.

## 5. Telegram Bot

### Bot Token
`.env` dosyasına `TELEGRAM_BOT_TOKEN` ekleyin.

### Webhook
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://yourdomain.com/v1/telegram/webhook"
```

## Sorun Giderme

### PostgreSQL bağlantı hatası
- PostgreSQL'in çalıştığından emin olun
- `DATABASE_URL` değişkenini kontrol edin

### Redis bağlantı hatası
- Redis'in çalıştığından emin olun
- `REDIS_URL` değişkenini kontrol edin

### pgvector extension hatası
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Sonraki Adımlar

1. İlk admin kullanıcısını oluşturun
2. Knowledge base dokümanları ekleyin
3. RAG sistemini test edin
4. LLM entegrasyonunu yapılandırın
5. Monitoring kurun

