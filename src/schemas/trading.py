from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TradeDirection(str, Enum):
    LONG = "long"
    SHORT = "short"

class TradeSignal(BaseModel):
    """Incoming trade signal schema"""
    symbol: str
    action: TradeDirection
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: Optional[float] = None
    strategy_id: Optional[str] = None
    timeframe: Optional[str] = "1h"
    metadata: Optional[Dict] = Field(default_factory=dict)

class TradeCreate(BaseModel):
    """Schema for creating a new trade"""
    symbol: str
    direction: TradeDirection
    entry_price: float
    quantity: float
    strategy_id: str
    stop_loss: float
    take_profit: float
    metadata: Optional[Dict] = Field(default_factory=dict)

class TradeResponse(BaseModel):
    """Schema for trade response"""
    id: int
    symbol: str
    direction: TradeDirection
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    status: OrderStatus
    strategy_id: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    trade_data: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PerformanceMetricsResponse(BaseModel):
    """Schema for performance metrics"""
    id: int
    strategy_id: str
    timestamp: datetime
    total_trades: int
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_pnl: Optional[float] = None
    metrics_data: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True