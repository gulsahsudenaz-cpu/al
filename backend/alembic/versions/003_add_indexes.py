"""Add Database Indexes

Revision ID: 003_add_indexes
Revises: 002_add_user_model
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_indexes'
down_revision = '002_add_user_model'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Vector index for embeddings (HNSW for pgvector)
    # Note: This requires pgvector extension to be enabled
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_kb_documents_embedding 
        ON kb_documents 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    # Full-text search index for content
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_kb_documents_content_fts 
        ON kb_documents 
        USING GIN (to_tsvector('english', COALESCE(content, '')))
    """)
    
    # Composite index for status and created_at
    op.create_index(
        'idx_kb_documents_status_created',
        'kb_documents',
        ['status', 'created_at']
    )
    
    # Index for rag_metrics hit_rate and created_at
    op.create_index(
        'idx_rag_metrics_hit_rate_created',
        'rag_metrics',
        ['hit_rate', 'created_at']
    )
    
    # Index for llm_usage model and created_at
    op.create_index(
        'idx_llm_usage_model_created',
        'llm_usage',
        ['model', 'created_at']
    )


def downgrade() -> None:
    op.drop_index('idx_llm_usage_model_created', table_name='llm_usage')
    op.drop_index('idx_rag_metrics_hit_rate_created', table_name='rag_metrics')
    op.drop_index('idx_kb_documents_status_created', table_name='kb_documents')
    op.execute("DROP INDEX IF EXISTS idx_kb_documents_content_fts")
    op.execute("DROP INDEX IF EXISTS idx_kb_documents_embedding")

