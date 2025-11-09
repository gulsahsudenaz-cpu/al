# Start Backend Script - Windows PowerShell
# Backend'i başlatmak için kullanılır

Write-Host "🚀 Backend Başlatılıyor..." -ForegroundColor Green
Write-Host ""

# Backend dizinine git
Set-Location backend

# Virtual environment kontrolü
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment bulunamadı. Önce setup script'ini çalıştırın." -ForegroundColor Red
    exit 1
}

# Environment variables yükle
if (Test-Path "..\.env") {
    Write-Host "📝 Environment variables yükleniyor..." -ForegroundColor Yellow
    Get-Content "..\.env" | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "✅ Environment variables yüklendi" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env dosyası bulunamadı" -ForegroundColor Yellow
}

# Alembic için sync driver (asyncpg değil)
$dbUrl = $env:DATABASE_URL
if ($dbUrl -like "*asyncpg*") {
    $dbUrl = $dbUrl -replace "postgresql\+asyncpg://", "postgresql://"
    $env:DATABASE_URL = $dbUrl
}

# Virtual environment aktifleştir
Write-Host "🐍 Virtual environment aktifleştiriliyor..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Backend'i başlat
Write-Host "🚀 Backend başlatılıyor..." -ForegroundColor Yellow
Write-Host "📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app.main:app --reload --port 8000

