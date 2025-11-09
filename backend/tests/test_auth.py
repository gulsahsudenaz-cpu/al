"""
Authentication Tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

client = TestClient(app)


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login"""
    # Create a test user
    async with AsyncSessionLocal() as db:
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("testpass123"),
            role=UserRole.USER,
            is_active=True
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
    
    # Test login
    response = client.post(
        "/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/v1/auth/login",
        json={"username": "nonexistent", "password": "wrongpass"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user():
    """Test login with inactive user"""
    # Create an inactive user
    async with AsyncSessionLocal() as db:
        test_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=hash_password("testpass123"),
            role=UserRole.USER,
            is_active=False
        )
        db.add(test_user)
        await db.commit()
    
    # Test login
    response = client.post(
        "/v1/auth/login",
        json={"username": "inactiveuser", "password": "testpass123"}
    )
    assert response.status_code == 403


def test_get_current_user_without_token():
    """Test getting current user without token"""
    response = client.get("/v1/auth/me")
    assert response.status_code == 403


def test_get_current_user_with_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

