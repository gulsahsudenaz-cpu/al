"""Telegram Bot API Routes"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.telegram_service import TelegramService
from app.core.database import get_db

router = APIRouter()
telegram_service = TelegramService()


class WebhookUpdate(BaseModel):
    update_id: int
    message: Optional[dict] = None
    edited_message: Optional[dict] = None
    callback_query: Optional[dict] = None


@router.post("/webhook")
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Telegram webhook endpoint"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    try:
        data = await request.json()
        update = WebhookUpdate(**data)
        
        # Process update with database session
        await telegram_service.process_update(data, db=db)
        
        return {"status": "ok"}
    except Exception as e:
        # Log error but return 200 to Telegram (to avoid retries)
        print(f"Telegram webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@router.post("/set-webhook")
async def set_webhook(webhook_url: Optional[str] = None):
    """Set Telegram webhook URL"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    url = webhook_url or settings.TELEGRAM_WEBHOOK_URL
    if not url:
        raise HTTPException(status_code=400, detail="Webhook URL not provided")
    
    # Set webhook via Telegram API
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            api_url,
            json={"url": url}
        )
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "success",
                "message": "Webhook set successfully",
                "url": url,
                "result": result
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to set webhook: {result.get('description', 'Unknown error')}"
            )


@router.get("/webhook-info")
async def get_webhook_info():
    """Get Telegram webhook info"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "success",
                "webhook_info": result.get("result", {})
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get webhook info: {result.get('description', 'Unknown error')}"
            )


@router.delete("/delete-webhook")
async def delete_webhook():
    """Delete Telegram webhook"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/deleteWebhook"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url)
        result = response.json()
        
        if result.get("ok"):
            return {
                "status": "success",
                "message": "Webhook deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete webhook: {result.get('description', 'Unknown error')}"
            )

