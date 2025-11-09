"""Telegram Bot Service"""
from typing import Dict, Optional
import httpx

from app.config import settings
from app.services.orchestrator import OrchestratorService


class TelegramService:
    """Telegram bot service"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.orchestrator = OrchestratorService()
    
    async def send_message(self, chat_id: int, text: str):
        """Send message to Telegram chat"""
        if not self.bot_token:
            return
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_url}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
    
    async def process_update(self, update: Dict):
        """Process Telegram update"""
        if "message" not in update:
            return
        
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not text:
            return
        
        # Process message through orchestrator
        response = await self.orchestrator.process_message(
            text=text,
            room_key=f"telegram_{chat_id}"
        )
        
        # Send response
        await self.send_message(chat_id, response.get("text", "Üzgünüm, yanıt veremiyorum."))

