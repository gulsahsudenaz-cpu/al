# 📤 GitHub'a Push Etme Rehberi

## 🎯 Adım Adım GitHub'a Push

### Adım 1: GitHub Repository Oluşturun

1. **GitHub'a gidin:**
   - https://github.com/new

2. **Repository oluşturun:**
   - Repository name: `chatbot` (veya istediğiniz ad)
   - Description: "AI Chatbot System with RAG, LLM, Telegram"
   - Public veya Private seçin
   - **ÖNEMLİ:** README, .gitignore, license **EKLEMEYIN** (zaten var)

3. **Repository oluştur butonuna tıklayın**

---

### Adım 2: GitHub Remote Ekleyin

```powershell
# YOUR_USERNAME'i GitHub kullanıcı adınızla değiştirin
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git

# Remote'u kontrol edin
git remote -v
```

**Beklenen çıktı:**
```
origin  https://github.com/YOUR_USERNAME/chatbot.git (fetch)
origin  https://github.com/YOUR_USERNAME/chatbot.git (push)
```

---

### Adım 3: Branch'i Main Olarak Ayarlayın

```powershell
# Mevcut branch'i kontrol edin
git branch

# Branch'i main olarak ayarlayın
git branch -M main
```

---

### Adım 4: GitHub'a Push Edin

```powershell
# İlk push
git push -u origin main
```

**Beklenen çıktı:**
```
Enumerating objects: 150, done.
Counting objects: 100% (150/150), done.
Delta compression using up to 8 threads
Compressing objects: 100% (120/120), done.
Writing objects: 100% (150/150), 45.23 KiB | 2.31 MiB/s, done.
Total 150 (delta 30), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (30/30), done.
To https://github.com/YOUR_USERNAME/chatbot.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

### Adım 5: GitHub'da Kontrol Edin

1. **Repository'yi açın:**
   - https://github.com/YOUR_USERNAME/chatbot

2. **Dosyaları kontrol edin:**
   - Tüm dosyalar görünmeli
   - README.md görünmeli
   - Backend, frontend, infra klasörleri görünmeli

---

## 🔐 GitHub Secrets (Opsiyonel)

CI/CD için GitHub Secrets ayarlayın:

1. **Repository Settings → Secrets and variables → Actions**
2. **"New repository secret" butonuna tıklayın**
3. **Şu secrets'ları ekleyin:**

```
OPENAI_API_KEY=sk-your-openai-api-key
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
TELEGRAM_BOT_TOKEN=8033290671:AAHHqhVnDdbIiou4FsO0ACdq7-EdsgW0of8
```

---

## ✅ Kontrol Listesi

- [ ] GitHub repository oluşturuldu
- [ ] GitHub remote eklendi
- [ ] Branch main olarak ayarlandı
- [ ] GitHub'a push edildi
- [ ] Repository'de dosyalar görünüyor
- [ ] GitHub Secrets ayarlandı (opsiyonel)

---

## 🚀 Sonraki Adım

GitHub'a push ettikten sonra:
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Railway deployment rehberi

---

## 🆘 Sorun Giderme

### Remote Zaten Var

```powershell
# Remote'u kontrol edin
git remote -v

# Eğer farklı bir remote varsa, önce kaldırın
git remote remove origin

# Sonra yeni remote ekleyin
git remote add origin https://github.com/YOUR_USERNAME/chatbot.git
```

### Push Hatası

```powershell
# Önce pull edin (eğer remote'da değişiklik varsa)
git pull origin main --allow-unrelated-histories

# Sonra push edin
git push -u origin main
```

### Authentication Hatası

```powershell
# GitHub Personal Access Token kullanın
# https://github.com/settings/tokens

# Token ile push edin
git push -u origin main
# Username: YOUR_USERNAME
# Password: YOUR_PERSONAL_ACCESS_TOKEN
```

---

## 🎉 Başarılar!

GitHub'a push tamamlandı! Artık Railway'a deploy edebilirsiniz.

**İyi çalışmalar! 🚀**

