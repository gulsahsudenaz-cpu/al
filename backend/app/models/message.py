"""Message Model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ADMIN = "admin"


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    text = Column(Text, nullable=False)
    media = Column(JSON, nullable=True)  # {type: str, url: str, size: int}
    context = Column(JSON, nullable=True)  # RAG sources, metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages", lazy="selectin")
    
    __table_args__ = (
        {"schema": "public"},
        {"indexes": [
            {"name": "idx_messages_chat_created", "columns": ["chat_id", "created_at"], "postgresql_ops": {"created_at": "DESC"}}
        ]}
    )

