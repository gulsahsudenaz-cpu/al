# 📤 GitHub'a Push Rehberi

## Adım Adım GitHub'a Yükleme

### 1. Git Repository Hazırlığı

Eğer henüz git repository yoksa:

```bash
cd c:\Users\BTA\Desktop\chatbot
git init
```

### 2. Tüm Dosyaları Ekle

```bash
git add .
```

### 3. Commit Yap

```bash
git commit -m "feat: Production-ready AI chatbot with RAG, LLM, media processing, and multi-channel support"
```

### 4. Branch'i Main Yap

```bash
git branch -M main
```

### 5. Remote Repository Ekle

```bash
git remote add origin https://github.com/gulsahsudenaz-cpu/al.git
```

### 6. GitHub'a Push Yap

```bash
git push -u origin main
```

## 🔐 GitHub Authentication

Eğer authentication hatası alırsanız:

### Personal Access Token Kullan

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "Generate new token (classic)"
3. Scopes: `repo` (tüm repo yetkileri)
4. Token'ı kopyala
5. Push yaparken password yerine token kullan:

```bash
git push -u origin main
# Username: gulsahsudenaz-cpu
# Password: [your-personal-access-token]
```

### SSH Key Kullan (Önerilen)

1. SSH key oluştur:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. SSH key'i GitHub'a ekle:
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - Public key'i ekle (`~/.ssh/id_ed25519.pub`)

3. Remote URL'yi SSH ile değiştir:
```bash
git remote set-url origin git@github.com:gulsahsudenaz-cpu/al.git
```

4. Push yap:
```bash
git push -u origin main
```

## 🔄 Sonraki Push'lar

Sonraki değişiklikler için:

```bash
git add .
git commit -m "feat: your change description"
git push
```

## ✅ Kontrol

GitHub'da repository'nin güncellendiğini kontrol edin:

https://github.com/gulsahsudenaz-cpu/al

## 🚂 Railway'e Bağlama

GitHub'a push yaptıktan sonra:

1. Railway'a git: https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Repository'yi seç: `gulsahsudenaz-cpu/al`
4. Railway otomatik olarak deploy edecek

## 📝 Notlar

- `.env` dosyası `.gitignore`'da olduğu için push edilmeyecek (güvenlik)
- Sensitive bilgileri GitHub'a push etmeyin
- Railway'de environment variables'ı manuel olarak ayarlayın

---

**GitHub'a başarıyla push yaptıktan sonra Railway deployment'a geçebilirsiniz! 🚀**

