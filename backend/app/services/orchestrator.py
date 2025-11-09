"""
Orchestrator Service - Rules → RAG → LLM Fallback
"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.rule_service import RuleService
from app.core.database import get_db
from app.core.security import PIIRedactor
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrchestratorService:
    """Main orchestration service"""
    
    def __init__(self):
        self.rule_service = RuleService()
        self.rag_service = rag_service
        self.llm_service = llm_service
    
    async def process_message(
        self,
        text: str,
        room_key: str,
        websocket=None,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Process message through: Rules → RAG → LLM
        Returns: {text: str, sources: List, context: Dict}
        """
        try:
            # Redact PII
            redacted_text = PIIRedactor.redact_text(text)
            
            # Step 1: Check rules
            try:
                rule_result = await self.rule_service.match_rule(redacted_text, db=db)
                if rule_result and rule_result.get("confidence", 0) >= 0.9:
                    logger.info("Rule matched", rule_id=rule_result.get("rule_id"), room_key=room_key)
                    return {
                        "text": rule_result.get("response", ""),
                        "sources": [],
                        "context": {"source": "rule", "rule_id": rule_result.get("rule_id")}
                    }
            except Exception as e:
                logger.warning("Rule matching error", error=str(e), exc_info=True)
                # Continue to RAG/LLM if rule matching fails
            
            # Step 2: RAG search
            try:
                rag_documents, hit_rate = await self.rag_service.search(
                    query=redacted_text,
                    context={"room_key": room_key},
                    db=db
                )
                
                if hit_rate and rag_documents:
                    # RAG hit - generate response with context
                    context_string = await self.rag_service.get_context_string(rag_documents)
                    system_prompt = self.llm_service.create_system_prompt(context_string)
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": redacted_text}
                    ]
                    
                    # Call LLM with RAG context
                    response_text = ""
                    error_occurred = False
                    async for chunk in self.llm_service.call_llm(
                        messages=messages,
                        temperature=0.2,
                        stream=True,
                        db=db
                    ):
                        if chunk.get("type") == "text":
                            response_text += chunk.get("data", "")
                        elif chunk.get("type") == "end":
                            break
                        elif chunk.get("type") == "error":
                            error_occurred = True
                            logger.error("LLM error in RAG context", error=chunk.get("data", {}).get("message"))
                            break
                    
                    if error_occurred or not response_text:
                        # Fallback message if LLM fails
                        response_text = "RAG sonuçları bulundu ancak yanıt oluşturulamadı. Lütfen operatöre yönlendiriliyorsunuz."
                    
                    logger.info("RAG hit", documents=len(rag_documents), hit_rate=hit_rate, room_key=room_key)
                    return {
                        "text": response_text,
                        "sources": [
                            {
                                "title": doc.get("name"),
                                "url": doc.get("source"),
                                "score": doc.get("score")
                            }
                            for doc in rag_documents
                        ],
                        "context": {"source": "rag", "hit_rate": hit_rate}
                    }
            except Exception as e:
                logger.error("RAG search error", error=str(e), room_key=room_key, exc_info=True)
                # Continue to LLM fallback if RAG fails
            
            # Step 3: LLM fallback (no RAG hit or RAG failed)
            try:
                system_prompt = self.llm_service.create_system_prompt()
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": redacted_text}
                ]
                
                response_text = ""
                error_occurred = False
                async for chunk in self.llm_service.call_llm(
                    messages=messages,
                    temperature=0.2,
                    stream=True,
                    db=db
                ):
                    if chunk.get("type") == "text":
                        response_text += chunk.get("data", "")
                    elif chunk.get("type") == "end":
                        break
                    elif chunk.get("type") == "error":
                        error_occurred = True
                        logger.error("LLM error in fallback", error=chunk.get("data", {}).get("message"))
                        break
                
                if error_occurred or not response_text:
                    response_text = "Üzgünüm, şu anda yanıt veremiyorum. Lütfen operatöre yönlendiriyorum."
                
                logger.info("LLM fallback used", room_key=room_key, has_response=bool(response_text))
                return {
                    "text": response_text,
                    "sources": [],
                    "context": {"source": "llm_fallback", "rag_hit": False}
                }
            except Exception as e:
                logger.error("LLM fallback error", error=str(e), room_key=room_key, exc_info=True)
                # Final fallback
                return {
                    "text": "Üzgünüm, şu anda sistemde bir sorun var. Lütfen daha sonra tekrar deneyin veya operatöre başvurun.",
                    "sources": [],
                    "context": {"source": "error_fallback"}
                }
        
        except Exception as e:
            logger.error("Orchestrator process_message error", error=str(e), room_key=room_key, exc_info=True)
            return {
                "text": "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
                "sources": [],
                "context": {"source": "error"}
            }

