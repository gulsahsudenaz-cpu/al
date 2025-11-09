"""
Prometheus Metrics Endpoint
"""
from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

# Metrics
rag_requests_total = Counter(
    'rag_requests_total',
    'Total number of RAG requests',
    ['status']
)

rag_response_time = Histogram(
    'rag_response_time_seconds',
    'RAG response time in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

llm_requests_total = Counter(
    'llm_requests_total',
    'Total number of LLM requests',
    ['model', 'status']
)

llm_cost_usd = Counter(
    'llm_cost_usd_total',
    'Total LLM cost in USD',
    ['model']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total LLM tokens',
    ['model', 'type']
)

websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

chat_messages_total = Counter(
    'chat_messages_total',
    'Total number of chat messages',
    ['role']
)

rag_hit_rate = Gauge(
    'rag_hit_rate',
    'RAG hit rate (0-1)'
)

database_connections = Gauge(
    'database_connections_active',
    'Number of active database connections'
)


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

