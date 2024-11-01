from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from src.db.session import get_db
from src.services.strategy import StrategyGenerator
from src.schemas.trading import TradeResponse

router = APIRouter()
strategy_generator = StrategyGenerator()

@router.post("/generate", response_model=Dict)
async def generate_strategy(
    market_data: Dict,
    db: AsyncSession = Depends(get_db)
):
    """Generate trading strategy based on market data"""
    try:
        if not strategy_generator.assistant_id:
            await strategy_generator.initialize()
            
        strategy = await strategy_generator.generate_strategy(market_data)
        return strategy
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/{strategy_id}", response_model=Dict)
async def get_strategy_performance(
    strategy_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics for a strategy"""
    metrics = await db.query(PerformanceMetrics)\
        .filter(PerformanceMetrics.strategy_id == strategy_id)\
        .order_by(PerformanceMetrics.timestamp.desc())\
        .first()
        
    if not metrics:
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    return metrics 