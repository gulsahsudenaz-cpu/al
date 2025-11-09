"""
LLM Service - GPT-4 Turbo Integration with Cost Tracking
"""
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime, timedelta
import time
import json
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.models.llm_usage import LLMUsage
from app.core.database import get_db


class CircuitBreaker:
    """Circuit breaker for LLM calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            raise


class LLMService:
    """LLM Service with GPT-4 Turbo"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.MODEL
        self.circuit_breaker = CircuitBreaker()
        self.daily_cost_limit = settings.LLM_DAILY_COST_LIMIT
        self.max_tokens = settings.LLM_MAX_TOKENS_PER_REQUEST
    
    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = None
    ) -> float:
        """Calculate cost based on token usage"""
        model = model or self.model
        
        # Pricing per 1M tokens (as of 2024)
        pricing = {
            "gpt-4-turbo": {"prompt": 10.0, "completion": 30.0},
            "gpt-4": {"prompt": 30.0, "completion": 60.0},
            "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
        }
        
        if model not in pricing:
            # Default to gpt-4-turbo pricing
            model = "gpt-4-turbo"
        
        cost = (
            (prompt_tokens / 1_000_000) * pricing[model]["prompt"] +
            (completion_tokens / 1_000_000) * pricing[model]["completion"]
        )
        return cost
    
    async def get_daily_cost(self, db: AsyncSession) -> float:
        """Get today's total cost"""
        today = datetime.utcnow().date()
        result = await db.execute(
            select(func.sum(LLMUsage.cost_usd)).where(
                func.date(LLMUsage.created_at) == today
            )
        )
        total = result.scalar() or 0.0
        return total
    
    async def check_cost_limit(self, db: AsyncSession) -> bool:
        """Check if daily cost limit is reached"""
        daily_cost = await self.get_daily_cost(db)
        return daily_cost < self.daily_cost_limit
    
    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        tools: Optional[List[Dict]] = None,
        stream: bool = True,
        db: AsyncSession = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Call LLM with streaming support
        Yields: {"type": "text"|"tool_call"|"end", "data": ...}
        """
        start_time = time.time()
        
        # Check cost limit
        if db and not await self.check_cost_limit(db):
            yield {
                "type": "error",
                "data": {"message": "Daily cost limit reached"}
            }
            return
        
        try:
            # Prepare request
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": self.max_tokens,
                "stream": stream,
            }
            
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Call LLM with circuit breaker
            response = await self.circuit_breaker.call(
                self.client.chat.completions.create,
                **request_params
            )
            
            content = ""
            tool_calls = []
            prompt_tokens = 0
            completion_tokens = 0
            
            if stream:
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta
                        
                        # Content
                        if delta.content:
                            content += delta.content
                            yield {"type": "text", "data": delta.content}
                        
                        # Tool calls
                        if delta.tool_calls:
                            for tool_call in delta.tool_calls:
                                if len(tool_calls) <= tool_call.index:
                                    tool_calls.extend([None] * (tool_call.index + 1 - len(tool_calls)))
                                if tool_calls[tool_call.index] is None:
                                    tool_calls[tool_call.index] = {
                                        "id": tool_call.id,
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    }
                                if tool_call.function:
                                    if tool_call.function.name:
                                        tool_calls[tool_call.index]["function"]["name"] = tool_call.function.name
                                    if tool_call.function.arguments:
                                        tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments
                        
                        # Usage
                        if chunk.usage:
                            prompt_tokens = chunk.usage.prompt_tokens or 0
                            completion_tokens = chunk.usage.completion_tokens or 0
            else:
                message = response.choices[0].message
                content = message.content or ""
                tool_calls = message.tool_calls or []
                if response.usage:
                    prompt_tokens = response.usage.prompt_tokens or 0
                    completion_tokens = response.usage.completion_tokens or 0
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            total_tokens = prompt_tokens + completion_tokens
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # Save usage
            if db:
                usage = LLMUsage(
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_usd=cost,
                    latency_ms=latency_ms
                )
                db.add(usage)
                await db.commit()
            
            # Yield end event
            yield {
                "type": "end",
                "data": {
                    "content": content,
                    "tool_calls": tool_calls,
                    "latency_ms": latency_ms,
                    "tokens": total_tokens,
                    "cost": cost
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"message": str(e)}
            }
    
    def create_system_prompt(self, rag_context: Optional[str] = None) -> str:
        """Create system prompt with RAG context"""
        base_prompt = """Sen kıdemli bir destek asistanı ve teknik çözümleyicisin. 
Kurallar:
- PII (kişisel bilgi) sızdırma yapma
- Bilmediğin konularda tahmin yapmak yerine "Bilmiyorum ancak şu kaynaktan sorabilirsin: [kaynak]"
- Kaynakları (başlık/url/skor) açıkça belirt
- RAG skoru minimum eşiğin altındaysa "RAG bulunamadı, operatöre yönlendiriyorum" de
- Kibar, kısa cümleler kullan
- Çok adımlı işlemlerde maddeli liste kullan"""
        
        if rag_context:
            base_prompt += f"\n\nKonteks:\n{rag_context}"
        
        return base_prompt


llm_service = LLMService()

