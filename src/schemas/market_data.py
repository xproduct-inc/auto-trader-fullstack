from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List

class MarketDataBase(BaseModel):
    symbol: str
    exchange: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketDataCreate(MarketDataBase):
    pass

class MarketDataResponse(MarketDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderBookEntry(BaseModel):
    price: float
    quantity: float

class OrderBookBase(BaseModel):
    symbol: str
    exchange: str
    timestamp: datetime
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]

class OrderBookCreate(OrderBookBase):
    pass

class OrderBookResponse(OrderBookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 