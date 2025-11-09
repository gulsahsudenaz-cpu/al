"""
WebSocket Manager - Real-time Chat with Heartbeat and Deduplication
"""
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import time
import hashlib
import redis.asyncio as redis
from datetime import datetime, timedelta

from app.config import settings
from app.services.orchestrator import OrchestratorService


class WebSocketManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.orchestrator = OrchestratorService()
    
    async def get_redis(self):
        """Get Redis client"""
        if self.redis_client is None:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis_client
    
    async def connect(self, websocket: WebSocket, room_key: Optional[str] = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        room_key = room_key or "default"
        
        if room_key not in self.active_connections:
            self.active_connections[room_key] = set()
        self.active_connections[room_key].add(websocket)
        
        self.connection_metadata[websocket] = {
            "room_key": room_key,
            "connected_at": datetime.utcnow(),
            "last_ping": time.time(),
            "message_hash": set()
        }
        
        # Send welcome message
        await self.send_personal_message({
            "type": "server.message",
            "message": "Bağlantı kuruldu. Size nasıl yardımcı olabilirim?",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket, room_key: Optional[str] = None):
        """Remove WebSocket connection"""
        room_key = room_key or "default"
        if room_key in self.active_connections:
            self.active_connections[room_key].discard(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict, room_key: str):
        """Broadcast message to all connections in a room"""
        if room_key not in self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections[room_key]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected connections
        for ws in disconnected:
            self.disconnect(ws, room_key)
    
    async def handle_message(self, websocket: WebSocket, data: dict):
        """Handle incoming WebSocket message"""
        message_type = data.get("type")
        metadata = self.connection_metadata.get(websocket, {})
        room_key = metadata.get("room_key", "default")
        
        # Handle ping
        if message_type == "ping":
            metadata["last_ping"] = time.time()
            await self.send_personal_message({
                "type": "pong",
                "timestamp": data.get("timestamp", time.time())
            }, websocket)
            return
        
        # Handle client message
        if message_type == "client.message":
            text = data.get("text", "")
            if not text:
                return
            
            # Deduplication check
            try:
                message_hash = hashlib.md5(f"{text}:{time.time() // 300}".encode()).hexdigest()
                redis_conn = await self.get_redis()
                dedup_key = f"ws:dedup:{message_hash}"
                
                if await redis_conn.exists(dedup_key):
                    return  # Duplicate message
                
                await redis_conn.setex(dedup_key, 300, "1")  # 5 minutes TTL
            except Exception as e:
                # If Redis fails, continue without deduplication
                print(f"Redis deduplication error: {e}")
            
            # Send typing indicator
            await self.send_personal_message({
                "type": "server.typing",
                "is_typing": True
            }, websocket)
            
            # Process message through orchestrator
            try:
                response = await self.orchestrator.process_message(
                    text=text,
                    room_key=room_key,
                    websocket=websocket
                )
                
                # Send response
                await self.send_personal_message({
                    "type": "server.message",
                    "message": response.get("text", ""),
                    "sources": response.get("sources", []),
                    "context": response.get("context", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
                
            except Exception as e:
                await self.send_personal_message({
                    "type": "server.error",
                    "message": "Bir hata oluştu. Lütfen tekrar deneyin.",
                    "code": "PROCESSING_ERROR"
                }, websocket)
            
            finally:
                # Stop typing indicator
                await self.send_personal_message({
                    "type": "server.typing",
                    "is_typing": False
                }, websocket)
        
        # Update last ping
        metadata["last_ping"] = time.time()
    
    async def check_timeouts(self):
        """Check for idle connections and timeouts"""
        current_time = time.time()
        timeout_threshold = settings.WS_SESSION_TIMEOUT
        
        for websocket, metadata in list(self.connection_metadata.items()):
            last_ping = metadata.get("last_ping", 0)
            idle_time = current_time - last_ping
            
            if idle_time > timeout_threshold:
                # Send timeout warning
                await self.send_personal_message({
                    "type": "server.warning",
                    "message": "Bağlantı zaman aşımına uğradı"
                }, websocket)
                self.disconnect(websocket, metadata.get("room_key"))
            elif idle_time > settings.WS_IDLE_WARNING:
                # Send idle warning
                await self.send_personal_message({
                    "type": "server.warning",
                    "message": "Bağlantı yakında sonlanacak"
                }, websocket)

