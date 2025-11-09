"""Chat API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
import html
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.logging import get_logger
from app.models.chat import Chat, ChatStatus
from app.models.message import Message, MessageRole
from app.services.orchestrator import OrchestratorService
from app.config import settings

router = APIRouter()
orchestrator = OrchestratorService()
logger = get_logger(__name__)

# Constants
MAX_TEXT_LENGTH = 5000
MAX_TENANT_LENGTH = 100


class ChatCreate(BaseModel):
    tenant: str = Field(..., max_length=MAX_TENANT_LENGTH, min_length=1)
    metadata: Optional[dict] = None
    
    @validator('tenant')
    def validate_tenant(cls, v):
        """Validate tenant string"""
        # Remove whitespace
        v = v.strip()
        if not v:
            raise ValueError("Tenant cannot be empty")
        # Basic sanitization
        v = html.escape(v)
        return v


class MessageCreate(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LENGTH, min_length=1)
    media: Optional[dict] = None
    
    @validator('text')
    def validate_text(cls, v):
        """Validate and sanitize text"""
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v.strip())
        if not v:
            raise ValueError("Message text cannot be empty")
        # Basic XSS protection - escape HTML
        v = html.escape(v)
        # Limit length
        if len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f"Message text cannot exceed {MAX_TEXT_LENGTH} characters")
        return v


@router.post("/chats")
async def create_chat(chat: ChatCreate, db: AsyncSession = Depends(get_db)):
    """Create a new chat"""
    try:
        new_chat = Chat(tenant=chat.tenant, status=ChatStatus.ACTIVE, meta_data=str(chat.metadata) if chat.metadata else None)
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        logger.info("Chat created", chat_id=str(new_chat.id), tenant=chat.tenant)
        return {"id": str(new_chat.id), "status": new_chat.status.value}
    except Exception as e:
        logger.error("Error creating chat", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat"
        )


@router.get("/chats/{chat_id}")
async def get_chat(chat_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get chat by ID"""
    from sqlalchemy import select
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "id": str(chat.id),
        "tenant": chat.tenant,
        "status": chat.status.value,
        "created_at": chat.created_at.isoformat()
    }


@router.get("/chats/{chat_id}/messages")
async def get_messages(chat_id: UUID, limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Get messages for a chat"""
    from sqlalchemy import select
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {
            "id": str(msg.id),
            "role": msg.role.value,
            "text": msg.text,
            "media": msg.media,
            "created_at": msg.created_at.isoformat()
        }
        for msg in reversed(messages)
    ]


@router.post("/chats/{chat_id}/messages")
async def create_message(
    chat_id: UUID,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new message"""
    try:
        # Verify chat exists
        from sqlalchemy import select
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Create user message
        user_message = Message(
            chat_id=chat_id,
            role=MessageRole.USER,
            text=message.text,
            media=message.media
        )
        db.add(user_message)
        await db.commit()
        logger.info("User message created", message_id=str(user_message.id), chat_id=str(chat_id))
        
        # Process through orchestrator
        response = await orchestrator.process_message(
            text=message.text,
            room_key=chat.tenant,
            db=db
        )
        
        # Create assistant message
        assistant_message = Message(
            chat_id=chat_id,
            role=MessageRole.ASSISTANT,
            text=response.get("text", ""),
            context=response.get("context", {})
        )
        db.add(assistant_message)
        await db.commit()
        logger.info("Assistant message created", message_id=str(assistant_message.id), chat_id=str(chat_id))
        
        return {
            "message": {
                "id": str(assistant_message.id),
                "role": assistant_message.role.value,
                "text": assistant_message.text,
                "sources": response.get("sources", [])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating message", error=str(e), chat_id=str(chat_id), exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )

