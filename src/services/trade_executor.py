from typing import Dict, Optional, List
import asyncio
from datetime import datetime
from loguru import logger
import httpx
from decimal import Decimal
from sqlalchemy import select

from src.core.config import get_settings
from src.utils.redis_client import RedisClient
from src.db.session import get_db
from src.db.models.trading import Trade
from src.services.risk_manager import RiskManager

settings = get_settings()

class TradeExecutor:
    def __init__(self):
        self.redis_client = RedisClient()
        self.risk_manager = RiskManager()
        self.active_orders: Dict[str, Dict] = {}
        self.http_client = httpx.AsyncClient()
        self.exchange_apis = {
            "binance": {
                "base_url": "https://api.binance.com",
                "endpoints": {
                    "order": "/api/v3/order",
                    "position": "/api/v3/position"
                }
            },
            "deribit": {
                "base_url": "https://www.deribit.com/api/v2",
                "endpoints": {
                    "order": "/private/buy",
                    "position": "/private/get_position"
                }
            }
        }

    async def initialize(self):
        """Initialize trade executor"""
        try:
            await self.redis_client.connect()
            await self.risk_manager.initialize()
            # Load active orders from database
            await self._load_active_trades()
        except Exception as e:
            logger.error(f"Error initializing trade executor: {e}")
            raise

    async def _load_active_trades(self):
        """Load active trades from database"""
        async for db in get_db():
            try:
                query = select(Trade).where(
                    Trade.exit_time.is_(None),
                    Trade.status == "FILLED"
                )
                result = await db.execute(query)
                trades = result.scalars().all()
                
                for trade in trades:
                    self.active_orders[str(trade.id)] = {
                        "order_id": str(trade.id),
                        "symbol": trade.symbol,
                        "side": trade.direction,
                        "price": trade.entry_price,
                        "quantity": trade.quantity,
                        "status": trade.status,
                        "exchange": trade.exchange if hasattr(trade, 'exchange') else "binance"
                    }
                    
            except Exception as e:
                logger.error(f"Error loading active trades: {e}")
                raise

    async def execute_trade(self, trade_signal: Dict) -> Optional[Dict]:
        """Execute trade on the exchange"""
        try:
            # Validate trade with risk manager
            if not await self.risk_manager.validate_trade(trade_signal):
                logger.warning("Trade rejected by risk manager")
                return None

            # Calculate position size
            account_balance = await self._get_account_balance(trade_signal["exchange"])
            position_size = await self.risk_manager.calculate_position_size(
                trade_signal, 
                account_balance
            )

            # Place order
            order = await self._place_order(trade_signal, position_size)
            if order:
                # Track order
                self.active_orders[order["order_id"]] = order
                
                # Store trade in database
                await self._store_trade(order)
                
                # Update risk metrics
                await self.risk_manager.update_risk_metrics(order)
                
                return order

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None

    async def manage_open_positions(self):
        """Monitor and manage open positions"""
        while True:
            try:
                for order_id, order in list(self.active_orders.items()):
                    # Check order status
                    status = await self._check_order_status(order)
                    
                    if status["status"] == "FILLED":
                        # Update position tracking
                        await self._update_position(order_id, status)
                        
                    elif status["status"] == "CANCELLED":
                        # Remove from tracking
                        await self._cleanup_order(order_id)

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                logger.error(f"Error managing positions: {e}")
                await asyncio.sleep(5)

    async def update_trade_status(self, trade_id: str, status: Dict):
        """Update trade status and related metrics"""
        try:
            async for db in get_db():
                trade = await db.query(Trade).filter(Trade.id == trade_id).first()
                if trade:
                    trade.status = status["status"]
                    if status["status"] == "FILLED":
                        trade.exit_time = datetime.utcnow()
                        trade.exit_price = status["price"]
                        trade.pnl = self._calculate_pnl(trade, status["price"])
                    
                    await db.commit()
                    
                    # Update risk metrics
                    await self.risk_manager.update_risk_metrics(trade)

        except Exception as e:
            logger.error(f"Error updating trade status: {e}")
            raise

    async def _place_order(self, trade_signal: Dict, position_size: float) -> Optional[Dict]:
        """Place order on exchange"""
        try:
            exchange = trade_signal["exchange"]
            api_config = self.exchange_apis[exchange]
            
            payload = self._format_order_payload(
                exchange,
                trade_signal,
                position_size
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_config['base_url']}{api_config['endpoints']['order']}",
                    json=payload,
                    headers=self._get_auth_headers(exchange)
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Order placement failed: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    async def _check_order_status(self, order: Dict) -> Dict:
        """Check order status on exchange"""
        try:
            exchange = order["exchange"]
            api_config = self.exchange_apis[exchange]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{api_config['base_url']}{api_config['endpoints']['order']}",
                    params={"orderId": order["order_id"]},
                    headers=self._get_auth_headers(exchange)
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Status check failed: {response.text}")
                    return {"status": "UNKNOWN"}

        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            return {"status": "UNKNOWN"}

    def _format_order_payload(self, exchange: str, signal: Dict, size: float) -> Dict:
        """Format order payload for specific exchange"""
        if exchange == "binance":
            return {
                "symbol": signal["symbol"],
                "side": signal["action"],
                "type": "LIMIT",
                "quantity": size,
                "price": signal["entry_price"],
                "timeInForce": "GTC",
                "stopPrice": signal["stop_loss"],
                "takeProfit": signal["take_profit"]
            }
        elif exchange == "deribit":
            return {
                "instrument_name": signal["symbol"],
                "amount": size,
                "type": "limit",
                "price": signal["entry_price"],
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"]
            }
        return {}

    def _get_auth_headers(self, exchange: str) -> Dict:
        """Get authentication headers for exchange API"""
        # Implementation depends on exchange authentication requirements
        return {}

    async def _store_trade(self, order: Dict):
        """Store trade in database"""
        async for db in get_db():
            try:
                trade = Trade(
                    symbol=order["symbol"],
                    direction=order["side"],
                    entry_price=order["price"],
                    quantity=order["quantity"],
                    status=order["status"],
                    strategy_id=order.get("strategy_id"),
                    entry_time=datetime.utcnow()
                )
                db.add(trade)
                await db.commit()

            except Exception as e:
                logger.error(f"Error storing trade: {e}")
                await db.rollback()
                raise

    def _calculate_pnl(self, trade: Trade, exit_price: float) -> float:
        """Calculate PnL for a trade"""
        try:
            entry_value = float(trade.entry_price) * float(trade.quantity)
            exit_value = float(exit_price) * float(trade.quantity)
            
            if trade.direction == "LONG":
                return exit_value - entry_value
            else:
                return entry_value - exit_value

        except Exception as e:
            logger.error(f"Error calculating PnL: {e}")
            return 0.0

    async def stop(self):
        """Cleanup resources"""
        await self.redis_client.disconnect()
        await self.risk_manager.stop()
        await self.http_client.aclose() 