# 🤖 Telegram Bot Token Kurulumu

## ✅ Token Yapılandırması Tamamlandı

Telegram bot token'ınız hazır:
- **Bot Token**: `8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8`
- **Bot Username**: @Sohbet_Admin_Bot
- **Admin User**: mzengin (ID: 5874850928)

## 📝 .env Dosyasına Token Ekleyin

`.env` dosyasını açın ve şu satırı ekleyin veya güncelleyin:

```env
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
```

**Manuel Olarak:**

```powershell
# .env dosyasını açın
notepad .env

# Şu satırı ekleyin veya güncelleyin:
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8

# Dosyayı kaydedin
```

## 🚀 Sonraki Adımlar

### 1. Backend'i Başlatın

```powershell
.\scripts\start_backend.ps1
```

### 2. Webhook'u Ayarlayın

Backend çalışırken, webhook'u ayarlayın:

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

### 3. Webhook Bilgisini Kontrol Edin

```powershell
curl http://localhost:8000/v1/telegram/webhook-info
```

### 4. Bot'a Mesaj Gönderin

Telegram'da @Sohbet_Admin_Bot'a mesaj gönderin ve yanıt alıp almadığını kontrol edin.

## 📚 Daha Fazla Bilgi

- [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) - Detaylı Telegram kurulum rehberi
- [SONRAKI_ADIMLAR.md](SONRAKI_ADIMLAR.md) - Sonraki adımlar

## 🎉 Hazırsınız!

Telegram bot token'ı yapılandırıldı. Şimdi backend'i başlatın ve webhook'u ayarlayın!

