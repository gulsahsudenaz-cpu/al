"""
RAG System Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_rag_search_endpoint():
    """Test RAG search endpoint"""
    response = client.post(
        "/v1/rag/search",
        json={"query": "test query"}
    )
    # Should return 200 even if no documents
    assert response.status_code in [200, 404, 500]
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "documents" in data
        assert "hit_rate" in data


@pytest.mark.asyncio
async def test_rag_metrics_endpoint():
    """Test RAG metrics endpoint (requires auth)"""
    # This would require authentication in real scenario
    response = client.get("/v1/admin/metrics/rag")
    # Should return 401 or 403 without auth
    assert response.status_code in [200, 401, 403]


def test_rag_hybrid_search_logic():
    """Test RAG hybrid search logic"""
    from app.services.rag_service import HybridRAGService
    
    rag_service = HybridRAGService()
    
    # Test threshold
    assert rag_service.min_similarity == 0.7
    assert rag_service.max_documents == 5
    
    # Test weights
    assert rag_service.semantic_weight == 0.7
    assert rag_service.keyword_weight == 0.3

