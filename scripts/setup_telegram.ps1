# Telegram Bot Setup Script - Windows PowerShell
# Telegram bot token'ını yapılandırmak ve webhook'u ayarlamak için

param(
    [Parameter(Mandatory=$true)]
    [string]$BotToken,
    
    [Parameter(Mandatory=$false)]
    [string]$WebhookUrl = ""
)

Write-Host "🤖 Telegram Bot Setup" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green
Write-Host ""

# .env dosyasını kontrol et
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env dosyası bulunamadı. Önce .env dosyasını oluşturun." -ForegroundColor Red
    exit 1
}

# .env dosyasını oku
$envContent = Get-Content ".env" -Raw

# TELEGRAM_BOT_TOKEN'ı güncelle veya ekle
if ($envContent -match "TELEGRAM_BOT_TOKEN=") {
    $envContent = $envContent -replace "TELEGRAM_BOT_TOKEN=.*", "TELEGRAM_BOT_TOKEN=$BotToken"
    Write-Host "✅ TELEGRAM_BOT_TOKEN güncellendi" -ForegroundColor Green
} else {
    $envContent += "`n# Telegram`nTELEGRAM_BOT_TOKEN=$BotToken`n"
    Write-Host "✅ TELEGRAM_BOT_TOKEN eklendi" -ForegroundColor Green
}

# Webhook URL varsa ekle
if ($WebhookUrl -and $WebhookUrl -ne "") {
    if ($envContent -match "TELEGRAM_WEBHOOK_URL=") {
        $envContent = $envContent -replace "TELEGRAM_WEBHOOK_URL=.*", "TELEGRAM_WEBHOOK_URL=$WebhookUrl"
        Write-Host "✅ TELEGRAM_WEBHOOK_URL güncellendi" -ForegroundColor Green
    } else {
        $envContent += "TELEGRAM_WEBHOOK_URL=$WebhookUrl`n"
        Write-Host "✅ TELEGRAM_WEBHOOK_URL eklendi" -ForegroundColor Green
    }
}

# .env dosyasını kaydet
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "✅ Telegram bot token yapılandırıldı!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Sonraki adımlar:" -ForegroundColor Yellow
Write-Host "1. Backend'i başlatın: .\scripts\start_backend.ps1" -ForegroundColor White
Write-Host "2. Webhook'u ayarlayın (backend çalışırken):" -ForegroundColor White
Write-Host "   curl -X POST http://localhost:8000/v1/telegram/set-webhook -H 'Content-Type: application/json' -d '{\"webhook_url\": \"https://yourdomain.com/v1/telegram/webhook\"}'" -ForegroundColor Cyan
Write-Host "3. Webhook bilgisini kontrol edin:" -ForegroundColor White
Write-Host "   curl http://localhost:8000/v1/telegram/webhook-info" -ForegroundColor Cyan
Write-Host ""

