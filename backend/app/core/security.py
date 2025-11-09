"""
Security Utilities: JWT, OTP, PII Redaction, Rate Limiting
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import re
import redis.asyncio as redis
from functools import wraps

from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
security = HTTPBearer()

# Redis for OTP and rate limiting
redis_client: Optional[redis.Redis] = None


async def get_redis():
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return {"user_id": user_id, "role": payload.get("role", "user")}


def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


async def generate_otp(user_id: str) -> str:
    """Generate OTP for Telegram authentication"""
    otp = secrets.token_hex(settings.OTP_LENGTH // 2)[:settings.OTP_LENGTH].upper()
    redis_conn = await get_redis()
    key = f"otp:{user_id}"
    await redis_conn.setex(key, settings.OTP_TTL, otp)
    return otp


async def verify_otp(user_id: str, otp: str) -> bool:
    """Verify OTP"""
    redis_conn = await get_redis()
    key = f"otp:{user_id}"
    stored_otp = await redis_conn.get(key)
    if stored_otp and stored_otp == otp:
        await redis_conn.delete(key)
        return True
    return False


class PIIRedactor:
    """PII (Personally Identifiable Information) Redaction"""
    
    PATTERNS = [
        (r'\b\d{11}\b', '[TC_NO_REDACTED]'),  # Turkish TC No
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_NO_REDACTED]'),  # Credit card
        (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL_REDACTED]'),  # Email
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),  # SSN
        (r'\b\d{10,11}\b', '[PHONE_REDACTED]'),  # Phone
    ]
    
    @classmethod
    def redact_text(cls, text: str) -> str:
        """Redact PII from text"""
        result = text
        for pattern, replacement in cls.PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result


async def rate_limit(key: str, limit: int, window: int):
    """Rate limiting using Redis"""
    redis_conn = await get_redis()
    current = await redis_conn.incr(key)
    if current == 1:
        await redis_conn.expire(key, window)
    if current > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


def require_role(required_roles: list):
    """Decorator for role-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user or current_user.get("role") not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

