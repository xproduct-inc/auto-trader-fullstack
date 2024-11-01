from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

from src.services.technical_analysis import TechnicalAnalysis
from src.services.strategy import StrategyGenerator

@dataclass
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Dict]
    equity_curve: List[float]
    performance_by_regime: Dict[str, Dict]  # Performance in different volatility regimes
    options_metrics: Dict[str, float]       # Options-specific metrics

class Backtester:
    def __init__(self):
        self.ta = TechnicalAnalysis()
        self.strategy_generator = StrategyGenerator()
        
    async def run_backtest(
        self, 
        historical_data: pd.DataFrame,
        options_chain_data: Dict,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000,
        position_size_pct: float = 0.02
    ) -> BacktestResult:
        """Run backtest on historical data"""
        try:
            trades = []
            equity = [initial_capital]
            current_capital = initial_capital
            
            # Prepare data
            data = self._prepare_data(historical_data, options_chain_data)
            
            # Iterate through each timeframe
            for timestamp, frame in data.iterrows():
                if start_date <= timestamp <= end_date:
                    # Get market context
                    market_data = self._get_market_snapshot(frame, data, timestamp)
                    
                    # Generate strategy
                    strategy = await self.strategy_generator.generate_strategy(market_data)
                    
                    # Execute strategy if valid
                    if strategy:
                        trade_result = self._execute_trade(
                            strategy, 
                            market_data, 
                            current_capital,
                            position_size_pct
                        )
                        
                        if trade_result:
                            trades.append(trade_result)
                            current_capital += trade_result['pnl']
                            equity.append(current_capital)
            
            # Calculate performance metrics
            result = self._calculate_performance_metrics(
                trades,
                equity,
                data,
                initial_capital
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            raise

    def _prepare_data(
        self, 
        historical_data: pd.DataFrame,
        options_chain_data: Dict
    ) -> pd.DataFrame:
        """Prepare and align data for backtesting"""
        # Calculate all technical indicators
        df = historical_data.copy()
        
        # Price-based indicators
        for period in [20, 50, 200]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        
        for period in [9, 21, 55]:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        # Volatility indicators
        df['atr'] = self._calculate_atr(df)
        df['historical_volatility'] = self._calculate_historical_volatility(df)
        
        # Options data
        df['iv_rank'] = self._calculate_iv_rank_series(df, options_chain_data)
        df['put_call_ratio'] = self._calculate_pcr_series(options_chain_data)
        
        return df

    def _get_market_snapshot(
        self, 
        current_frame: pd.Series,
        full_data: pd.DataFrame,
        timestamp: datetime
    ) -> Dict:
        """Get complete market context at a point in time"""
        return {
            "price_data": {
                "open": current_frame['open'],
                "high": current_frame['high'],
                "low": current_frame['low'],
                "close": current_frame['close'],
                "volume": current_frame['volume']
            },
            "technical_indicators": {
                "sma_200": current_frame['sma_200'],
                "ema_21": current_frame['ema_21'],
                "atr": current_frame['atr'],
                "historical_volatility": current_frame['historical_volatility']
            },
            "options_data": {
                "iv_rank": current_frame['iv_rank'],
                "put_call_ratio": current_frame['put_call_ratio']
            },
            "timestamp": timestamp
        }

    def _execute_trade(
        self,
        strategy: Dict,
        market_data: Dict,
        current_capital: float,
        position_size_pct: float
    ) -> Optional[Dict]:
        """Simulate trade execution"""
        try:
            position_size = current_capital * position_size_pct
            entry_price = market_data['price_data']['close']
            
            # Simulate options pricing and Greeks
            options_prices = self._simulate_options_prices(
                entry_price,
                market_data['options_data']['iv_rank'],
                strategy
            )
            
            # Calculate trade result
            exit_price = self._simulate_exit_price(strategy, market_data)
            pnl = self._calculate_trade_pnl(
                strategy,
                options_prices,
                position_size
            )
            
            return {
                "entry_time": market_data['timestamp'],
                "strategy_type": strategy['strategy_type'],
                "position_size": position_size,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl": pnl,
                "options_data": options_prices
            }
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return None

    def _calculate_performance_metrics(
        self,
        trades: List[Dict],
        equity_curve: List[float],
        data: pd.DataFrame,
        initial_capital: float
    ) -> BacktestResult:
        """Calculate comprehensive performance metrics"""
        try:
            # Basic metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            losing_trades = total_trades - winning_trades
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            total_pnl = sum(t['pnl'] for t in trades)
            
            # Advanced metrics
            returns = pd.Series(equity_curve).pct_change().dropna()
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            max_drawdown = self._calculate_max_drawdown(equity_curve)
            
            # Performance by volatility regime
            regime_performance = self._analyze_regime_performance(trades, data)
            
            # Options-specific metrics
            options_metrics = self._calculate_options_metrics(trades)
            
            return BacktestResult(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                trades=trades,
                equity_curve=equity_curve,
                performance_by_regime=regime_performance,
                options_metrics=options_metrics
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            raise 