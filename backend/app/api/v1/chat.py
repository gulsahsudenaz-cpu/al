"""Chat API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.chat import Chat, ChatStatus
from app.models.message import Message, MessageRole
from app.services.orchestrator import OrchestratorService

router = APIRouter()
orchestrator = OrchestratorService()


class ChatCreate(BaseModel):
    tenant: str
    metadata: Optional[dict] = None


class MessageCreate(BaseModel):
    text: str
    media: Optional[dict] = None


@router.post("/chats")
async def create_chat(chat: ChatCreate, db: AsyncSession = Depends(get_db)):
    """Create a new chat"""
    new_chat = Chat(tenant=chat.tenant, status=ChatStatus.ACTIVE, metadata=str(chat.metadata) if chat.metadata else None)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return {"id": str(new_chat.id), "status": new_chat.status.value}


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
    
    return {
        "message": {
            "id": str(assistant_message.id),
            "role": assistant_message.role.value,
            "text": assistant_message.text,
            "sources": response.get("sources", [])
        }
    }

