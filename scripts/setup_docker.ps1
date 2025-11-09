# Docker Setup Script - Windows PowerShell
# Docker servislerini başlatmak için kullanılır

Write-Host "🐳 Docker Servisleri Başlatılıyor..." -ForegroundColor Green
Write-Host ""

# Docker kontrolü
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker bulunamadı. Lütfen Docker Desktop'ı yükleyin." -ForegroundColor Red
    exit 1
}

# Docker Desktop kontrolü
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

# Servisleri başlat
Write-Host "🐳 PostgreSQL ve Redis başlatılıyor..." -ForegroundColor Yellow
docker-compose up -d postgres redis

# Servislerin başlamasını bekle
Write-Host "⏳ Servislerin başlaması bekleniyor (15 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

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

Write-Host ""
Write-Host "✅ Docker servisleri hazır!" -ForegroundColor Green
Write-Host ""

# Root dizine dön
Set-Location ..

