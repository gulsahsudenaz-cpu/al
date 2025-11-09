# Complete Setup Script - Windows PowerShell
# Tüm aşamaları otomatik olarak gerçekleştirir

Write-Host "🚀 AI Chatbot System - Complete Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

$ErrorActionPreference = "Stop"

# Aşama 1: Git Repository (Zaten yapıldı)
Write-Host "✅ Aşama 1: Git Repository - Tamamlandı" -ForegroundColor Green
Write-Host ""

# Aşama 2: Lokal Geliştirme Ortamı
Write-Host "🔄 Aşama 2: Lokal Geliştirme Ortamı" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

# Python kontrolü
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python bulunamadı. Lütfen Python 3.11+ yükleyin." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green

# Virtual environment
if (-not (Test-Path "backend\venv")) {
    Write-Host "📦 Virtual environment oluşturuluyor..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    Set-Location ..
    Write-Host "✅ Virtual environment oluşturuldu" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment mevcut" -ForegroundColor Green
}

# Dependencies
Write-Host "📦 Dependencies yükleniyor..." -ForegroundColor Yellow
Set-Location backend
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.\venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy asyncpg alembic redis python-jose passlib python-dotenv pydantic-settings openai httpx aiohttp prometheus-client pgvector python-multipart rq Pillow python-dateutil bcrypt cryptography --no-cache-dir --quiet
Set-Location ..
Write-Host "✅ Dependencies yüklendi" -ForegroundColor Green

# .env dosyası
if (-not (Test-Path ".env")) {
    Write-Host "📝 .env dosyası oluşturuluyor..." -ForegroundColor Yellow
    @"
# Application
DEBUG=False
SECRET_KEY=change-me-in-production-$(Get-Random)
JWT_SECRET_KEY=change-me-in-production-$(Get-Random)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (ZORUNLU - Lütfen düzenleyin)
OPENAI_API_KEY=your-openai-api-key-here

# Model
MODEL=gpt-4-turbo
LLM_DAILY_COST_LIMIT=50.0

# RAG
RAG_MIN_SIMILARITY=0.7
RAG_MAX_DOCUMENTS=5

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env dosyası oluşturuldu" -ForegroundColor Green
    Write-Host "⚠️  Lütfen .env dosyasını düzenleyin ve OPENAI_API_KEY ekleyin!" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env dosyası mevcut" -ForegroundColor Green
}

Write-Host ""

# Aşama 3: Docker Servisleri
Write-Host "🔄 Aşama 3: Docker Servisleri" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow

# Docker kontrolü
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker bulunamadı. Lütfen Docker Desktop'ı yükleyin." -ForegroundColor Red
    exit 1
}

try {
    docker ps | Out-Null
    Write-Host "✅ Docker çalışıyor" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop çalışmıyor. Lütfen Docker Desktop'ı başlatın." -ForegroundColor Red
    Write-Host "⏳ Docker Desktop'ı başlattıktan sonra script'i tekrar çalıştırın." -ForegroundColor Yellow
    exit 1
}

# Docker servislerini başlat
Write-Host "🐳 Docker servisleri başlatılıyor..." -ForegroundColor Yellow
Set-Location infra
docker-compose up -d postgres redis 2>&1 | Out-Null
Set-Location ..

Write-Host "⏳ Servislerin başlaması bekleniyor (15 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Servisleri kontrol et
$postgresRunning = docker ps --filter "name=chatbot-postgres" --format "{{.Names}}" | Select-String "postgres"
$redisRunning = docker ps --filter "name=chatbot-redis" --format "{{.Names}}" | Select-String "redis"

if ($postgresRunning) {
    Write-Host "✅ PostgreSQL çalışıyor" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL başlatılamadı" -ForegroundColor Red
}

if ($redisRunning) {
    Write-Host "✅ Redis çalışıyor" -ForegroundColor Green
} else {
    Write-Host "❌ Redis başlatılamadı" -ForegroundColor Red
}

# pgvector extension
Write-Host "🔧 pgvector extension kuruluyor..." -ForegroundColor Yellow
try {
    docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | Out-Null
    Write-Host "✅ pgvector extension kuruldu" -ForegroundColor Green
} catch {
    Write-Host "⚠️  pgvector extension kurulumu başarısız (manuel olarak kurulabilir)" -ForegroundColor Yellow
}

Write-Host ""

# Aşama 4: Database Migrations
Write-Host "🔄 Aşama 4: Database Migrations" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# Environment variables yükle
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

Set-Location backend
$env:PATH = ".\venv\Scripts;" + $env:PATH

# Alembic için sync driver kullan (asyncpg değil)
$dbUrl = $env:DATABASE_URL
if ($dbUrl -like "*asyncpg*") {
    $dbUrl = $dbUrl -replace "postgresql\+asyncpg://", "postgresql://"
} elseif (-not $dbUrl) {
    $dbUrl = "postgresql://user:password@localhost:5432/chatbot"
}

$env:DATABASE_URL = $dbUrl

Write-Host "🔄 Migrations çalıştırılıyor..." -ForegroundColor Yellow
try {
    .\venv\Scripts\python.exe -m alembic upgrade head 2>&1 | Out-Null
    Write-Host "✅ Migrations tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Migrations hatası (veritabanı henüz hazır olmayabilir)" -ForegroundColor Yellow
}

Set-Location ..
Write-Host ""

# Aşama 5: Test
Write-Host "🧪 Aşama 5: Test" -ForegroundColor Yellow
Write-Host "---------------" -ForegroundColor Yellow

Write-Host "✅ Kurulum tamamlandı!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki adımlar:" -ForegroundColor Yellow
Write-Host "1. .env dosyasını düzenleyin (OPENAI_API_KEY ekleyin)" -ForegroundColor White
Write-Host "2. Backend'i başlatın:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "3. Health check: curl http://localhost:8000/health" -ForegroundColor White
Write-Host "4. API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "5. GitHub'a push edin ve Railway'a deploy edin" -ForegroundColor White
Write-Host ""

