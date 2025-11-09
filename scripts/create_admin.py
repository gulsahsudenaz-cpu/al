"""
Create Initial Admin User
"""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import init_db, AsyncSessionLocal
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole


async def create_admin(username: str = "admin", password: str = "admin123", email: str = "admin@example.com"):
    """Create initial admin user"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.username == username)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User '{username}' already exists!")
            token = create_access_token(
                data={"sub": str(existing_user.id), "username": existing_user.username, "role": existing_user.role.value}
            )
            print(f"Admin token: {token}")
            return
        
        # Create admin user
        hashed_password = hash_password(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ Admin user '{username}' created successfully!")
        token = create_access_token(
            data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role.value}
        )
        print(f"Admin token: {token}")


if __name__ == "__main__":
    import os
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    asyncio.run(create_admin(username, password, email))

