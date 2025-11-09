"""
RAG Service - Hybrid Search (Semantic + BM25)
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from openai import AsyncOpenAI

from app.config import settings
from app.models.kb_document import KBDocument, DocumentStatus
from app.models.rag_metrics import RAGMetrics
from app.core.database import get_db


class HybridRAGService:
    """Hybrid RAG System with Semantic + Keyword Search"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.min_similarity = settings.RAG_MIN_SIMILARITY
        self.max_documents = settings.RAG_MAX_DOCUMENTS
        self.semantic_weight = settings.RAG_HYBRID_WEIGHTS["semantic"]
        self.keyword_weight = settings.RAG_HYBRID_WEIGHTS["keyword"]
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text"""
        response = await self.openai_client.embeddings.create(
            model=settings.RAG_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    async def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Tuple[KBDocument, float]]:
        """Semantic search using pgvector cosine similarity"""
        # Convert embedding to PostgreSQL vector format
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        query = select(KBDocument).where(
            KBDocument.status == DocumentStatus.INDEXED,
            KBDocument.embedding.isnot(None)
        ).order_by(
            text("embedding <=> :embedding").bindparam(embedding=embedding_str)
        ).limit(limit)
        
        # Execute query (this would need proper async session handling)
        # For now, returning placeholder
        return []
    
    async def keyword_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Tuple[KBDocument, float]]:
        """Keyword search using BM25-like scoring"""
        # Extract keywords
        keywords = re.findall(r'\b\w+\b', query.lower())
        
        # PostgreSQL full-text search
        query_text = " & ".join(keywords)
        sql = f"""
            SELECT *, ts_rank(to_tsvector('english', content), plainto_tsquery('english', :query)) as score
            FROM kb_documents
            WHERE status = 'indexed'
            AND to_tsvector('english', content) @@ plainto_tsquery('english', :query)
            ORDER BY score DESC
            LIMIT :limit
        """
        # Execute query (placeholder)
        return []
    
    def hybrid_score(
        self,
        semantic_results: List[Tuple[KBDocument, float]],
        keyword_results: List[Tuple[KBDocument, float]]
    ) -> List[Tuple[KBDocument, float]]:
        """Combine semantic and keyword results with weighted scoring"""
        doc_scores: Dict[str, Tuple[KBDocument, float]] = {}
        
        # Add semantic results
        for doc, score in semantic_results:
            normalized_score = (1.0 - score) if score < 1.0 else 0.0  # Convert distance to similarity
            if doc.id not in doc_scores:
                doc_scores[str(doc.id)] = (doc, 0.0)
            doc, current_score = doc_scores[str(doc.id)]
            doc_scores[str(doc.id)] = (doc, current_score + normalized_score * self.semantic_weight)
        
        # Add keyword results
        for doc, score in keyword_results:
            if doc.id not in doc_scores:
                doc_scores[str(doc.id)] = (doc, 0.0)
            doc, current_score = doc_scores[str(doc.id)]
            doc_scores[str(doc.id)] = (doc, current_score + score * self.keyword_weight)
        
        # Sort by score and return
        results = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)
        return results
    
    async def search(
        self,
        query: str,
        context: Optional[Dict] = None,
        db: AsyncSession = None
    ) -> Tuple[List[Dict], bool]:
        """
        Hybrid RAG search
        Returns: (documents, hit_rate)
        """
        start_time = time.time()
        
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query)
            
            # Semantic search
            semantic_results = await self.semantic_search(query_embedding, limit=10)
            
            # Keyword search
            keyword_results = await self.keyword_search(query, limit=10)
            
            # Hybrid scoring
            combined_results = self.hybrid_score(semantic_results, keyword_results)
            
            # Apply threshold
            filtered_results = [
                (doc, score) for doc, score in combined_results
                if score >= self.min_similarity
            ]
            
            # Limit results
            final_results = filtered_results[:self.max_documents]
            
            # Calculate metrics
            response_time_ms = (time.time() - start_time) * 1000
            hit_rate = len(final_results) > 0
            similarity_scores = [score for _, score in final_results]
            
            # Format results
            documents = [
                {
                    "id": str(doc.id),
                    "name": doc.name,
                    "source": doc.source,
                    "content": doc.content[:500],  # Truncate
                    "score": score,
                    "metadata": doc.metadata or {}
                }
                for doc, score in final_results
            ]
            
            # Save metrics
            if db:
                metrics = RAGMetrics(
                    query_text=query,
                    retrieved_documents=len(final_results),
                    similarity_scores=similarity_scores,
                    response_time_ms=response_time_ms,
                    hit_rate=hit_rate
                )
                db.add(metrics)
                await db.commit()
            
            return documents, hit_rate
            
        except Exception as e:
            # Log error and return empty results
            print(f"RAG search error: {e}")
            return [], False
    
    async def get_context_string(self, documents: List[Dict]) -> str:
        """Convert retrieved documents to context string"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[{i}] {doc['name']}\n{doc['content']}\nSource: {doc['source']}")
        return "\n\n".join(context_parts)


rag_service = HybridRAGService()

