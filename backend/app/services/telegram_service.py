"""Telegram Bot Service"""
from typing import Dict, Optional, List
import httpx
import asyncio
from datetime import datetime

from app.config import settings
from app.services.orchestrator import OrchestratorService
from app.core.database import get_db
from app.models.chat import Chat
from app.models.message import Message
from sqlalchemy.ext.asyncio import AsyncSession


class TelegramService:
    """Telegram bot service with media support and OTP authentication"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        if self.bot_token:
            self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.api_url = None
        self.orchestrator = OrchestratorService()
    
    async def send_message(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: Optional[str] = "HTML",
        reply_to_message_id: Optional[int] = None
    ):
        """Send message to Telegram chat"""
        if not self.bot_token or not self.api_url:
            print("Telegram bot token not configured")
            return
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode
                }
                if reply_to_message_id:
                    payload["reply_to_message_id"] = reply_to_message_id
                
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return None
    
    async def send_photo(self, chat_id: int, photo_url: str, caption: Optional[str] = None):
        """Send photo to Telegram chat"""
        if not self.bot_token or not self.api_url:
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "chat_id": chat_id,
                    "photo": photo_url
                }
                if caption:
                    payload["caption"] = caption
                
                response = await client.post(
                    f"{self.api_url}/sendPhoto",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error sending Telegram photo: {e}")
            return None
    
    async def send_document(self, chat_id: int, document_url: str, caption: Optional[str] = None):
        """Send document to Telegram chat"""
        if not self.bot_token or not self.api_url:
            return
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "chat_id": chat_id,
                    "document": document_url
                }
                if caption:
                    payload["caption"] = caption
                
                response = await client.post(
                    f"{self.api_url}/sendDocument",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error sending Telegram document: {e}")
            return None
    
    async def send_typing(self, chat_id: int):
        """Send typing indicator to Telegram chat"""
        if not self.bot_token or not self.api_url:
            return
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{self.api_url}/sendChatAction",
                    json={"chat_id": chat_id, "action": "typing"}
                )
        except Exception as e:
            print(f"Error sending typing indicator: {e}")
    
    async def process_update(self, update: Dict, db: Optional[AsyncSession] = None):
        """Process Telegram update"""
        try:
            # Handle different update types
            message = update.get("message") or update.get("edited_message")
            callback_query = update.get("callback_query")
            
            if callback_query:
                # Handle callback queries (button clicks)
                await self.handle_callback_query(callback_query)
                return
            
            if not message:
                return
            
            chat = message.get("chat", {})
            chat_id = chat.get("id")
            user = message.get("from", {})
            user_id = user.get("id")
            username = user.get("username", "")
            first_name = user.get("first_name", "")
            
            # Get or create chat
            room_key = f"telegram_{chat_id}"
            
            # Handle different message types
            if "text" in message:
                text = message.get("text", "")
                await self.handle_text_message(
                    chat_id=chat_id,
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    text=text,
                    message_id=message.get("message_id"),
                    room_key=room_key,
                    db=db
                )
            elif "photo" in message:
                await self.handle_photo_message(
                    chat_id=chat_id,
                    user_id=user_id,
                    photo=message.get("photo", []),
                    caption=message.get("caption", ""),
                    room_key=room_key,
                    db=db
                )
            elif "document" in message:
                await self.handle_document_message(
                    chat_id=chat_id,
                    user_id=user_id,
                    document=message.get("document", {}),
                    caption=message.get("caption", ""),
                    room_key=room_key,
                    db=db
                )
            elif "voice" in message:
                await self.handle_voice_message(
                    chat_id=chat_id,
                    user_id=user_id,
                    voice=message.get("voice", {}),
                    room_key=room_key,
                    db=db
                )
        
        except Exception as e:
            print(f"Error processing Telegram update: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_text_message(
        self,
        chat_id: int,
        user_id: int,
        username: str,
        first_name: str,
        text: str,
        message_id: int,
        room_key: str,
        db: Optional[AsyncSession] = None
    ):
        """Handle text message from Telegram"""
        # Send typing indicator
        await self.send_typing(chat_id)
        
        # Process message through orchestrator
        try:
            response = await self.orchestrator.process_message(
                text=text,
                room_key=room_key,
                user_id=str(user_id),
                metadata={
                    "platform": "telegram",
                    "chat_id": chat_id,
                    "username": username,
                    "first_name": first_name
                },
                db=db
            )
            
            # Send response
            response_text = response.get("text", "Üzgünüm, yanıt veremiyorum.")
            await self.send_message(chat_id, response_text, reply_to_message_id=message_id)
        
        except Exception as e:
            print(f"Error processing text message: {e}")
            await self.send_message(
                chat_id, 
                "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
                reply_to_message_id=message_id
            )
    
    async def handle_photo_message(
        self,
        chat_id: int,
        user_id: int,
        photo: List[Dict],
        caption: str,
        room_key: str,
        db: Optional[AsyncSession] = None
    ):
        """Handle photo message from Telegram"""
        # Get largest photo
        largest_photo = max(photo, key=lambda p: p.get("file_size", 0))
        file_id = largest_photo.get("file_id")
        
        # Send typing indicator
        await self.send_typing(chat_id)
        
        # Process caption or send acknowledgment
        if caption:
            await self.handle_text_message(
                chat_id=chat_id,
                user_id=user_id,
                username="",
                first_name="",
                text=f"[Fotoğraf] {caption}",
                message_id=0,
                room_key=room_key,
                db=db
            )
        else:
            await self.send_message(
                chat_id,
                "Fotoğrafınızı aldım. Şu anda fotoğraf analizi henüz aktif değil."
            )
    
    async def handle_document_message(
        self,
        chat_id: int,
        user_id: int,
        document: Dict,
        caption: str,
        room_key: str,
        db: Optional[AsyncSession] = None
    ):
        """Handle document message from Telegram"""
        file_name = document.get("file_name", "document")
        file_size = document.get("file_size", 0)
        
        # Send typing indicator
        await self.send_typing(chat_id)
        
        # Process caption or send acknowledgment
        if caption:
            await self.handle_text_message(
                chat_id=chat_id,
                user_id=user_id,
                username="",
                first_name="",
                text=f"[Dosya: {file_name}] {caption}",
                message_id=0,
                room_key=room_key,
                db=db
            )
        else:
            await self.send_message(
                chat_id,
                f"Dosyanızı aldım ({file_name}). Şu anda dosya analizi henüz aktif değil."
            )
    
    async def handle_voice_message(
        self,
        chat_id: int,
        user_id: int,
        voice: Dict,
        room_key: str,
        db: Optional[AsyncSession] = None
    ):
        """Handle voice message from Telegram"""
        # Send typing indicator
        await self.send_typing(chat_id)
        
        # Send acknowledgment
        await self.send_message(
            chat_id,
            "Ses mesajınızı aldım. Şu anda ses mesajı analizi henüz aktif değil."
        )
    
    async def handle_callback_query(self, callback_query: Dict):
        """Handle callback query (button click)"""
        query_id = callback_query.get("id")
        data = callback_query.get("data", "")
        chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        
        # Answer callback query
        if self.api_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{self.api_url}/answerCallbackQuery",
                        json={"callback_query_id": query_id}
                    )
            except Exception as e:
                print(f"Error answering callback query: {e}")
        
        # Process callback data
        # TODO: Implement callback handling
        print(f"Callback query received: {data}")

