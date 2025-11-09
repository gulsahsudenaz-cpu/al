"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis
import time
from typing import Callable, Optional

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Redis client for rate limiting
_redis_rate_limit: Optional[redis.Redis] = None


async def get_redis_rate_limit():
    """Get Redis client for rate limiting"""
    global _redis_rate_limit
    if _redis_rate_limit is None:
        _redis_rate_limit = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_rate_limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID from token)
        client_id = self.get_client_id(request)
        current = 0
        
        # Check rate limit
        try:
            redis_client = await get_redis_rate_limit()
            key = f"rate_limit:{client_id}:{int(time.time() / self.period)}"
            current = await redis_client.incr(key)
            
            if current == 1:
                await redis_client.expire(key, self.period)
            
            if current > self.calls:
                logger.warning("Rate limit exceeded", client_id=client_id, current=current, limit=self.calls)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.calls} requests per {self.period} seconds"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Rate limit check error", error=str(e), exc_info=True)
            # Continue if Redis fails (graceful degradation)
            current = 0
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - current))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() / self.period) * self.period + self.period)
        
        return response
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, decode JWT to get user ID
            # For now, use IP address
            pass
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return client_ip

