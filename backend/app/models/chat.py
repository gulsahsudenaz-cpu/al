"""Chat Model"""
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ChatStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    WAITING = "waiting"
    ASSIGNED = "assigned"


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant = Column(String(100), nullable=False, index=True)
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE, nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    sla_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        {"schema": "public"}
    )

