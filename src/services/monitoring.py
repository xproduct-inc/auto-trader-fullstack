from prometheus_client import Counter, Gauge, Histogram, Info
from typing import Dict
import time
from loguru import logger

class MonitoringService:
    def __init__(self):
        # Counters
        self.trade_counter = Counter(
            'trading_total_trades',
            'Total number of trades executed',
            ['exchange', 'symbol', 'direction']
        )
        
        self.error_counter = Counter(
            'trading_errors_total',
            'Total number of errors',
            ['service', 'error_type']
        )

        # Gauges
        self.active_positions = Gauge(
            'trading_active_positions',
            'Number of active positions',
            ['exchange']
        )
        
        self.account_balance = Gauge(
            'trading_account_balance',
            'Current account balance',
            ['exchange']
        )
        
        self.strategy_performance = Gauge(
            'trading_strategy_performance',
            'Strategy performance metrics',
            ['strategy_id', 'metric']
        )

        # Histograms
        self.latency_histogram = Histogram(
            'trading_operation_latency_seconds',
            'Latency of trading operations',
            ['operation'],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        
        self.pnl_histogram = Histogram(
            'trading_pnl_distribution',
            'Distribution of trading PnL',
            ['strategy_id']
        )

        # System Info
        self.system_info = Info('trading_system', 'Trading system information')

    def track_trade(self, exchange: str, symbol: str, direction: str):
        """Track executed trade"""
        self.trade_counter.labels(
            exchange=exchange,
            symbol=symbol,
            direction=direction
        ).inc()

    def track_error(self, service: str, error_type: str):
        """Track service error"""
        self.error_counter.labels(
            service=service,
            error_type=error_type
        ).inc()

    def update_positions(self, exchange: str, count: int):
        """Update active positions count"""
        self.active_positions.labels(exchange=exchange).set(count)

    def update_balance(self, exchange: str, balance: float):
        """Update account balance"""
        self.account_balance.labels(exchange=exchange).set(balance)

    def update_strategy_metrics(self, strategy_id: str, metrics: Dict[str, float]):
        """Update strategy performance metrics"""
        for metric, value in metrics.items():
            self.strategy_performance.labels(
                strategy_id=strategy_id,
                metric=metric
            ).set(value)

    def track_latency(self, operation: str):
        """Context manager for tracking operation latency"""
        class LatencyTimer:
            def __init__(self, histogram, operation):
                self.histogram = histogram
                self.operation = operation
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                latency = time.time() - self.start_time
                self.histogram.labels(operation=self.operation).observe(latency)

        return LatencyTimer(self.latency_histogram, operation)

    def record_pnl(self, strategy_id: str, pnl: float):
        """Record PnL for distribution tracking"""
        self.pnl_histogram.labels(strategy_id=strategy_id).observe(pnl)

    def update_system_info(self, info: Dict[str, str]):
        """Update system information"""
        self.system_info.info(info) 