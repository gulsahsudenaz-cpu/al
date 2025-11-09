"""Admin API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_, case

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.logging import get_logger
from app.models.chat import Chat, ChatStatus
from app.models.rag_metrics import RAGMetrics
from app.models.llm_usage import LLMUsage
from app.models.message import Message
from app.models.kb_document import KBDocument

router = APIRouter()
logger = get_logger(__name__)


@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Today's date
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total chats today
        today_chats_result = await db.execute(
            select(func.count(Chat.id)).where(Chat.created_at >= today_start)
        )
        today_chats = today_chats_result.scalar() or 0
        
        # Total active chats
        active_chats_result = await db.execute(
            select(func.count(Chat.id)).where(Chat.status == ChatStatus.ACTIVE)
        )
        active_chats = active_chats_result.scalar() or 0
        
        # Unresolved chats (waiting or assigned)
        unresolved_result = await db.execute(
            select(func.count(Chat.id)).where(
                Chat.status.in_([ChatStatus.WAITING, ChatStatus.ASSIGNED])
            )
        )
        unresolved = unresolved_result.scalar() or 0
        
        # Average response time from LLM (today)
        avg_response_result = await db.execute(
            select(func.avg(LLMUsage.latency_ms)).where(LLMUsage.created_at >= today_start)
        )
        avg_response_time = float(avg_response_result.scalar() or 0.0) / 1000  # Convert to seconds
        
        # RAG hit rate (last 7 days)
        week_start = datetime.utcnow() - timedelta(days=7)
        rag_hit_rate_result = await db.execute(
            select(
                func.avg(
                    case((RAGMetrics.hit_rate == True, 1), else_=0)
                ).label("hit_rate")
            ).where(RAGMetrics.created_at >= week_start)
        )
        rag_hit_rate = float(rag_hit_rate_result.scalar() or 0.0) * 100
        
        # Total messages today
        today_messages_result = await db.execute(
            select(func.count(Message.id)).where(Message.created_at >= today_start)
        )
        today_messages = today_messages_result.scalar() or 0
        
        # LLM cost today
        llm_cost_result = await db.execute(
            select(func.sum(LLMUsage.cost_usd)).where(LLMUsage.created_at >= today_start)
        )
        llm_cost_today = float(llm_cost_result.scalar() or 0.0)
        
        return {
            "today_chats": today_chats,
            "active_chats": active_chats,
            "unresolved": unresolved,
            "avg_response_time_seconds": round(avg_response_time, 2),
            "rag_hit_rate": round(rag_hit_rate, 1),
            "today_messages": today_messages,
            "llm_cost_today": round(llm_cost_today, 4),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting dashboard stats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")


@router.get("/chats")
async def list_chats(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all chats (admin only)"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        query = select(Chat)
        if status:
            try:
                query = query.where(Chat.status == ChatStatus(status))
            except ValueError:
                # Invalid status, ignore filter
                logger.warning(f"Invalid chat status: {status}")
        
        query = query.order_by(desc(Chat.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        chats = result.scalars().all()
        
        # Get message counts for each chat (optimized with single query per chat)
        chat_list = []
        for chat in chats:
            # Count messages
            msg_count_result = await db.execute(
                select(func.count(Message.id)).where(Message.chat_id == chat.id)
            )
            message_count = msg_count_result.scalar() or 0
            
            # Get last message
            last_msg_result = await db.execute(
                select(Message)
                .where(Message.chat_id == chat.id)
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            last_message = last_msg_result.scalar_one_or_none()
            
            chat_list.append({
                "id": str(chat.id),
                "tenant": chat.tenant or "unknown",
                "status": chat.status.value,
                "message_count": message_count,
                "last_message": last_message.text[:100] if last_message and last_message.text else None,
                "last_message_at": last_message.created_at.isoformat() if last_message else chat.created_at.isoformat(),
                "created_at": chat.created_at.isoformat()
            })
        
        return chat_list
    except Exception as e:
        logger.error("Error listing chats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list chats")


@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a chat"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Verify chat exists
        chat_result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = chat_result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Get messages
        messages_result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
            .limit(limit)
        )
        messages = messages_result.scalars().all()
        
        return [
            {
                "id": str(msg.id),
                "role": msg.role.value,
                "text": msg.text or "",
                "media": msg.media or None,
                "context": msg.context or None,
                "created_at": msg.created_at.isoformat() if msg.created_at else datetime.utcnow().isoformat()
            }
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting chat messages", chat_id=str(chat_id), error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get chat messages")


@router.get("/metrics/rag")
async def get_rag_metrics(
    limit: int = 100,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get RAG metrics"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Validate days parameter
        if days < 1 or days > 365:
            days = 7
        
        # Get metrics for last N days
        since_date = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(RAGMetrics)
            .where(RAGMetrics.created_at >= since_date)
            .order_by(desc(RAGMetrics.created_at))
            .limit(limit)
        )
        metrics = result.scalars().all()
        
        # Calculate hit rate (as percentage)
        hit_rate_result = await db.execute(
            select(
                func.avg(
                    case((RAGMetrics.hit_rate == True, 1), else_=0)
                ).label("hit_rate")
            ).where(RAGMetrics.created_at >= since_date)
        )
        avg_hit_rate = float(hit_rate_result.scalar() or 0.0) * 100
        
        # Calculate average response time
        avg_response_time_result = await db.execute(
            select(func.avg(RAGMetrics.response_time_ms)).label("avg_response_time")
            .where(RAGMetrics.created_at >= since_date)
        )
        avg_response_time = float(avg_response_time_result.scalar() or 0.0)
        
        # Get daily hit rates for chart (with error handling)
        daily_hit_rates = []
        try:
            for i in range(days):
                day_start = since_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                try:
                    day_result = await db.execute(
                        select(
                            func.avg(
                                case((RAGMetrics.hit_rate == True, 1), else_=0)
                            ).label("hit_rate")
                        ).where(
                            and_(
                                RAGMetrics.created_at >= day_start,
                                RAGMetrics.created_at < day_end
                            )
                        )
                    )
                    day_hit_rate = float(day_result.scalar() or 0.0) * 100
                    daily_hit_rates.append(day_hit_rate)
                except Exception as e:
                    logger.warning(f"Error calculating daily hit rate for day {i}", error=str(e))
                    daily_hit_rates.append(0.0)
        except Exception as e:
            logger.error("Error calculating daily hit rates", error=str(e))
            # Fill with zeros if calculation fails
            daily_hit_rates = [0.0] * days
        
        # Ensure we have exactly 'days' number of values
        while len(daily_hit_rates) < days:
            daily_hit_rates.append(0.0)
        
        return {
            "metrics": [
                {
                    "id": str(m.id),
                    "query_text": (m.query_text or "")[:100],  # Truncate long queries
                    "retrieved_documents": m.retrieved_documents or 0,
                    "similarity_scores": m.similarity_scores or [],
                    "response_time_ms": m.response_time_ms or 0.0,
                    "hit_rate": m.hit_rate or False,
                    "created_at": m.created_at.isoformat() if m.created_at else datetime.utcnow().isoformat()
                }
                for m in metrics
            ],
            "avg_hit_rate": avg_hit_rate,
            "avg_response_time_ms": avg_response_time,
            "daily_hit_rates": daily_hit_rates[:days],  # Ensure exact length
            "total_queries": len(metrics)
        }
    except Exception as e:
        logger.error("Error getting RAG metrics", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get RAG metrics")


@router.get("/metrics/llm")
async def get_llm_metrics(
    limit: int = 100,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get LLM usage metrics"""
    # Check role
    if current_user.get("role") not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Validate days parameter
        if days < 1 or days > 365:
            days = 7
        
        # Get metrics for last N days
        since_date = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(LLMUsage)
            .where(LLMUsage.created_at >= since_date)
            .order_by(desc(LLMUsage.created_at))
            .limit(limit)
        )
        usage = result.scalars().all()
        
        # Calculate totals
        total_result = await db.execute(
            select(
                func.sum(LLMUsage.cost_usd).label("total_cost"),
                func.sum(LLMUsage.total_tokens).label("total_tokens"),
                func.avg(LLMUsage.latency_ms).label("avg_latency"),
                func.count(LLMUsage.id).label("total_calls")
            ).where(LLMUsage.created_at >= since_date)
        )
        totals = total_result.first()
        
        # Get today's metrics
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await db.execute(
            select(
                func.sum(LLMUsage.cost_usd).label("today_cost"),
                func.count(LLMUsage.id).label("today_calls")
            ).where(LLMUsage.created_at >= today_start)
        )
        today_totals = today_result.first()
        
        return {
            "usage": [
                {
                    "id": str(u.id),
                    "model": u.model or "unknown",
                    "prompt_tokens": u.prompt_tokens or 0,
                    "completion_tokens": u.completion_tokens or 0,
                    "total_tokens": u.total_tokens or 0,
                    "cost_usd": float(u.cost_usd or 0.0),
                    "latency_ms": float(u.latency_ms or 0.0),
                    "created_at": u.created_at.isoformat() if u.created_at else datetime.utcnow().isoformat()
                }
                for u in usage
            ],
            "totals": {
                "total_cost_usd": float(totals.total_cost or 0.0) if totals else 0.0,
                "total_tokens": int(totals.total_tokens or 0) if totals else 0,
                "avg_latency_ms": float(totals.avg_latency or 0.0) if totals else 0.0,
                "total_calls": int(totals.total_calls or 0) if totals else 0
            },
            "today": {
                "cost_usd": float(today_totals.today_cost or 0.0) if today_totals else 0.0,
                "calls": int(today_totals.today_calls or 0) if today_totals else 0
            }
        }
    except Exception as e:
        logger.error("Error getting LLM metrics", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get LLM metrics")

