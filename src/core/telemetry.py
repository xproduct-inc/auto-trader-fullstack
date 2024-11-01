from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from loguru import logger

from src.core.config import get_settings

settings = get_settings()

def setup_telemetry(app):
    """Setup OpenTelemetry and Sentry"""
    try:
        # Setup OpenTelemetry
        tracer_provider = TracerProvider()
        processor = BatchSpanProcessor(OTLPSpanExporter())
        tracer_provider.add_span_processor(processor)
        trace.set_tracer_provider(tracer_provider)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        
        # Setup Sentry only if DSN is provided and valid
        if settings.SENTRY_DSN and settings.SENTRY_DSN.startswith(('http://', 'https://')):
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                integrations=[
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=1.0,
            )
            # Add Sentry middleware
            app.add_middleware(SentryAsgiMiddleware)
            logger.info("Sentry integration enabled")
        else:
            logger.warning("Sentry DSN not provided or invalid - Sentry integration disabled")
            
    except Exception as e:
        logger.warning(f"Telemetry setup failed: {e} - Continuing without telemetry")