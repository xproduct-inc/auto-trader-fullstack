from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from loguru import logger
from prometheus_client import make_asgi_app

from src.core.config import get_settings
from src.api.v1.router import api_router
from src.services.data_ingestion import DataIngestionService
from src.services.strategy import StrategyGenerator
from src.services.risk_manager import RiskManager
from src.services.trade_executor import TradeExecutor
from src.core.middleware import PrometheusMiddleware
from src.services.monitoring import MonitoringService
from src.core.telemetry import setup_telemetry

settings = get_settings()

# Initialize services
data_service = DataIngestionService()
strategy_generator = StrategyGenerator()
risk_manager = RiskManager()
trade_executor = TradeExecutor()

# Initialize monitoring
monitoring = MonitoringService()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI Trading System API"
)

# Setup telemetry before creating the app
setup_telemetry(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Initializing services...")
        
        # Initialize all services
        await data_service.initialize()
        await strategy_generator.initialize()
        await risk_manager.initialize()
        await trade_executor.initialize()
        
        # Start background tasks
        asyncio.create_task(data_service.start_data_streams())
        asyncio.create_task(trade_executor.manage_open_positions())
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("Shutting down services...")
        
        # Stop all services
        await data_service.stop()
        await strategy_generator.stop()
        await risk_manager.stop()
        await trade_executor.stop()
        
        logger.info("All services shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "data_ingestion": data_service.running,
            "strategy": strategy_generator.assistant_id is not None,
            "risk_manager": risk_manager.redis_client.redis is not None,
            "trade_executor": trade_executor.http_client is not None
        }
    } 