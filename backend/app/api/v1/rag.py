"""RAG API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.logging import get_logger
from app.services.rag_service import rag_service
from app.models.kb_document import KBDocument, DocumentStatus

router = APIRouter()
logger = get_logger(__name__)


class DocumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    metadata: Optional[dict] = None


@router.post("/documents")
async def create_document(
    document: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new knowledge base document"""
    # Check role
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        new_doc = KBDocument(
            name=document.name,
            source=document.source,
            content=document.content,
            status=DocumentStatus.PENDING,
            metadata=document.metadata
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        # Trigger indexing job in background
        try:
            from app.workers.indexer import enqueue_document
            enqueue_document(str(new_doc.id))
            logger.info("Document enqueued for indexing", doc_id=str(new_doc.id))
        except Exception as e:
            logger.error("Error enqueueing document", doc_id=str(new_doc.id), error=str(e), exc_info=True)
            # Don't fail the request if enqueueing fails
        
        return {
            "id": str(new_doc.id),
            "name": new_doc.name,
            "status": new_doc.status.value
        }
    except Exception as e:
        logger.error("Error creating document", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create document")


@router.get("/documents")
async def list_documents(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List knowledge base documents"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        from sqlalchemy import select, desc
        
        query = select(KBDocument)
        if status:
            try:
                query = query.where(KBDocument.status == DocumentStatus(status))
            except ValueError:
                logger.warning(f"Invalid document status: {status}")
                # Ignore invalid status filter
        
        query = query.order_by(desc(KBDocument.created_at)).limit(min(limit, 100))
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return [
            {
                "id": str(doc.id),
                "name": doc.name or "Unnamed",
                "source": doc.source or "unknown",
                "status": doc.status.value,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in documents
        ]
    except Exception as e:
        logger.error("Error listing documents", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.post("/search")
async def search_rag(
    query: str = Field(..., min_length=1, max_length=1000),
    db: AsyncSession = Depends(get_db)
):
    """Search RAG system"""
    try:
        documents, hit_rate = await rag_service.search(query=query, db=db)
        
        return {
            "query": query,
            "documents": documents or [],
            "hit_rate": hit_rate or False,
            "count": len(documents) if documents else 0
        }
    except Exception as e:
        logger.error("Error searching RAG", query=query[:100], error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to search RAG system")

