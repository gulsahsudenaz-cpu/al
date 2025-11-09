# Kurulum (Kurulum.md) — AI Chatbot System

Bu dosya **sistem kurulumunu** uçtan uca anlatır ve otomasyon için komutları içerir. 

Güncel mimari: FastAPI (backend), Web Widget + Admin Panel (frontend), PostgreSQL (pgvector), Redis, RQ Worker, Nginx, Docker Compose.

> Not: Ortam değişkenleri `.env` dosyasından okunur. Örnek için `.env.example`'ı baz alın.

---

## 1) Gereksinimler

- Docker + Docker Compose
- Python 3.11+ (lokal geliştirme için)
- Node 18+ (e2e ve statik build için)
- OpenAI API Key (LLM / Embedding)
- Telegram Bot Token (opsiyonel OTP)
- PostgreSQL 15+ (pgvector etkin)

## 2) Hızlı Başlangıç (Docker Compose)

```bash
cd infra
cp ../.env.example ../.env     # ortam değişkenlerini düzenleyin
docker-compose up -d           # postgres, redis, backend, worker, nginx
```

> `http://localhost:8080` Nginx reverse proxy (backend `/api`, statik `/admin`, `/widget` kuralı sizdeki Nginx ayarına göre değişebilir).

## 3) Lokal Geliştirme (Hot Reload)

### Backend:

```bash
cd backend
pip install -r requirements/dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend Admin / Widget (tek dosya sürümünü static olarak servis ediyorsanız bu adımı atlayın):

```bash
# Örn. admin React/Vite projesi varsa
cd frontend/admin
npm i
npm run dev
```

## 4) Veritabanı & Migrasyonlar

```bash
cd backend
alembic upgrade head

# yeni değişiklik
alembic revision -m "add_x" --autogenerate
alembic upgrade head
```

## 5) Çalışma Zamanı Ayarları (Özet)

- `DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/chatbot`
- `REDIS_URL=redis://redis:6379/0`
- `OPENAI_API_KEY=...`
- `JWT_SECRET=...`
- `TELEGRAM_BOT_TOKEN=... (ops.)`
- `RAG_MIN_SIMILARITY=0.70`
- `LLM_DAILY_COST_LIMIT=50`

## 6) Gözlemlenebilirlik

### 6.1 Prometheus Scrape

- Backend `/metrics` metrik uç noktası açık.
- `infra/monitoring/prometheus.yml` dosyasındaki `targets` kısmında backend:8000/metrics var.

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.monitoring.yml up -d
```

### 6.2 OpenTelemetry (Traces)

- `backend/app/monitoring/otel_fastapi.py` backend içinde kullanılır:

```python
# app/main.py içinde otomatik olarak setup edilir
# OTEL_EXPORTER_OTLP_ENDPOINT environment variable'ı ayarlanmalı
```

- Grafana ile tempo/jaeger'e bağlanın.

## 7) Testler

### 7.1 Unit/Integration (pytest)

```bash
cd backend
pytest -q
pytest -v --cov=app --cov-report=html
```

### 7.2 E2E (Playwright)

```bash
npm i -D @playwright/test
npx playwright install
npx playwright test
```

## 8) CI/CD (GitHub Actions)

- `.github/workflows/ci.yml` dosyası: lint + test + e2e.
- Ortam sırları (`OPENAI_API_KEY`, vb.) GitHub Secrets'te.

**GitHub Secrets Ayarlama:**
1. Repository Settings → Secrets and variables → Actions
2. New repository secret ekle:
   - `OPENAI_API_KEY`: OpenAI API anahtarı
   - Diğer gerekli secrets

## 9) Worker & İndeksleme

- `backend/app/workers/indexer.py` içinde RQ job tanımlı.
- Belgeler `/v1/rag/documents` ile kuyruğa girer → worker işler → pgvector'a yazar.

**Worker Çalıştırma:**
```bash
cd backend
python -m app.workers.indexer
```

**Document Indexing:**
```python
from app.workers.indexer import enqueue_document
enqueue_document(doc_id="uuid-here")
```

## 10) Güvenlik Notları

- CORS allowlist
- Rate limit (Redis tabanlı)
- PII redaction açık
- JWT + OTP
- RBAC (admin/supervisor/agent)

> Sorun/öneri: `README.md` altında issue açın veya `docs/` klasörü.

---

## Hızlı Entegrasyon Notları

### 1) Monitoring

#### Traces (OTLP)

`app/main.py` içine otomatik olarak eklenir:

```python
# OTEL_EXPORTER_OTLP_ENDPOINT environment variable'ı ayarlanmalı
# Örnek: http://otel-collector:4318
```

#### Metrics (Prometheus)

`/metrics` endpoint'i otomatik olarak açık:

```bash
curl http://localhost:8000/metrics
```

### 2) CI

Workflow; Postgres/Redis servisle alembic upgrade + pytest çalıştırır, ayrı job'da Playwright E2E'yi koşturur.

GitHub Secrets'e `OPENAI_API_KEY` eklemeyi unutma.

### 3) Test Şablonu

- `test_health.py`: Basit health kontrolü
- `test_rag_system.py`: RAG metrik endpoint'i için "smoke" testi
- Playwright E2E: Canvas'taki Admin Panel akışına uygun şekilde sohbet açıp mesaj gönderir

### 4) Worker (RQ)

`enqueue_document(doc_id, path)` çağrısı ile indeks kuyruğuna atarsın. Gerçek embedding/pgvector yazımı için `backend/app/workers/indexer.py` dosyasındaki kodları kullanabilirsin.

### 5) Admin Panel (Canvas) ile Entegrasyon Hatırlatması

Canvas'taki tek dosya Admin Panel — Unified V1 kodunda WS mesajları şöyle bekleniyor:

- **Gönderim**: `{ type: 'client.message', text, chat_id }`
- **Sunucudan yazıyor**: `{ type: 'server.typing', chat_id, is_typing: true/false }`
- **Sunucudan mesaj**: `{ type: 'server.message', id, chat_id, text, ts }`

### 6) Railway Deployment

Railway'a deploy etmek için `DEPLOYMENT.md` dosyasına bakın.

**Hızlı Başlangıç:**
1. Git repository'yi GitHub'a push edin
2. Railway'de yeni proje oluşturun
3. GitHub repository'nizi bağlayın
4. PostgreSQL ve Redis plugin'lerini ekleyin
5. Environment variables'ları ayarlayın
6. Deploy!

## Sorun Giderme

### PostgreSQL bağlantı hatası
- PostgreSQL'in çalıştığından emin olun
- `DATABASE_URL` değişkenini kontrol edin
- pgvector extension'ını kontrol edin: `CREATE EXTENSION IF NOT EXISTS vector;`

### Redis bağlantı hatası
- Redis'in çalıştığından emin olun
- `REDIS_URL` değişkenini kontrol edin

### Migrations hatası
```bash
# Manuel olarak çalıştır
cd backend
alembic upgrade head
```

### Worker çalışmıyor
```bash
# Worker'ı manuel olarak başlat
cd backend
python -m app.workers.indexer
```

### Monitoring çalışmıyor
- `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable'ını kontrol edin
- Prometheus ve Grafana servislerinin çalıştığından emin olun
- `docker-compose.monitoring.yml` dosyasını kontrol edin
