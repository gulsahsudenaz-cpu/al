"""
Telegram Bot - Standalone Bot Script
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.telegram_service import TelegramService
from app.config import settings


async def main():
    """Main bot loop"""
    if not settings.TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return
    
    telegram_service = TelegramService()
    print("Telegram bot started")
    
    # Keep running
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

