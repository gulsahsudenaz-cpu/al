# 🤖 Telegram Bot Kurulumu

## 📋 Genel Bakış

Telegram bot token'ınız yapılandırıldı:
- **Bot Token**: `8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8`
- **Bot Username**: @Sohbet_Admin_Bot
- **Admin User**: mzengin (ID: 5874850928)

## 🚀 Kurulum Adımları

### 1. .env Dosyasına Token Ekleyin

```powershell
# Script ile (önerilen)
.\scripts\setup_telegram.ps1 -BotToken "8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8"

# Veya manuel olarak .env dosyasını düzenleyin
notepad .env

# Şu satırı ekleyin veya güncelleyin:
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
```

### 2. Backend'i Başlatın

```powershell
# Backend'i başlat
.\scripts\start_backend.ps1

# Veya manuel olarak
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### 3. Webhook'u Ayarlayın

Backend çalışırken, webhook'u ayarlayın:

#### Lokal Test (ngrok kullanarak)

```powershell
# 1. ngrok'u indirin ve çalıştırın
# https://ngrok.com/download
ngrok http 8000

# 2. ngrok URL'ini alın (örn: https://abc123.ngrok.io)

# 3. Webhook'u ayarlayın
$webhookUrl = "https://abc123.ngrok.io/v1/telegram/webhook"
curl -X POST http://localhost:8000/v1/telegram/set-webhook `
  -H "Content-Type: application/json" `
  -d "{\"webhook_url\": \"$webhookUrl\"}"
```

#### Production (Railway deploy sonrası)

```powershell
# Railway URL'inizi kullanın
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"
curl -X POST https://your-app.railway.app/v1/telegram/set-webhook `
  -H "Content-Type: application/json" `
  -d "{\"webhook_url\": \"$webhookUrl\"}"
```

### 4. Webhook Bilgisini Kontrol Edin

```powershell
# Webhook bilgisini kontrol et
curl http://localhost:8000/v1/telegram/webhook-info

# Beklenen çıktı:
# {
#   "status": "success",
#   "webhook_info": {
#     "url": "https://...",
#     "has_custom_certificate": false,
#     "pending_update_count": 0
#   }
# }
```

## 🧪 Test Etme

### 1. Bot'a Mesaj Gönderin

1. Telegram'da @Sohbet_Admin_Bot'a mesaj gönderin
2. Bot yanıt vermeli

### 2. Logları Kontrol Edin

```powershell
# Backend loglarını kontrol edin
# Terminal'de backend çalışırken loglar görünecek
```

### 3. Database'i Kontrol Edin

```powershell
# Chat ve message kayıtlarını kontrol edin
# Database'de telegram chat'leri görünmeli
```

## 📱 Özellikler

### Desteklenen Mesaj Tipleri

- ✅ **Text Messages**: Metin mesajları
- ✅ **Photo Messages**: Fotoğraf mesajları (caption ile)
- ✅ **Document Messages**: Dosya mesajları
- ✅ **Voice Messages**: Ses mesajları (yakında)
- ✅ **Media Support**: Fotoğraf ve dosya desteği

### Özellikler

- ✅ **Two-way Communication**: İki yönlü iletişim
- ✅ **Media Support**: Medya desteği
- ✅ **OTP Authentication**: OTP kimlik doğrulama (yakında)
- ✅ **Admin Support**: Admin kullanıcı desteği
- ✅ **RAG Integration**: RAG sistemi entegrasyonu
- ✅ **LLM Integration**: LLM sistemi entegrasyonu

## 🔧 API Endpoints

### Webhook Endpoint

```
POST /v1/telegram/webhook
```

Telegram'dan gelen webhook'ları işler.

### Set Webhook

```
POST /v1/telegram/set-webhook
Body: {"webhook_url": "https://..."}
```

Webhook URL'ini ayarlar.

### Get Webhook Info

```
GET /v1/telegram/webhook-info
```

Webhook bilgisini getirir.

### Delete Webhook

```
DELETE /v1/telegram/delete-webhook
```

Webhook'u siler.

## 🛠️ Sorun Giderme

### Bot Yanıt Vermiyor

1. **Webhook Kontrolü:**
   ```powershell
   curl http://localhost:8000/v1/telegram/webhook-info
   ```

2. **Backend Logları:**
   - Backend loglarını kontrol edin
   - Hata mesajlarını kontrol edin

3. **Token Kontrolü:**
   - .env dosyasında token doğru mu?
   - Token geçerli mi?

### Webhook Ayarlanamıyor

1. **HTTPS Kontrolü:**
   - Webhook URL HTTPS olmalı
   - Lokal test için ngrok kullanın

2. **Backend Kontrolü:**
   - Backend çalışıyor mu?
   - Port 8000 açık mı?

3. **Firewall Kontrolü:**
   - Firewall webhook'u engelliyor mu?
   - Port 8000 açık mı?

### Media Mesajları İşlenmiyor

1. **File Size Kontrolü:**
   - Dosya boyutu limiti: 20MB
   - Büyük dosyalar işlenmeyebilir

2. **Media Processing:**
   - Media processing henüz tam olarak aktif değil
   - Yakında eklenecek

## 📚 İlgili Dokümantasyon

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Webhook Setup](https://core.telegram.org/bots/api#setwebhook)
- [Telegram Service](backend/app/services/telegram_service.py)
- [Telegram API Routes](backend/app/api/v1/telegram.py)

## 🎉 Başarılar!

Telegram bot'unuz hazır! Bot'a mesaj göndererek test edebilirsiniz.

**İyi çalışmalar! 🚀**

