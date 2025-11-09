"""
Create Initial Admin User
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import init_db, AsyncSessionLocal
from app.core.security import hash_password, create_access_token
from app.models.user import User  # TODO: Create User model


async def create_admin():
    """Create initial admin user"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        # TODO: Implement user creation
        print("Admin user creation - TODO: Implement User model")
        
        # For now, just print token
        token = create_access_token(data={"sub": "admin", "role": "admin"})
        print(f"Admin token: {token}")


if __name__ == "__main__":
    asyncio.run(create_admin())

