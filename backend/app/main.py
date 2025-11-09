"""
FastAPI Main Application
Production-ready AI Chatbot Backend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import json

from app.config import settings
from app.core.security import get_current_user
from app.core.logging import setup_logging
from app.api.v1 import router as api_router
from app.websocket.manager import WebSocketManager
from app.core.database import init_db, close_db
from app.monitoring.prometheus import router as prometheus_router
from app.middleware.rate_limit import RateLimitMiddleware

# OpenTelemetry setup
if settings.ENABLE_METRICS and settings.OTEL_EXPORTER_OTLP_ENDPOINT:
    try:
        from app.monitoring.otel_fastapi import setup_tracing, instrument_app
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        setup_tracing(
            service_name="chatbot-backend",
            otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT
        )
        logger.info("OpenTelemetry tracing enabled", endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning("OpenTelemetry setup failed", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="AI Chatbot API",
    description="Production-ready AI Chatbot with RAG and LLM integration",
    version="2.0.0",
    lifespan=lifespan
)

# Setup logging
setup_logging(level="INFO" if not settings.DEBUG else "DEBUG", json_format=settings.DEBUG)

# Middleware - CORS Configuration
# In development (DEBUG=True), allow all origins for easier local testing
# In production, use configured origins
if settings.DEBUG:
    # Development: Allow all origins (including file:// protocol for local HTML files)
    # Note: JWT tokens are sent in Authorization header, so credentials=False is OK
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # JWT tokens in header don't require credentials
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    # Production: Use configured origins
    valid_origins = [
        origin.strip() 
        for origin in settings.CORS_ORIGINS 
        if origin and origin.strip() and not origin.strip().startswith("file://")
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=valid_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
if not settings.DEBUG:
    app.add_middleware(RateLimitMiddleware, calls=settings.MAX_MESSAGES_PER_MINUTE, period=60)

# WebSocket Manager
ws_manager = WebSocketManager()

# Routers
app.include_router(api_router, prefix="/v1")

# Prometheus metrics
if settings.ENABLE_METRICS:
    app.include_router(prometheus_router)

# Instrument FastAPI with OpenTelemetry
if settings.ENABLE_METRICS and settings.OTEL_EXPORTER_OTLP_ENDPOINT:
    try:
        from app.monitoring.otel_fastapi import instrument_app
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        instrument_app(app, excluded_urls="health,metrics")
        logger.info("OpenTelemetry instrumentation enabled")
    except Exception as e:
        logger = get_logger(__name__)
        logger.warning("OpenTelemetry instrumentation failed", error=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint with actual connection tests"""
    from app.core.database import engine
    from app.core.security import get_redis
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "services": {}
    }
    
    # Check database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"
        logger.warning("Database health check failed", error=str(e))
    
    # Check Redis connection
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["services"]["redis"] = "connected"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"
        logger.warning("Redis health check failed", error=str(e))
    
    # Vector DB uses same database, so it's included in database check
    health_status["services"]["vector_db"] = health_status["services"].get("database", "unknown")
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return Response(
        content=json.dumps(health_status),
        media_type="application/json",
        status_code=status_code
    )


@app.websocket("/v1/ws/chat")
async def websocket_endpoint(websocket: WebSocket, room_key: str = None):
    """WebSocket endpoint for real-time chat"""
    await ws_manager.connect(websocket, room_key)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room_key)


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info"
    )

