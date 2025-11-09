# AI Chatbot System - Production Ready

Üretim seviyesinde, ölçeklenebilir, maliyet kontrollü AI destekli sohbet sistemi.

## Özellikler

- ✅ **Web Widget** - Gerçek zamanlı sohbet widget'ı (mobil uyumlu, 320px+)
- ✅ **Admin Panel** - RBAC ile yönetim paneli
- ✅ **Telegram Bot** - İki yönlü Telegram entegrasyonu
- ✅ **RAG Sistemi** - Hibrit arama (Semantic + BM25)
- ✅ **LLM Entegrasyonu** - GPT-4 Turbo desteği
- ✅ **WebSocket** - Gerçek zamanlı iletişim (heartbeat, deduplication)
- ✅ **Güvenlik** - JWT, OTP, RBAC, PII redaction, rate limiting
- ✅ **İzleme** - OpenTelemetry, metrikler, Grafana
- ✅ **Maliyet Kontrolü** - Günlük limit, token takibi
- ✅ **Test** - Pytest, Playwright, CI/CD

## Teknoloji Yığını

- **Backend**: FastAPI, SQLAlchemy, AsyncIO
- **Database**: PostgreSQL 15+ (pgvector)
- **Cache/PubSub**: Redis
- **Vector DB**: pgvector (HNSW)
- **LLM**: OpenAI GPT-4 Turbo
- **Frontend**: HTML/CSS/JS (Vite ready)
- **WebSocket**: FastAPI WebSocket
- **Workers**: RQ (Redis Queue)
- **Monitoring**: OpenTelemetry, Grafana

## Kurulum

### Gereksinimler

- Python 3.11+
- PostgreSQL 15+ (pgvector extension)
- Redis 7+
- Docker & Docker Compose (önerilir)

### Hızlı Başlangıç

1. **Repository'yi klonlayın**
```bash
git clone <repository-url>
cd chatbot
```

2. **Environment variables ayarlayın**
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. **Docker Compose ile başlatın**
```bash
cd infra
docker-compose up -d
```

4. **Backend bağımlılıklarını yükleyin**
```bash
cd ../backend
pip install -r requirements.txt
```

5. **Veritabanı migrations çalıştırın**
```bash
alembic upgrade head
```

6. **Backend'i başlatın**
```bash
uvicorn app.main:app --reload
```

## Yapılandırma

### Environment Variables

`.env` dosyasında aşağıdaki değişkenleri ayarlayın:

```env
# OpenAI
OPENAI_API_KEY=your-api-key
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
```

## API Dokümantasyonu

Backend çalıştıktan sonra:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend

### Widget

Widget'ı kullanmak için:

```html
<script>
window.ChatbotConfig = {
    apiUrl: "ws://localhost:8000/v1/ws/chat",
    roomKey: "tenant_123",
    theme: "auto"
};
</script>
<link rel="stylesheet" href="/widget/widget.css">
<script src="/widget/widget.js"></script>
```

### Admin Panel

Admin paneli: `frontend/admin/index.html`

## RAG Sistemi

RAG sistemi hibrit arama kullanır:
- **Semantic Search**: pgvector ile embedding bazlı arama
- **Keyword Search**: BM25 benzeri full-text search
- **Hybrid Scoring**: Ağırlıklandırılmış skorlama (0.7 semantic, 0.3 keyword)
- **Threshold**: Minimum similarity 0.7

## LLM Entegrasyonu

- **Model**: GPT-4 Turbo (varsayılan)
- **Streaming**: Token-by-token streaming desteği
- **Tool Calling**: Function calling desteği
- **Cost Tracking**: Her çağrıda maliyet takibi
- **Circuit Breaker**: Hata durumunda otomatik koruma

## Güvenlik

- **JWT Authentication**: Token tabanlı kimlik doğrulama
- **OTP**: Telegram OTP desteği
- **RBAC**: Rol tabanlı erişim kontrolü
- **PII Redaction**: Kişisel bilgi maskeleme
- **Rate Limiting**: İstek sınırlama
- **CORS**: Cross-origin koruması

## İzleme

- **OpenTelemetry**: Distributed tracing
- **Metrics**: Custom metrikler
- **Grafana**: Dashboard'lar
- **Health Checks**: Sağlık kontrolleri

## Test

```bash
# Unit tests
pytest backend/tests/

# Integration tests
pytest backend/tests/integration/

# E2E tests
playwright test
```

## Deployment

### Railway (Önerilen)

Railway ile kolay deployment için [DEPLOYMENT.md](DEPLOYMENT.md) dosyasına bakın.

**Hızlı Başlangıç:**
1. Git repository'yi GitHub'a push edin
2. Railway'de yeni proje oluşturun
3. GitHub repository'nizi bağlayın
4. PostgreSQL ve Redis plugin'lerini ekleyin
5. Environment variables'ları ayarlayın
6. Deploy!

Detaylı rehber: [DEPLOYMENT.md](DEPLOYMENT.md)

### Docker

```bash
docker-compose -f infra/docker-compose.yml up -d
```

### Production

1. Environment variables ayarlayın
2. SSL sertifikası yapılandırın (Let's Encrypt)
3. Nginx reverse proxy yapılandırın
4. Monitoring kurun
5. Backup stratejisi oluşturun

## Başarı Kriterleri

- ✅ RAG hit rate ≥ %70
- ✅ p95 latency < 800ms (RAG)
- ✅ Uptime ≥ %99.5
- ✅ Cost per chat < $0.01
- ✅ User satisfaction ≥ 4.0/5.0

## Lisans

MIT License

## 📚 Dokümantasyon

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Kurulum rehberi (hızlı başlangıç + detaylı)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Railway deployment rehberi
- [TELEGRAM.md](TELEGRAM.md) - Telegram bot kurulumu
- [kurulum.md](kurulum.md) - Teknik kurulum detayları (Türkçe)

## Destek

Sorularınız için issue açabilirsiniz.

