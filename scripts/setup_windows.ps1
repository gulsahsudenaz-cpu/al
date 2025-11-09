# Windows PowerShell Setup Script
# AI Chatbot System - Automated Setup

Write-Host "🚀 AI Chatbot System - Windows Setup" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Check Docker
Write-Host "🔍 Docker kontrol ediliyor..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker mevcut: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker bulunamadı. Lütfen Docker Desktop'ı yükleyin ve başlatın." -ForegroundColor Red
    exit 1
}

# Check Docker Desktop
Write-Host "🔍 Docker Desktop kontrol ediliyor..." -ForegroundColor Yellow
try {
    $dockerPs = docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker Desktop çalışmıyor. Lütfen Docker Desktop'ı başlatın." -ForegroundColor Red
        Write-Host "⏳ Docker Desktop'ın başlamasını bekleyin ve script'i tekrar çalıştırın." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Docker Desktop çalışıyor" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop çalışmıyor. Lütfen Docker Desktop'ı başlatın." -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "🔍 Python kontrol ediliyor..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python mevcut: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python bulunamadı. Lütfen Python 3.11+ yükleyin." -ForegroundColor Red
    exit 1
}

# Create .env file
Write-Host "📝 .env dosyası kontrol ediliyor..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env dosyası mevcut" -ForegroundColor Green
} else {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env dosyası oluşturuldu (.env.example'dan)" -ForegroundColor Green
        Write-Host "⚠️  Lütfen .env dosyasını düzenleyin ve OPENAI_API_KEY ekleyin" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  .env.example dosyası bulunamadı" -ForegroundColor Yellow
    }
}

# Create virtual environment
Write-Host "📦 Virtual environment kontrol ediliyor..." -ForegroundColor Yellow
if (Test-Path "backend\venv") {
    Write-Host "✅ Virtual environment mevcut" -ForegroundColor Green
} else {
    Write-Host "📦 Virtual environment oluşturuluyor..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    Set-Location ..
    Write-Host "✅ Virtual environment oluşturuldu" -ForegroundColor Green
}

# Install dependencies
Write-Host "📦 Dependencies yükleniyor..." -ForegroundColor Yellow
Set-Location backend
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt --no-cache-dir
Set-Location ..
Write-Host "✅ Dependencies yüklendi" -ForegroundColor Green

# Start Docker services
Write-Host "🐳 Docker servisleri başlatılıyor..." -ForegroundColor Yellow
Set-Location infra
docker-compose up -d postgres redis
Set-Location ..
Write-Host "⏳ Servislerin başlaması bekleniyor (10 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check services
Write-Host "🔍 Servisler kontrol ediliyor..." -ForegroundColor Yellow
$postgresStatus = docker ps --filter "name=chatbot-postgres" --format "{{.Status}}"
$redisStatus = docker ps --filter "name=chatbot-redis" --format "{{.Status}}"

if ($postgresStatus) {
    Write-Host "✅ PostgreSQL: $postgresStatus" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL başlatılamadı" -ForegroundColor Red
}

if ($redisStatus) {
    Write-Host "✅ Redis: $redisStatus" -ForegroundColor Green
} else {
    Write-Host "❌ Redis başlatılamadı" -ForegroundColor Red
}

# Create pgvector extension
Write-Host "🔧 pgvector extension kuruluyor..." -ForegroundColor Yellow
try {
    docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | Out-Null
    Write-Host "✅ pgvector extension kuruldu" -ForegroundColor Green
} catch {
    Write-Host "⚠️  pgvector extension kurulumu başarısız (manuel olarak kurulabilir)" -ForegroundColor Yellow
}

# Run migrations
Write-Host "🔄 Database migrations çalıştırılıyor..." -ForegroundColor Yellow
Set-Location backend
$env:PATH = ".\venv\Scripts;" + $env:PATH
.\venv\Scripts\python.exe -m alembic upgrade head
Set-Location ..
Write-Host "✅ Migrations tamamlandı" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Kurulum tamamlandı!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki adımlar:" -ForegroundColor Yellow
Write-Host "1. .env dosyasını düzenleyin (OPENAI_API_KEY, SECRET_KEY, etc.)" -ForegroundColor White
Write-Host "2. Backend'i başlatın: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "3. Health check: curl http://localhost:8000/health" -ForegroundColor White
Write-Host "4. API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

