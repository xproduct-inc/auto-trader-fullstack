from typing import Dict, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import func, select
from decimal import Decimal

from src.core.config import get_settings
from src.db.session import get_db
from src.db.models.trading import Trade, PerformanceMetrics
from src.utils.redis_client import RedisClient

settings = get_settings()

class RiskManager:
    def __init__(self):
        self.redis_client = RedisClient()
        self.risk_limits = settings.RISK_LIMITS
        self.daily_trades: Dict[str, int] = {}
        self.positions: Dict[str, Dict] = {}

    async def initialize(self):
        """Initialize risk manager"""
        await self.redis_client.connect()
        await self._load_active_positions()

    async def validate_trade(self, trade_signal: Dict) -> bool:
        """Validate trade against risk parameters"""
        try:
            # Check daily trade limit
            today = datetime.utcnow().date().isoformat()
            symbol_key = f"{trade_signal['symbol']}_{today}"
            
            if self.daily_trades.get(symbol_key, 0) >= self.risk_limits["max_daily_trades"]:
                logger.warning(f"Daily trade limit reached for {trade_signal['symbol']}")
                return False

            # Validate position size
            if not await self._validate_position_size(trade_signal):
                return False

            # Check maximum drawdown
            if not await self._check_drawdown_limit():
                return False

            # Validate stop loss percentage
            if not self._validate_stop_loss(trade_signal):
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False

    async def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """Calculate appropriate position size based on risk parameters"""
        try:
            # Calculate risk amount per trade
            risk_per_trade = account_balance * self.risk_limits["stop_loss_percentage"]
            
            # Calculate position size based on stop loss
            price_diff = abs(signal["entry_price"] - signal["stop_loss"])
            risk_per_unit = price_diff / signal["entry_price"]
            
            position_size = risk_per_trade / risk_per_unit
            
            # Apply maximum position size limit
            position_size = min(position_size, self.risk_limits["max_position_size"])
            
            return float(Decimal(str(position_size)).quantize(Decimal('0.00001')))

        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            raise

    async def update_risk_metrics(self, trade: Trade):
        """Update risk metrics after trade execution"""
        try:
            # Update daily trade count
            today = datetime.utcnow().date().isoformat()
            symbol_key = f"{trade.symbol}_{today}"
            self.daily_trades[symbol_key] = self.daily_trades.get(symbol_key, 0) + 1

            # Update position tracking
            if trade.status == "FILLED":
                await self._update_position(trade)

            # Calculate and store risk metrics
            await self._calculate_risk_metrics()

        except Exception as e:
            logger.error(f"Error updating risk metrics: {e}")
            raise

    async def check_risk_limits(self) -> Dict[str, bool]:
        """Check all risk limits and return status"""
        return {
            "daily_trades_limit": await self._check_daily_trades_limit(),
            "drawdown_limit": await self._check_drawdown_limit(),
            "exposure_limit": await self._check_exposure_limit()
        }

    async def _validate_position_size(self, trade_signal: Dict) -> bool:
        """Validate position size against limits"""
        try:
            current_exposure = sum(
                pos["size"] * pos["price"] 
                for pos in self.positions.values()
            )
            
            new_exposure = trade_signal["position_size"] * trade_signal["entry_price"]
            
            if current_exposure + new_exposure > self.risk_limits["max_position_size"]:
                logger.warning("Position size exceeds maximum exposure limit")
                return False
                
            return True

        except Exception as e:
            logger.error(f"Error validating position size: {e}")
            return False

    def _validate_stop_loss(self, trade_signal: Dict) -> bool:
        """Validate stop loss percentage"""
        try:
            stop_loss_pct = abs(trade_signal["entry_price"] - trade_signal["stop_loss"]) / trade_signal["entry_price"]
            
            if stop_loss_pct > self.risk_limits["stop_loss_percentage"]:
                logger.warning("Stop loss percentage exceeds maximum limit")
                return False
                
            return True

        except Exception as e:
            logger.error(f"Error validating stop loss: {e}")
            return False

    async def _load_active_positions(self):
        """Load active positions from database"""
        async for db in get_db():
            try:
                # Updated to use SQLAlchemy 2.0 style
                query = select(Trade).where(
                    Trade.exit_time.is_(None),
                    Trade.status == "FILLED"
                )
                result = await db.execute(query)
                active_trades = result.scalars().all()
                
                for trade in active_trades:
                    self.positions[trade.id] = {
                        "symbol": trade.symbol,
                        "size": trade.quantity,
                        "price": trade.entry_price,
                        "direction": trade.direction
                    }

            except Exception as e:
                logger.error(f"Error loading active positions: {e}")
                raise

    async def _calculate_risk_metrics(self):
        """Calculate and store current risk metrics"""
        async for db in get_db():
            try:
                # Updated to use SQLAlchemy 2.0 style
                query = select(Trade).where(
                    Trade.exit_time >= datetime.utcnow() - timedelta(days=30)
                )
                result = await db.execute(query)
                trades = result.scalars().all()
                
                cumulative_pnl = 0
                max_drawdown = 0
                peak = 0
                
                for trade in trades:
                    if trade.pnl:
                        cumulative_pnl += trade.pnl
                        peak = max(peak, cumulative_pnl)
                        drawdown = peak - cumulative_pnl
                        max_drawdown = max(max_drawdown, drawdown)

                # Store metrics in Redis for quick access
                await self.redis_client.set_data(
                    "risk_metrics",
                    {
                        "max_drawdown": max_drawdown,
                        "current_exposure": sum(
                            pos["size"] * pos["price"] 
                            for pos in self.positions.values()
                        ),
                        "active_positions": len(self.positions),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            except Exception as e:
                logger.error(f"Error calculating risk metrics: {e}")
                raise

    async def stop(self):
        """Cleanup resources"""
        await self.redis_client.disconnect() 