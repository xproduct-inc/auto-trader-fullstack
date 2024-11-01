from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Trading System"
    API_PORT: int = 9000
    ENVIRONMENT: str = "development"
    
    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    
    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    
    # Exchange Settings
    ENABLED_EXCHANGES: List[str] = ["binance", "deribit"]
    TRADING_PAIRS: List[str] = ["BTC-USD", "ETH-USD"]
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    BINANCE_TESTNET: bool = False
    BINANCE_TESTNET_BASE_URL: Optional[str] = None
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Risk Management Settings
    MAX_POSITION_SIZE: float = 1000.0
    MAX_DAILY_TRADES: int = 10
    STOP_LOSS_PERCENTAGE: float = 0.02
    MAX_DRAWDOWN: float = 0.05
    RISK_PER_TRADE: float = 0.01

    @property
    def RISK_LIMITS(self) -> Dict:
        return {
            "max_position_size": self.MAX_POSITION_SIZE,
            "max_daily_trades": self.MAX_DAILY_TRADES,
            "stop_loss_percentage": self.STOP_LOSS_PERCENTAGE,
            "max_drawdown": self.MAX_DRAWDOWN
        }
    
    # Analytics Settings
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_DB: str = "trading_analytics"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    
    # Telemetry Settings
    SENTRY_DSN: Optional[str] = "https://dummy@dummy.ingest.sentry.io/123456"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://jaeger:4317"
    OTEL_SERVICE_NAME: str = "ai-trading"
    
    # Monitoring Settings
    GRAFANA_ADMIN_PASSWORD: str
    PROMETHEUS_RETENTION_DAYS: int = 15
    
    # Feature Flags
    ENABLE_TESTNET: bool = False
    ENABLE_PAPER_TRADING: bool = False
    ENABLE_MOCK_RESPONSES: bool = False
    ENABLE_DEBUG_MODE: bool = False
    
    # Performance Settings
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_TIMEOUT: int = 60
    HTTP_TIMEOUT: int = 30
    MAX_CONNECTIONS: int = 100
    POOL_SIZE: int = 20
    
    # Cache Settings
    CACHE_TTL: int = 15
    MARKET_DATA_CACHE_TTL: int = 15
    STRATEGY_CACHE_TTL: int = 300
    
    # Logging Settings
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()