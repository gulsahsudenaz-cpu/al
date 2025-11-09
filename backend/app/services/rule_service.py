"""
Rule Service - Rule Engine with Regex/Keyword Matching
"""
from typing import Dict, Optional
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.rule import Rule
from app.core.database import get_db


class RuleService:
    """Rule engine service"""
    
    async def match_rule(
        self,
        text: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[Dict]:
        """
        Match text against rules
        Returns: {rule_id, response, confidence} or None
        """
        if not db:
            return None
        
        # Get all rules ordered by priority
        result = await db.execute(
            select(Rule).order_by(Rule.order.asc())
        )
        rules = result.scalars().all()
        
        for rule in rules:
            # Try regex match
            try:
                if re.search(rule.key, text, re.IGNORECASE):
                    return {
                        "rule_id": str(rule.id),
                        "response": rule.value,
                        "confidence": 0.95,
                        "action": rule.action
                    }
            except re.error:
                # Invalid regex, try keyword match
                if rule.key.lower() in text.lower():
                    return {
                        "rule_id": str(rule.id),
                        "response": rule.value,
                        "confidence": 0.85,
                        "action": rule.action
                    }
        
        return None

