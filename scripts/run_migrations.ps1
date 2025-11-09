# Run Migrations Script - Windows PowerShell
# Database migrations çalıştırır

Write-Host "🗄️  Database Migrations Çalıştırılıyor..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# .env dosyası kontrolü
if (-not (Test-Path "..\.env")) {
    Write-Host "❌ .env dosyası bulunamadı. Root dizinde .env dosyası oluşturun." -ForegroundColor Red
    exit 1
}

# Backend dizinine git
Set-Location backend

# Virtual environment kontrolü
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment bulunamadı. Önce setup script'ini çalıştırın." -ForegroundColor Red
    exit 1
}

# Environment variables yükle
Write-Host "📝 Environment variables yükleniyor..." -ForegroundColor Yellow
Get-Content "..\.env" | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}
Write-Host "✅ Environment variables yüklendi" -ForegroundColor Green

# Alembic için sync driver (asyncpg değil)
$dbUrl = $env:DATABASE_URL
if ($dbUrl -like "*asyncpg*") {
    $dbUrl = $dbUrl -replace "postgresql\+asyncpg://", "postgresql://"
}
$env:DATABASE_URL = $dbUrl

Write-Host "🔄 Migrations çalıştırılıyor..." -ForegroundColor Yellow
try {
    .\venv\Scripts\python.exe -m alembic upgrade head
    Write-Host "✅ Migrations tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "❌ Migrations hatası:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "✅ Database migrations tamamlandı!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki adım: Backend'i başlatın" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host ""

