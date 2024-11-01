from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from src.db.base import Base

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderBook(Base):
    __tablename__ = "order_book"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    bids = Column(JSON, nullable=False)
    asks = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 