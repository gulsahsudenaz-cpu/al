"""Telegram Bot API Routes"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.services.telegram_service import TelegramService

router = APIRouter()
telegram_service = TelegramService()


class WebhookUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    data = await request.json()
    update = WebhookUpdate(**data)
    
    # Process update
    await telegram_service.process_update(update.dict())
    
    return {"status": "ok"}


@router.get("/webhook")
async def set_webhook():
    """Set Telegram webhook URL"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    # TODO: Set webhook via Telegram API
    return {"status": "webhook set", "url": settings.TELEGRAM_WEBHOOK_URL}

