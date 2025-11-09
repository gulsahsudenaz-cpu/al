"""Authentication Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import (
    create_access_token,
    verify_password,
    hash_password,
    generate_otp,
    verify_otp,
    get_current_user,
    rate_limit
)
from app.core.database import get_db
from app.models.user import User, UserRole
from app.config import settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class TelegramOTPRequest(BaseModel):
    user_id: str
    telegram_id: str


class TelegramOTPVerify(BaseModel):
    user_id: str
    otp: str


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint"""
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/telegram-otp/request")
async def request_telegram_otp(request: TelegramOTPRequest):
    """Request OTP for Telegram authentication"""
    await rate_limit(f"otp:request:{request.user_id}", limit=5, window=300)
    otp = await generate_otp(request.user_id)
    # TODO: Send OTP via Telegram
    return {"message": "OTP sent", "otp": otp}  # Remove otp in production


@router.post("/telegram-otp/verify")
async def verify_telegram_otp(request: TelegramOTPVerify):
    """Verify OTP and return access token"""
    is_valid = await verify_otp(request.user_id, request.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP"
        )
    
    access_token = create_access_token(data={"sub": request.user_id, "role": "user"})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

