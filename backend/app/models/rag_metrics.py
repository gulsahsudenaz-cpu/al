"""RAG Metrics Model"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class RAGMetrics(Base):
    __tablename__ = "rag_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(String(1000), nullable=False)
    retrieved_documents = Column(Integer, nullable=False, default=0)
    similarity_scores = Column(ARRAY(Float), nullable=True)
    response_time_ms = Column(Float, nullable=False)
    hit_rate = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        {"schema": "public"}
    )

