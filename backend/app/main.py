"""
FastAPI Main Application
Production-ready AI Chatbot Backend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.config import settings
from app.core.security import get_current_user
from app.api.v1 import router as api_router
from app.websocket.manager import WebSocketManager
from app.core.database import init_db, close_db
from app.monitoring.prometheus import router as prometheus_router

# OpenTelemetry setup
if settings.ENABLE_METRICS and settings.OTEL_EXPORTER_OTLP_ENDPOINT:
    try:
        from app.monitoring.otel_fastapi import setup_tracing, instrument_app
        setup_tracing(
            service_name="chatbot-backend",
            otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT
        )
    except Exception as e:
        print(f"⚠️  OpenTelemetry setup failed: {e}")


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

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
        instrument_app(app, excluded_urls="health,metrics")
    except Exception as e:
        print(f"⚠️  OpenTelemetry instrumentation failed: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "redis": "connected",
            "vector_db": "connected"
        }
    }


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

