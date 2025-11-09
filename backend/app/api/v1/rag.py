"""RAG API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.services.rag_service import rag_service
from app.models.kb_document import KBDocument, DocumentStatus

router = APIRouter()


class DocumentCreate(BaseModel):
    name: str
    source: str
    content: str
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
    except Exception as e:
        print(f"Error enqueueing document: {e}")
    
    return {
        "id": str(new_doc.id),
        "name": new_doc.name,
        "status": new_doc.status.value
    }


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
    
    from sqlalchemy import select
    
    query = select(KBDocument)
    if status:
        query = query.where(KBDocument.status == DocumentStatus(status))
    query = query.limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [
        {
            "id": str(doc.id),
            "name": doc.name,
            "source": doc.source,
            "status": doc.status.value,
            "created_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]


@router.post("/search")
async def search_rag(
    query: str,
    db: AsyncSession = Depends(get_db)
):
    """Search RAG system"""
    documents, hit_rate = await rag_service.search(query=query, db=db)
    
    return {
        "query": query,
        "documents": documents,
        "hit_rate": hit_rate,
        "count": len(documents)
    }

