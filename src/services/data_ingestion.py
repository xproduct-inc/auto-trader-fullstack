import asyncio
import websockets
import json
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.utils.redis_client import RedisClient
from src.db.session import get_db
from src.db.models.market_data import MarketData, OrderBook
from src.schemas.market_data import MarketDataCreate, OrderBookCreate

settings = get_settings()

class DataIngestionService:
    def __init__(self):
        self.redis_client = RedisClient()
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.running = False
        self.exchange_urls = {
            "binance": "wss://stream.binance.com:9443/ws",
            "deribit": "wss://www.deribit.com/ws/api/v2"
        }
        self.enabled_exchanges = []

    async def initialize(self):
        """Initialize the data ingestion service"""
        try:
            logger.info("Initializing data ingestion service...")
            await self.redis_client.connect()
            self.running = False
            
            # Validate exchange configurations
            self.enabled_exchanges = self._validate_exchange_configs()
            if not self.enabled_exchanges:
                logger.warning("No valid exchange configurations found - running in mock mode")
                
            logger.info("Data ingestion service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data ingestion service: {e}")
            raise

    def _validate_exchange_configs(self) -> List[str]:
        """Validate exchange configurations and return list of valid exchanges"""
        valid_exchanges = []
        
        for exchange in settings.ENABLED_EXCHANGES:
            if exchange == "binance":
                if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
                    valid_exchanges.append(exchange)
                    logger.info("Binance configuration validated")
                else:
                    logger.warning("Binance API credentials not configured - skipping Binance")
                    
            elif exchange == "deribit":
                # Add Deribit validation when needed
                logger.warning("Deribit integration not yet implemented - skipping")
                
        return valid_exchanges

    async def start_data_streams(self):
        """Initialize and start all data streams"""
        try:
            self.running = True
            logger.info("Starting data streams...")
            
            if not self.enabled_exchanges:
                logger.warning("No valid exchanges configured - running in mock mode")
                await self._start_mock_data_stream()
                return
            
            tasks = []
            for exchange in self.enabled_exchanges:
                for pair in settings.TRADING_PAIRS:
                    tasks.append(self.connect_and_subscribe(exchange, pair))
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error starting data streams: {e}")
            self.running = False
            raise

    async def _start_mock_data_stream(self):
        """Generate mock market data for testing"""
        while self.running:
            try:
                for pair in settings.TRADING_PAIRS:
                    mock_data = self._generate_mock_data(pair)
                    await self.process_market_data("mock", pair, json.dumps(mock_data))
                await asyncio.sleep(1)  # Generate data every second
            except Exception as e:
                logger.error(f"Error generating mock data: {e}")
                await asyncio.sleep(5)

    def _generate_mock_data(self, trading_pair: str) -> Dict:
        """Generate mock market data"""
        import random
        base_price = 50000 if "BTC" in trading_pair else 2000  # Base price for BTC or ETH
        return {
            "s": trading_pair,
            "T": int(datetime.utcnow().timestamp() * 1000),
            "o": base_price * (1 + random.uniform(-0.001, 0.001)),
            "h": base_price * (1 + random.uniform(0, 0.002)),
            "l": base_price * (1 - random.uniform(0, 0.002)),
            "c": base_price * (1 + random.uniform(-0.001, 0.001)),
            "v": random.uniform(1, 100)
        }

    async def connect_and_subscribe(self, exchange: str, trading_pair: str):
        """Establish WebSocket connection and subscribe to market data"""
        while self.running:
            try:
                async with websockets.connect(self.exchange_urls[exchange]) as ws:
                    self.connections[f"{exchange}_{trading_pair}"] = ws
                    
                    # Subscribe to market data
                    subscribe_msg = self.get_subscription_message(exchange, trading_pair)
                    await ws.send(json.dumps(subscribe_msg))
                    
                    while self.running:
                        message = await ws.recv()
                        await self.process_market_data(exchange, trading_pair, message)
                        
            except Exception as e:
                logger.error(f"Connection error for {exchange}_{trading_pair}: {e}")
                await asyncio.sleep(5)  # Wait before reconnecting

    async def process_market_data(self, exchange: str, trading_pair: str, message: str):
        """Process and store market data"""
        try:
            data = json.loads(message)
            
            # Transform data based on exchange format
            normalized_data = self.normalize_market_data(exchange, data)
            if normalized_data:
                # Cache in Redis
                await self.cache_data(exchange, trading_pair, normalized_data)
                
                # Store in TimescaleDB
                await self.store_market_data(normalized_data)
                
        except Exception as e:
            logger.error(f"Error processing market data: {e}")

    async def cache_data(self, exchange: str, trading_pair: str, data: Dict):
        """Cache market data in Redis"""
        key = f"market_data:{exchange}:{trading_pair}"
        await self.redis_client.set_data(key, data, expire=15)
        
        # Publish update for real-time subscribers
        await self.redis_client.publish("market_updates", {
            "exchange": exchange,
            "trading_pair": trading_pair,
            "data": data
        })

    async def store_market_data(self, data: Dict):
        """Store market data in TimescaleDB"""
        async for db in get_db():
            market_data = MarketData(**data)
            db.add(market_data)
            await db.commit()

    def normalize_market_data(self, exchange: str, data: Dict) -> Optional[Dict]:
        """Normalize market data based on exchange format"""
        if exchange == "binance":
            return self.normalize_binance_data(data)
        elif exchange == "deribit":
            return self.normalize_deribit_data(data)
        return None

    def normalize_binance_data(self, data: Dict) -> Optional[Dict]:
        """Normalize Binance market data format"""
        try:
            return {
                "symbol": data["s"],
                "exchange": "binance",
                "timestamp": datetime.fromtimestamp(data["T"] / 1000),
                "open": float(data["o"]),
                "high": float(data["h"]),
                "low": float(data["l"]),
                "close": float(data["c"]),
                "volume": float(data["v"])
            }
        except KeyError:
            return None

    def normalize_deribit_data(self, data: Dict) -> Optional[Dict]:
        """Normalize Deribit market data format"""
        try:
            return {
                "symbol": data["instrument_name"],
                "exchange": "deribit",
                "timestamp": datetime.fromtimestamp(data["timestamp"] / 1000),
                "open": float(data["open"]),
                "high": float(data["high"]),
                "low": float(data["low"]),
                "close": float(data["close"]),
                "volume": float(data["volume"])
            }
        except KeyError:
            return None

    def get_subscription_message(self, exchange: str, trading_pair: str) -> Dict:
        """Generate exchange-specific subscription messages"""
        if exchange == "binance":
            return {
                "method": "SUBSCRIBE",
                "params": [f"{trading_pair.lower()}@kline_1m"],
                "id": 1
            }
        elif exchange == "deribit":
            return {
                "method": "public/subscribe",
                "params": {
                    "channels": [f"chart.trades.{trading_pair}.1"]
                }
            }
        return {}

    async def stop(self):
        """Stop all data streams and cleanup"""
        self.running = False
        for connection in self.connections.values():
            await connection.close()
        await self.redis_client.disconnect() 