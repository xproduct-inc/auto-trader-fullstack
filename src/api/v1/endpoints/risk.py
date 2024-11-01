from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from src.db.session import get_db
from src.services.risk_manager import RiskManager
from src.schemas.trading import TradeSignal

router = APIRouter()
risk_manager = RiskManager()

@router.post("/validate-trade", response_model=Dict[str, bool])
async def validate_trade(
    trade_signal: TradeSignal,
    db: AsyncSession = Depends(get_db)
):
    """Validate trade against risk parameters"""
    try:
        is_valid = await risk_manager.validate_trade(trade_signal.dict())
        return {"is_valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=Dict)
async def get_risk_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get current risk metrics"""
    try:
        metrics = await risk_manager.check_risk_limits()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-position-size", response_model=Dict)
async def calculate_position_size(
    trade_signal: TradeSignal,
    account_balance: float,
    db: AsyncSession = Depends(get_db)
):
    """Calculate appropriate position size"""
    try:
        size = await risk_manager.calculate_position_size(
            trade_signal.dict(),
            account_balance
        )
        return {"position_size": size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 