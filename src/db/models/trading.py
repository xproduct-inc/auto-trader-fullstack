from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON
from sqlalchemy.sql import func
import enum
from src.db.base import Base

class OrderStatus(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TradeDirection(enum.Enum):
    LONG = "long"
    SHORT = "short"

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    direction = Column(Enum(TradeDirection), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    quantity = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    strategy_id = Column(String, nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True))
    pnl = Column(Float)
    trade_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    total_trades = Column(Integer, nullable=False)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    total_pnl = Column(Float)
    metrics_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 