"""Knowledge Base Document Model"""
from sqlalchemy import Column, String, DateTime, Text, Enum, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, Vector
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"


class KBDocument(Base):
    __tablename__ = "kb_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    source = Column(String(1000), nullable=False)  # URL or file path
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)  # OpenAI embedding dimension (1536)
    size = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        {"schema": "public"},
        {"indexes": [
            {"name": "idx_kb_documents_status", "columns": ["status"]}
        ]}
    )

