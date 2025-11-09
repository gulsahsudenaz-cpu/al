"""Admin API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.chat import Chat, ChatStatus
from app.models.rag_metrics import RAGMetrics
from app.models.llm_usage import LLMUsage
from sqlalchemy import select, func, desc

router = APIRouter()


@router.get("/chats")
async def list_chats(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all chats (admin only)"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = select(Chat)
    if status:
        query = query.where(Chat.status == ChatStatus(status))
    query = query.order_by(desc(Chat.created_at)).limit(limit)
    
    result = await db.execute(query)
    chats = result.scalars().all()
    
    return [
        {
            "id": str(chat.id),
            "tenant": chat.tenant,
            "status": chat.status.value,
            "created_at": chat.created_at.isoformat()
        }
        for chat in chats
    ]


@router.get("/metrics/rag")
async def get_rag_metrics(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get RAG metrics"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.execute(
        select(RAGMetrics)
        .order_by(desc(RAGMetrics.created_at))
        .limit(limit)
    )
    metrics = result.scalars().all()
    
    # Calculate hit rate
    hit_rate_result = await db.execute(
        select(func.avg(func.cast(RAGMetrics.hit_rate, Integer))).label("hit_rate")
    )
    avg_hit_rate = float(hit_rate_result.scalar() or 0.0)
    
    return {
        "metrics": [
            {
                "id": str(m.id),
                "query_text": m.query_text,
                "retrieved_documents": m.retrieved_documents,
                "similarity_scores": m.similarity_scores,
                "response_time_ms": m.response_time_ms,
                "hit_rate": m.hit_rate,
                "created_at": m.created_at.isoformat()
            }
            for m in metrics
        ],
        "avg_hit_rate": avg_hit_rate
    }


@router.get("/metrics/llm")
async def get_llm_metrics(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get LLM usage metrics"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.execute(
        select(LLMUsage)
        .order_by(desc(LLMUsage.created_at))
        .limit(limit)
    )
    usage = result.scalars().all()
    
    # Calculate totals
    total_result = await db.execute(
        select(
            func.sum(LLMUsage.cost_usd).label("total_cost"),
            func.sum(LLMUsage.total_tokens).label("total_tokens"),
            func.avg(LLMUsage.latency_ms).label("avg_latency")
        )
    )
    totals = total_result.first()
    
    return {
        "usage": [
            {
                "id": str(u.id),
                "model": u.model,
                "prompt_tokens": u.prompt_tokens,
                "completion_tokens": u.completion_tokens,
                "total_tokens": u.total_tokens,
                "cost_usd": u.cost_usd,
                "latency_ms": u.latency_ms,
                "created_at": u.created_at.isoformat()
            }
            for u in usage
        ],
        "totals": {
            "total_cost_usd": totals.total_cost or 0.0,
            "total_tokens": totals.total_tokens or 0,
            "avg_latency_ms": totals.avg_latency or 0.0
        }
    }

