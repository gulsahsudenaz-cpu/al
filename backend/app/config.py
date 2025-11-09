"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    API_V1_PREFIX: str = "/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "POSTGRES_URL",  # Railway uses POSTGRES_URL
            "postgresql://user:password@localhost:5432/chatbot"
        )
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    
    # Redis
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        os.getenv(
            "REDISCLOUD_URL",  # Railway Redis plugin
            "redis://localhost:6379/0"
        )
    )
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
    
    # Vector DB
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", DATABASE_URL)  # pgvector
    VECTOR_INDEX_TYPE: str = os.getenv("VECTOR_INDEX_TYPE", "HNSW")
    
    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL", None)
    MODEL: str = os.getenv("MODEL", "gpt-4-turbo")
    LLM_DAILY_COST_LIMIT: float = float(os.getenv("LLM_DAILY_COST_LIMIT", "50.0"))
    LLM_MAX_TOKENS_PER_REQUEST: int = int(os.getenv("LLM_MAX_TOKENS_PER_REQUEST", "512"))
    LLM_CACHE_TTL: int = int(os.getenv("LLM_CACHE_TTL", "86400"))
    
    # RAG
    RAG_MIN_SIMILARITY: float = float(os.getenv("RAG_MIN_SIMILARITY", "0.7"))
    RAG_MAX_DOCUMENTS: int = int(os.getenv("RAG_MAX_DOCUMENTS", "5"))
    RAG_HYBRID_WEIGHTS: dict = {"semantic": 0.7, "keyword": 0.3}
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OTP_LENGTH: int = 6
    OTP_TTL: int = 300  # 5 minutes
    MAX_MEDIA_SIZE_MB: int = 15
    MAX_MESSAGES_PER_MINUTE: int = 30
    MAX_SESSIONS_PER_USER: int = 3
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30000  # 30 seconds
    WS_SESSION_TIMEOUT: int = 1800  # 30 minutes
    WS_IDLE_WARNING: int = 1500  # 25 minutes
    
    # Context
    CONTEXT_WINDOW_SIZE: int = 10
    MAX_CONTEXT_TOKENS: int = 2000
    
    # Media Storage
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL", None)
    S3_ACCESS_KEY: Optional[str] = os.getenv("S3_ACCESS_KEY", None)
    S3_SECRET_KEY: Optional[str] = os.getenv("S3_SECRET_KEY", None)
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME", None)
    USE_MINIO: bool = os.getenv("USE_MINIO", "False").lower() == "true"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", None)
    TELEGRAM_WEBHOOK_URL: Optional[str] = os.getenv("TELEGRAM_WEBHOOK_URL", None)
    
    # Monitoring
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

