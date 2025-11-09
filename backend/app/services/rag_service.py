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
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.RAG_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    async def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None,
        db: AsyncSession = None
    ) -> List[Tuple[KBDocument, float]]:
        """Semantic search using pgvector cosine similarity"""
        if not db or not query_embedding:
            return []
        
        try:
            # Convert embedding to PostgreSQL array format
            # Note: pgvector requires vector type, but we store as ARRAY
            # We'll cast ARRAY to vector in the query
            embedding_array = query_embedding
            
            # Use raw SQL for pgvector similarity search
            # Cosine distance operator: <=> (returns 0-2, where 0 = identical)
            # Convert distance to similarity: 1 - (distance / 2)
            # Since we store as ARRAY, we need to cast to vector for pgvector operations
            sql_query = text("""
                SELECT 
                    id, name, source, content, size, status, 
                    metadata, created_at, updated_at,
                    1 - ((embedding::vector <=> :embedding::vector) / 2.0) as similarity
                FROM kb_documents
                WHERE status = 'indexed' 
                AND embedding IS NOT NULL
                AND array_length(embedding, 1) > 0
                ORDER BY embedding::vector <=> :embedding::vector
                LIMIT :limit
            """)
            
            # Convert embedding to string format for PostgreSQL
            embedding_str = "[" + ",".join(map(str, embedding_array)) + "]"
            
            result = await db.execute(
                sql_query,
                {
                    "embedding": embedding_str,
                    "limit": limit
                }
            )
            
            documents = []
            for row in result:
                doc = KBDocument(
                    id=row.id,
                    name=row.name,
                    source=row.source,
                    content=row.content,
                    size=row.size,
                    status=DocumentStatus.INDEXED,
                    metadata=row.metadata,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                similarity = float(row.similarity) if row.similarity else 0.0
                documents.append((doc, similarity))
            
            return documents
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    async def keyword_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        db: AsyncSession = None
    ) -> List[Tuple[KBDocument, float]]:
        """Keyword search using PostgreSQL full-text search (BM25-like)"""
        if not db or not query:
            return []
        
        try:
            # Use PostgreSQL full-text search
            sql_query = text("""
                SELECT 
                    id, name, source, content, size, status, 
                    metadata, created_at, updated_at,
                    ts_rank(
                        to_tsvector('english', COALESCE(content, '')),
                        plainto_tsquery('english', :query)
                    ) as score
                FROM kb_documents
                WHERE status = 'indexed'
                AND to_tsvector('english', COALESCE(content, '')) @@ plainto_tsquery('english', :query)
                ORDER BY score DESC
                LIMIT :limit
            """)
            
            result = await db.execute(
                sql_query,
                {
                    "query": query,
                    "limit": limit
                }
            )
            
            documents = []
            for row in result:
                doc = KBDocument(
                    id=row.id,
                    name=row.name,
                    source=row.source,
                    content=row.content,
                    size=row.size,
                    status=DocumentStatus.INDEXED,
                    metadata=row.metadata,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                # Normalize score to 0-1 range
                # ts_rank typically returns 0-10, normalize to 0-1
                score = float(row.score) if row.score else 0.0
                score = min(1.0, score / 10.0)  # Normalize
                documents.append((doc, score))
            
            return documents
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []
    
    def hybrid_score(
        self,
        semantic_results: List[Tuple[KBDocument, float]],
        keyword_results: List[Tuple[KBDocument, float]]
    ) -> List[Tuple[KBDocument, float]]:
        """Combine semantic and keyword results with weighted scoring"""
        doc_scores: Dict[str, Tuple[KBDocument, float]] = {}
        
        # Add semantic results (score is already similarity 0-1)
        for doc, score in semantic_results:
            doc_id = str(doc.id)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = (doc, 0.0)
            current_doc, current_score = doc_scores[doc_id]
            doc_scores[doc_id] = (doc, current_score + score * self.semantic_weight)
        
        # Add keyword results (score is normalized to 0-1)
        for doc, score in keyword_results:
            doc_id = str(doc.id)
            if doc_id not in doc_scores:
                doc_scores[doc_id] = (doc, 0.0)
            current_doc, current_score = doc_scores[doc_id]
            doc_scores[doc_id] = (doc, current_score + score * self.keyword_weight)
        
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
            
            if not query_embedding:
                return [], False
            
            # Semantic search
            semantic_results = await self.semantic_search(
                query_embedding, 
                limit=10,
                db=db
            )
            
            # Keyword search
            keyword_results = await self.keyword_search(
                query, 
                limit=10,
                db=db
            )
            
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
                try:
                    metrics = RAGMetrics(
                        query_text=query,
                        retrieved_documents=len(final_results),
                        similarity_scores=similarity_scores,
                        response_time_ms=response_time_ms,
                        hit_rate=hit_rate
                    )
                    db.add(metrics)
                    await db.commit()
                except Exception as e:
                    print(f"Error saving RAG metrics: {e}")
                    await db.rollback()
            
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
