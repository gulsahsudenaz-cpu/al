"""
OpenTelemetry Tracing Setup for FastAPI
"""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
import os


def setup_tracing(service_name: str = "chatbot-backend", otlp_endpoint: str = None):
    """Setup OpenTelemetry tracing"""
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    
    if not otlp_endpoint:
        print("⚠️  OpenTelemetry endpoint not configured. Tracing disabled.")
        return
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "2.0.0",
    })
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Create OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{otlp_endpoint}/v1/traces",
        headers={}
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument libraries
    try:
        RedisInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()
        OpenAIInstrumentor().instrument()
    except Exception as e:
        print(f"⚠️  Instrumentation error: {e}")
    
    print(f"✅ OpenTelemetry tracing enabled: {otlp_endpoint}")
    return tracer_provider


def instrument_app(app, excluded_urls: str = "health,metrics"):
    """Instrument FastAPI app with OpenTelemetry"""
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls=excluded_urls.split(",")
    )

