# AI Trading System: Technology Stack Overview
1.1 Backend Infrastructure
yamlCopyCore Technologies:
  - FastAPI: Main API framework
  - Python 3.11+: Base language
  - Redis Stack: Real-time data & caching
  - TimescaleDB: Time-series data
  - ClickHouse: Analytics storage

Key Libraries:
  - Pydantic v2: Data validation
  - SQLAlchemy 2.0: Database ORM
  - Polars: Data processing
  - NumPy: Numerical computations
  - websockets: Real-time connections
  - httpx: HTTP client
  - aiocache: Async caching
  - asyncio: Async operations

AI/ML Stack:
  - LangGraph: Agent orchestration
  - OpenAI SDK: Assistant API
  - Langchain: LLM operations

Monitoring:
  - Prometheus: Metrics
  - Grafana: Dashboards
  - OpenTelemetry: Tracing
  - Sentry: Error tracking
  - Loguru: Logging
1.2 Frontend Infrastructure
yamlCopyCore Framework:
  - Next.js 14: React framework
  - TypeScript: Type safety
  - Tailwind CSS: Styling
  - Shadcn/ui: Components

State Management:
  - TanStack Query: Server state
  - Zustand: Client state
  - Jotai: Atomic state

Visualization:
  - TradingView Charts: Financial charts
  - Recharts: Analytics charts
  - D3.js: Custom visualizations

Real-time:
  - SSE: One-way updates
  - Socket.io: Bi-directional


Backend Setup

pythonCopy"""
Create a FastAPI project structure with the following requirements:

1. Project structure:
src/
  ├── api/            # API routes
  ├── core/           # Core configuration
  ├── db/             # Database models
  ├── services/       # Business logic
  ├── schemas/        # Pydantic models
  ├── agents/         # Trading agents
  └── utils/          # Utilities

2. Configuration:
   - Environment-based settings
   - Database connections
   - API configurations
   - Logging setup

3. Dependencies:
   - FastAPI
   - Pydantic v2
   - SQLAlchemy 2.0
   - Redis Stack
   - Other core libraries

Create the basic project structure with configuration files and dependency management.
"""

# Example main.py structure needed
Prompt for Claude (Database Setup):
pythonCopy"""
Create database models and connections for:

1. TimescaleDB models for:
   - Market data
   - Options chains
   - Trading history
   - Performance metrics

2. Redis models for:
   - Real-time data
   - Caching
   - Pub/Sub events

3. Requirements:
   - Async operations
   - Connection pooling
   - Error handling
   - Migration support

Use SQLAlchemy 2.0 for TimescaleDB and aioredis for Redis.
"""


# AI Trading System: Implementation Guide 

## System Overview
Build an autonomous crypto trading system that uses OpenAI's Assistant API for strategy generation, with real-time data processing and risk management.

## Core Components Implementation Guide

### 1. Data Ingestion Service
**Prompt Template for AI Assistant:**
```
Create a Python class for real-time crypto data ingestion with the following requirements:

1. Class name: DataIngestionService
2. Features needed:
   - Websocket connections to Binance and other exchanges
   - Real-time OHLCV and orderbook data collection
   - Data normalization and validation
   - Redis caching with 15-second refresh
   - Error handling and automatic reconnection
3. Required methods:
   - start_data_streams()
   - process_market_data()
   - cache_data()
   - get_latest_data()
4. Use these libraries:
   - websockets
   - redis
   - pandas
   - asyncio

The data should be structured for quick access by the strategy generator.
```

### 2. Strategy Generation Service
**Prompt Template for AI Assistant:**
```
Create a Python class for dynamic trading strategy generation using OpenAI Assistant API with these requirements:

1. Class name: StrategyGenerator
2. Features needed:
   - OpenAI Assistant API integration
   - Real-time strategy generation every 15 seconds
   - Code validation and safe execution
   - Strategy performance tracking
3. Required methods:
   - generate_strategy()
   - validate_strategy_code()
   - execute_strategy()
   - update_performance_metrics()
4. Input data format:
{
    "market_data": {
        "symbol": str,
        "timestamp": datetime,
        "ohlcv": dict,
        "orderbook": dict
    },
    "current_strategy": {
        "code": str,
        "performance": dict
    }
}
```

