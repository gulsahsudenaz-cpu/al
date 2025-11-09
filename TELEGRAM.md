# 🤖 Telegram Bot Kurulumu

## 📋 Genel Bakış

Telegram bot token'ınız:
- **Bot Token**: `8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8`
- **Bot Username**: @Sohbet_Admin_Bot
- **Admin User**: mzengin (ID: 5874850928)

## 🚀 Kurulum

### 1. .env Dosyasına Token Ekleyin

```powershell
# .env dosyasını açın
notepad .env

# Şu satırı ekleyin veya güncelleyin:
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
```

### 2. Backend'i Başlatın

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### 3. Webhook'u Ayarlayın

#### Lokal Test (ngrok)

```powershell
# 1. ngrok'u indirin ve çalıştırın
# https://ngrok.com/download
ngrok http 8000

# 2. ngrok URL'ini alın (örn: https://abc123.ngrok.io)

# 3. Webhook'u ayarlayın
$webhookUrl = "https://abc123.ngrok.io/v1/telegram/webhook"
curl -X POST http://localhost:8000/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

#### Production (Railway)

```powershell
# Railway URL'inizi kullanın
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"
curl -X POST https://your-app.railway.app/v1/telegram/set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

### 4. Webhook Bilgisini Kontrol Edin

```powershell
curl http://localhost:8000/v1/telegram/webhook-info
```

### 5. Bot'a Mesaj Gönderin

Telegram'da @Sohbet_Admin_Bot'a mesaj gönderin ve yanıt alıp almadığını kontrol edin.

## 📱 Özellikler

- ✅ Text Messages
- ✅ Photo Messages
- ✅ Document Messages
- ✅ Voice Messages
- ✅ Two-way Communication
- ✅ RAG Integration
- ✅ LLM Integration

## 🔧 API Endpoints

- `POST /v1/telegram/webhook` - Webhook endpoint
- `POST /v1/telegram/set-webhook` - Webhook ayarlama
- `GET /v1/telegram/webhook-info` - Webhook bilgisi
- `DELETE /v1/telegram/delete-webhook` - Webhook silme

## 🆘 Sorun Giderme

### Bot Yanıt Vermiyor
1. Webhook kontrolü: `curl http://localhost:8000/v1/telegram/webhook-info`
2. Backend loglarını kontrol edin
3. Token kontrolü: .env dosyasında token doğru mu?

### Webhook Ayarlanamıyor
1. HTTPS kontrolü: Webhook URL HTTPS olmalı
2. Backend kontrolü: Backend çalışıyor mu?
3. Firewall kontrolü: Port 8000 açık mı?

