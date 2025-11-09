# ✅ Deployment Checklist

## 📋 Railway Deployment Öncesi Kontrol Listesi

### Git ve GitHub
- [ ] Git repository oluşturuldu
- [ ] Tüm dosyalar commit edildi
- [ ] GitHub repository oluşturuldu
- [ ] GitHub'a push edildi
- [ ] GitHub Secrets ayarlandı (opsiyonel)

### Kod Hazırlığı
- [ ] Backend kodları hazır
- [ ] Frontend kodları hazır
- [ ] Database migrations hazır
- [ ] Railway configuration dosyaları hazır
  - [ ] `railway.json`
  - [ ] `Procfile`
  - [ ] `nixpacks.toml`
  - [ ] `railway.toml`

### Environment Variables
- [ ] `OPENAI_API_KEY` hazır
- [ ] `TELEGRAM_BOT_TOKEN` hazır (8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8)
- [ ] `SECRET_KEY` hazır
- [ ] `JWT_SECRET_KEY` hazır

### Railway Setup
- [ ] Railway hesabı oluşturuldu
- [ ] Railway'de proje oluşturuldu
- [ ] GitHub repository bağlandı
- [ ] PostgreSQL plugin eklendi
- [ ] Redis plugin eklendi
- [ ] pgvector extension kuruldu
- [ ] Environment variables ayarlandı

### Deployment
- [ ] Build başarılı
- [ ] Deploy başarılı
- [ ] Health check çalışıyor
- [ ] API docs erişilebilir
- [ ] Telegram webhook ayarlandı
- [ ] Bot test edildi

---

## 🚀 Hızlı Deployment Komutları

### 1. GitHub'a Push

```powershell
# Remote ekle (YOUR_USERNAME'i değiştirin)
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git

# Branch'i main yap
git branch -M main

# Push et
git push -u origin main
```

### 2. Railway'de Proje Oluştur

1. Railway'a git: https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Repository'yi seç
4. Deploy!

### 3. PostgreSQL ve Redis Ekle

1. "+ New" → "Database" → "Add PostgreSQL"
2. "+ New" → "Database" → "Add Redis"
3. PostgreSQL'de pgvector extension kur:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 4. Environment Variables Ayarla

Railway dashboard → Backend service → Variables:

```env
OPENAI_API_KEY=sk-your-key
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

### 5. Telegram Webhook Ayarla

```powershell
$webhookUrl = "https://your-app.railway.app/v1/telegram/webhook"
curl -X POST $webhookUrl/../set-webhook -H "Content-Type: application/json" -d "{\"webhook_url\": \"$webhookUrl\"}"
```

---

## 📚 İlgili Dokümantasyon

- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Detaylı Railway deployment
- [GITHUB_PUSH.md](GITHUB_PUSH.md) - GitHub'a push rehberi
- [DEPLOYMENT.md](DEPLOYMENT.md) - Genel deployment rehberi

---

## 🎉 Başarılar!

Tüm checklist'i tamamladıktan sonra, sistem production'da çalışıyor olacak!

**İyi çalışmalar! 🚀**

