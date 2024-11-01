from fastapi import APIRouter
from src.api.v1.endpoints import market_data, strategy, risk, trading

api_router = APIRouter()

# Market Data endpoints
api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["market-data"]
)

# Strategy endpoints
api_router.include_router(
    strategy.router,
    prefix="/strategy",
    tags=["strategy"]
)

# Risk Management endpoints
api_router.include_router(
    risk.router,
    prefix="/risk",
    tags=["risk"]
)

# Trading endpoints
api_router.include_router(
    trading.router,
    prefix="/trading",
    tags=["trading"]
) 