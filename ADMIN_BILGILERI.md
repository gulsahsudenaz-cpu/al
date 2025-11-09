# Admin Kullanıcı Bilgileri

## Varsayılan Admin Bilgileri

- **Kullanıcı Adı:** `admin`
- **Şifre:** `admin123`
- **Email:** `admin@example.com`

## Admin Kullanıcısı Oluşturma

### Yöntem 1: Script ile (Önerilen)

```bash
cd backend
python ../scripts/create_admin.py
```

Veya özel bilgilerle:

```bash
ADMIN_USERNAME=myadmin ADMIN_PASSWORD=mypassword python ../scripts/create_admin.py
```

### Yöntem 2: Manuel SQL ile

```sql
INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYx5YKQx5K2', -- 'admin123' şifresinin hash'i
    'admin',
    true,
    NOW(),
    NOW()
);
```

**Not:** Hash'i Python ile oluşturmak için:

```python
from app.core.security import hash_password
print(hash_password("admin123"))
```

### Yöntem 3: API ile (Backend çalışıyorsa)

```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

## Güvenlik Uyarısı

⚠️ **ÖNEMLİ:** Production ortamında mutlaka şifreyi değiştirin!

```bash
# Yeni şifre ile admin oluştur
ADMIN_USERNAME=admin ADMIN_PASSWORD=GüçlüŞifre123! python ../scripts/create_admin.py
```

## Şifre Değiştirme

Admin kullanıcısının şifresini değiştirmek için:

1. Backend'e bağlanın
2. Python shell açın:
   ```bash
   cd backend
   python
   ```
3. Şifreyi hash'leyin ve güncelleyin:
   ```python
   from app.core.security import hash_password
   from app.core.database import AsyncSessionLocal
   from app.models.user import User
   from sqlalchemy import select
   import asyncio
   
   async def update_password():
       async with AsyncSessionLocal() as db:
           result = await db.execute(select(User).where(User.username == "admin"))
           user = result.scalar_one_or_none()
           if user:
               user.hashed_password = hash_password("YeniŞifre123!")
               await db.commit()
               print("Şifre güncellendi!")
   
   asyncio.run(update_password())
   ```

