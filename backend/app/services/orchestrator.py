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
        db: Optional[AsyncSession] = None
    ) -> Dict:
        """
        Process message through: Rules → RAG → LLM
        Returns: {text: str, sources: List, context: Dict}
        """
        # Redact PII
        redacted_text = PIIRedactor.redact_text(text)
        
        # Step 1: Check rules
        rule_result = await self.rule_service.match_rule(redacted_text, db=db)
        if rule_result and rule_result.get("confidence", 0) >= 0.9:
            return {
                "text": rule_result.get("response", ""),
                "sources": [],
                "context": {"source": "rule", "rule_id": rule_result.get("rule_id")}
            }
        
        # Step 2: RAG search
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
            
            return {
                "text": response_text or "RAG sonuçları bulundu ancak yanıt oluşturulamadı.",
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
        
        # Step 3: LLM fallback (no RAG hit)
        system_prompt = self.llm_service.create_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": redacted_text}
        ]
        
        response_text = ""
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
        
        return {
            "text": response_text or "Üzgünüm, şu anda yanıt veremiyorum. Lütfen operatöre yönlendiriyorum.",
            "sources": [],
            "context": {"source": "llm_fallback", "rag_hit": False}
        }

