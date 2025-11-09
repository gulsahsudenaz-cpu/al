# 🤖 AI-Powered Chatbot System

Production-ready AI chatbot with RAG (Retrieval Augmented Generation), LLM integration, and multi-channel support (Web, Telegram, Admin Panel).

## 🚀 Features

- **Multi-Channel Support**: Web widget, Admin panel (RBAC), Telegram bot
- **RAG System**: Hybrid search (semantic + BM25) with pgvector
- **LLM Integration**: GPT-4 Turbo with cost tracking and caching
- **Real-time Communication**: WebSocket with heartbeat and reconnection
- **Media Processing**: Voice transcription (Whisper), image processing, file uploads
- **Security**: JWT authentication, OTP, PII redaction, rate limiting
- **Monitoring**: OpenTelemetry, Prometheus metrics, Grafana dashboards
- **Production Ready**: Docker, health checks, automated SSL, auto-scaling

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- OpenAI API Key
- (Optional) Telegram Bot Token
- (Optional) S3/MinIO for media storage

## 🏃 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/gulsahsudenaz-cpu/al.git
cd al
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create `backend/.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
```

### 4. Database Setup

```bash
cd backend
alembic upgrade head
python ../scripts/create_admin.py
```

### 5. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access Admin Panel

Open `frontend/admin/login.html` in browser:
- Username: `admin`
- Password: `admin123`

## 🚂 Railway Deployment

### 1. Connect GitHub Repository

1. Go to [Railway](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Select repository: `gulsahsudenaz-cpu/al`

### 2. Add Services

- **PostgreSQL**: Add PostgreSQL service (Railway will auto-create)
- **Redis**: Add Redis service (Railway will auto-create)
- **Backend**: Main application service

### 3. Environment Variables

Set in Railway dashboard:

```
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
OPENAI_API_KEY=your-openai-api-key
MODEL=gpt-4-turbo
ENABLE_METRICS=True
```

### 4. Deploy

Railway will automatically:
- Build the application
- Run migrations (`alembic upgrade head`)
- Start the backend service
- Health check on `/health`

### 5. Custom Domain (Optional)

1. Go to Settings → Domains
2. Add custom domain
3. Railway will auto-configure SSL

## 📁 Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Core utilities
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── websocket/      # WebSocket manager
│   │   └── workers/        # Background workers
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── admin/              # Admin panel
│   └── widget/             # Web widget
├── infra/                  # Docker & infrastructure
├── scripts/                # Utility scripts
└── tests/                  # Test suites
```

## 🔧 Configuration

### Backend Config

Key settings in `backend/app/config.py`:

- `DEBUG`: Enable debug mode (default: True)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key
- `RAG_MIN_SIMILARITY`: RAG similarity threshold (default: 0.7)
- `LLM_DAILY_COST_LIMIT`: Daily LLM cost limit (default: $50)

### Environment Variables

See `backend/.env.example` for all available options.

## 📊 API Documentation

Once backend is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Admin Credentials

Default admin user:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change password in production!

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# E2E tests
npm test
```

## 📈 Monitoring

- **Prometheus Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/health
- **OpenTelemetry**: Configure `OTEL_EXPORTER_OTLP_ENDPOINT`

## 🐳 Docker Deployment

```bash
cd infra
docker-compose up -d
```

## 📝 Documentation

- [Setup Guide](SETUP_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Admin Info](ADMIN_BILGILERI.md)
- [Quick Start](HIZLI_BASLATMA.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT-4 Turbo and Whisper API
- FastAPI for the web framework
- pgvector for vector search
- Railway for hosting platform

## 🔗 Links

- [Railway Deployment](https://railway.app)
- [OpenAI API](https://openai.com/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

---

**Made with ❤️ for AI-powered customer support**
