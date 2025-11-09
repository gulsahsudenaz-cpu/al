"""Rule Model"""
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(500), nullable=False)  # regex/keyword pattern
    action = Column(String(50), nullable=False)  # reply|route|rag|macro
    value = Column(Text, nullable=False)  # action value (JSON or string)
    order = Column(Integer, nullable=False, default=0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        {"schema": "public"},
        {"indexes": [
            {"name": "idx_rules_order", "columns": ["order"]}
        ]}
    )

