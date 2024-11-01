from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta

from src.db.session import get_db
from src.schemas.market_data import MarketDataResponse, OrderBookResponse
from src.services.data_ingestion import DataIngestionService
from src.utils.redis_client import RedisClient

router = APIRouter()
redis_client = RedisClient()

@router.get("/latest/{exchange}/{trading_pair}", response_model=MarketDataResponse)
async def get_latest_market_data(
    exchange: str,
    trading_pair: str,
    db: AsyncSession = Depends(get_db)
):
    """Get latest market data for a specific trading pair"""
    # Try Redis first
    key = f"market_data:{exchange}:{trading_pair}"
    cached_data = await redis_client.get_data(key)
    if cached_data:
        return cached_data

    # Fallback to database
    query = (
        db.query(MarketData)
        .filter(
            MarketData.exchange == exchange,
            MarketData.symbol == trading_pair
        )
        .order_by(MarketData.timestamp.desc())
        .first()
    )
    
    if not query:
        raise HTTPException(status_code=404, detail="Market data not found")
    
    return query

@router.get("/historical/{exchange}/{trading_pair}", response_model=List[MarketDataResponse])
async def get_historical_market_data(
    exchange: str,
    trading_pair: str,
    start_time: datetime,
    end_time: datetime = None,
    db: AsyncSession = Depends(get_db)
):
    """Get historical market data for a specific trading pair"""
    if not end_time:
        end_time = datetime.utcnow()

    query = (
        db.query(MarketData)
        .filter(
            MarketData.exchange == exchange,
            MarketData.symbol == trading_pair,
            MarketData.timestamp.between(start_time, end_time)
        )
        .order_by(MarketData.timestamp.asc())
    )
    
    return await query.all() 