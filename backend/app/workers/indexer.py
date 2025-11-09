"""
RQ Worker - Document Indexer
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rq import Worker, Queue, Connection
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
import asyncio

from app.config import settings
from app.models.kb_document import KBDocument, DocumentStatus
from app.services.rag_service import rag_service
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging(level="INFO", json_format=False)
logger = get_logger(__name__)


redis_conn = Redis.from_url(settings.REDIS_URL)
indexer_queue = Queue("indexer", connection=redis_conn)


async def index_document(doc_id: str):
    """
    Index a document: Generate embedding and update database
    """
    # Create database session
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        # Get document
        result = await db.execute(
            select(KBDocument).where(KBDocument.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            logger.warning("Document not found", doc_id=doc_id)
            return
        
        if doc.status == DocumentStatus.INDEXED:
            logger.info("Document already indexed", doc_id=doc_id)
            return
        
        try:
            # Generate embedding
            logger.info("Generating embedding for document", doc_id=doc_id, content_length=len(doc.content))
            embedding = await rag_service.get_embedding(doc.content)
            
            if not embedding:
                raise Exception("Failed to generate embedding")
            
            # Update document with embedding (as array)
            # PostgreSQL will handle the conversion to vector type if pgvector extension is active
            from sqlalchemy import update
            await db.execute(
                update(KBDocument)
                .where(KBDocument.id == doc_id)
                .values(
                    embedding=embedding,
                    status=DocumentStatus.INDEXED
                )
            )
            
            await db.commit()
            logger.info("Document indexed successfully", doc_id=doc_id, embedding_dim=len(embedding))
            
        except Exception as e:
            logger.error("Error indexing document", doc_id=doc_id, error=str(e), exc_info=True)
            from sqlalchemy import update
            await db.execute(
                update(KBDocument)
                .where(KBDocument.id == doc_id)
                .values(status=DocumentStatus.FAILED)
            )
            await db.commit()
            raise
    
    await engine.dispose()


def index_document_sync(doc_id: str):
    """Synchronous wrapper for index_document"""
    asyncio.run(index_document(doc_id))


def enqueue_document(doc_id: str, path: str = None):
    """
    Enqueue a document for indexing
    """
    job = indexer_queue.enqueue(index_document_sync, doc_id)
    logger.info("Document enqueued for indexing", doc_id=doc_id, job_id=job.id)
    return job.id


if __name__ == "__main__":
    # Start RQ worker
    with Connection(redis_conn):
        worker = Worker([indexer_queue])
        worker.work()