### 3. Risk Management System
**Prompt Template for AI Assistant:**
```
Create a Python class for real-time risk management with these requirements:

1. Class name: RiskManager
2. Features needed:
   - Position size calculation
   - Exposure monitoring
   - Stop-loss management
   - Maximum drawdown protection
3. Required methods:
   - validate_trade()
   - calculate_position_size()
   - update_risk_metrics()
   - check_risk_limits()
4. Risk parameters:
{
    "max_position_size": float,
    "max_daily_trades": int,
    "stop_loss_percentage": float,
    "max_drawdown": float
}
```

### 4. Trading Execution Service
**Prompt Template for AI Assistant:**
```
Create a Python class for trade execution with these requirements:

1. Class name: TradeExecutor
2. Features needed:
   - Exchange API integration
   - Order management
   - Position tracking
   - Trade logging
3. Required methods:
   - execute_trade()
   - manage_open_positions()
   - update_trade_status()
   - log_trade_activity()
4. Trade signal format:
{
    "action": "BUY/SELL",
    "symbol": str,
    "size": float,
    "price": float,
    "stop_loss": float,
    "take_profit": float
}
```

### 5. Real-time Dashboard
**Prompt Template for AI Assistant:**
```
Create a React dashboard with these requirements:

1. Component name: TradingDashboard
2. Features needed:
   - Real-time price charts
   - Current position display
   - Strategy performance metrics
   - Risk metrics visualization
3. Required components:
   - MarketChart
   - PositionTable
   - AlertSystem
   - PerformanceMetrics
4. Data update frequency: Every second
5. Use these libraries:
   - recharts for charts
   - shadcn/ui for components
   - WebSocket for real-time updates
```

## Integration Examples

### 1. System Initialization
```python
# Example of how components should work together
async def initialize_system():
    # Configuration
    config = {
        "redis_url": "redis://localhost:6379",
        "exchanges": ["binance", "deribit"],
        "trading_pairs": ["BTC-USD", "ETH-USD"],
        "risk_limits": {
            "max_position_size": 1000,
            "max_daily_trades": 10
        }
    }
    
    # Initialize components
    data_service = DataIngestionService(config)
    strategy_generator = StrategyGenerator(config)
    risk_manager = RiskManager(config)
    trade_executor = TradeExecutor(config)
    
    # Start services
    await asyncio.gather(
        data_service.start(),
        strategy_generator.start(),
        trade_executor.start()
    )
```

### 2. Data Flow Integration
```python
# Example of data flow between components
async def process_trading_cycle():
    while True:
        try:
            # 1. Get latest market data
            market_data = await data_service.get_latest_data()
            
            # 2. Generate/update strategy
            strategy = await strategy_generator.generate_strategy(market_data)
            
            # 3. Execute strategy with risk checks
            signal = await strategy.generate_signal(market_data)
            if await risk_manager.validate_trade(signal):
                await trade_executor.execute_trade(signal)
                
            await asyncio.sleep(15)  # Wait for next cycle
            
        except Exception as e:
            logging.error(f"Error in trading cycle: {e}")
            await asyncio.sleep(1)
```

## Implementation Steps

1. Base Infrastructure Setup
```
Prompt for AI Assistant:
Create a docker-compose.yml file with:
- Redis container
- PostgreSQL container
- Python FastAPI service
- React frontend service
Include configuration for:
- Volume mounts
- Environment variables
- Network setup
- Health checks
```

2. Data Pipeline Implementation
```
Prompt for AI Assistant:
Create an async Python script that:
1. Connects to exchange WebSocket feeds
2. Processes real-time market data
3. Stores data in Redis and PostgreSQL
4. Implements error handling and reconnection
Use the DataIngestionService class structure provided above.
```

3. Strategy Generation System
```
Prompt for AI Assistant:
Create an async Python script that:
1. Integrates with OpenAI Assistant API
2. Implements the strategy generation flow
3. Handles code execution safety
4. Manages strategy transitions
Use the StrategyGenerator class structure provided above.
```

## Testing Requirements

1. Unit Tests Template
```
Prompt for AI Assistant:
Create unit tests for the [Component] class that verify:
1. Data processing accuracy
2. Error handling
3. Edge cases
4. Performance requirements
Use pytest with async support.
```

2. Integration Tests Template
```
Prompt for AI Assistant:
Create integration tests that verify:
1. Component communication
2. Data flow correctness
3. System recovery
4. Performance under load
Include mock exchange data and responses.
```

## Monitoring Requirements

1. Metrics Collection
```
Prompt for AI Assistant:
Create a monitoring system that tracks:
1. Data freshness
2. Strategy performance
3. System latency
4. Error rates
Use Prometheus and Grafana.
```