from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from src.db.session import get_db
from src.services.trade_executor import TradeExecutor
from src.schemas.trading import TradeSignal, TradeResponse

router = APIRouter()
trade_executor = TradeExecutor()

@router.post("/execute", response_model=Dict)
async def execute_trade(
    trade_signal: TradeSignal,
    db: AsyncSession = Depends(get_db)
):
    """Execute a trade"""
    try:
        result = await trade_executor.execute_trade(trade_signal.dict())
        if result:
            return result
        raise HTTPException(status_code=400, detail="Trade execution failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=List[TradeResponse])
async def get_active_trades(
    db: AsyncSession = Depends(get_db)
):
    """Get all active trades"""
    try:
        trades = await db.query(Trade).filter(
            Trade.exit_time.is_(None),
            Trade.status == "FILLED"
        ).all()
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close/{trade_id}", response_model=Dict)
async def close_trade(
    trade_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Close a specific trade"""
    try:
        result = await trade_executor.close_position(trade_id)
        if result:
            return result
        raise HTTPException(status_code=400, detail="Failed to close trade")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 