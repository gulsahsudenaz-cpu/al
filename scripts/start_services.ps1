# Start Services Script - Windows PowerShell
# Docker servislerini başlatır ve hazırlar

Write-Host "🐳 Docker Servislerini Başlatılıyor..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

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

# Infra dizinine git
Set-Location infra

# Servisleri kontrol et
$postgresRunning = docker ps --filter "name=chatbot-postgres" --format "{{.Names}}" | Select-String "postgres"
$redisRunning = docker ps --filter "name=chatbot-redis" --format "{{.Names}}" | Select-String "redis"

if (-not $postgresRunning -or -not $redisRunning) {
    Write-Host "🐳 PostgreSQL ve Redis başlatılıyor..." -ForegroundColor Yellow
    docker-compose up -d postgres redis
    
    Write-Host "⏳ Servislerin başlaması bekleniyor (15 saniye)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
} else {
    Write-Host "✅ Docker servisleri zaten çalışıyor" -ForegroundColor Green
}

# Servisleri kontrol et
Write-Host "🔍 Servisler kontrol ediliyor..." -ForegroundColor Yellow
docker-compose ps

# pgvector extension
Write-Host "🔧 pgvector extension kuruluyor..." -ForegroundColor Yellow
try {
    docker exec chatbot-postgres psql -U user -d chatbot -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | Out-Null
    Write-Host "✅ pgvector extension kuruldu" -ForegroundColor Green
} catch {
    Write-Host "⚠️  pgvector extension kurulumu başarısız (manuel olarak kurulabilir)" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "✅ Docker servisleri hazır!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki adım: Database migrations çalıştırın" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   alembic upgrade head" -ForegroundColor Cyan
Write-Host ""

