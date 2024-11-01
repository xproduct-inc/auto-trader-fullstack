# AI Trading System

An AI-powered cryptocurrency trading system built with FastAPI, TimescaleDB, Redis, and OpenAI's Assistant API.

## Features

- Real-time market data ingestion from multiple exchanges
- AI-powered trading strategy generation
- Risk management and position sizing
- Automated trade execution
- Performance monitoring and analytics
- Distributed tracing and error tracking

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Databases**: 
  - TimescaleDB (time-series data)
  - Redis Stack (real-time data & caching)
  - ClickHouse (analytics)
- **AI/ML**: 
  - OpenAI Assistant API
  - LangGraph
  - LangChain
- **Monitoring**:
  - Prometheus
  - Grafana
  - OpenTelemetry
  - Sentry

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Poetry (Python package manager)
- Binance API keys (for live trading)
- Deribit API keys (optional)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-trading-system.git
cd ai-trading-system
```

2. Set up the environment:
```bash
make setup
```

3. Configure your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

4. Start the services:
```bash
make docker-up
```

5. Run database migrations:
```bash
make migrate
```

## Exchange Integration

### Binance Setup

1. Create a Binance account and generate API keys:
   - Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
   - Create new API keys
   - Enable trading permissions
   - Add IP restrictions (recommended)

2. Add Binance credentials to `.env`:
```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

### Deribit Setup (Optional)

1. Create a Deribit account and generate API keys:
   - Go to [Deribit API Management](https://www.deribit.com/main#/account/api)
   - Create new API keys
   - Set appropriate permissions
   - Add IP restrictions (recommended)

2. Add Deribit credentials to `.env`:
```env
DERIBIT_API_KEY=your_api_key
DERIBIT_API_SECRET=your_api_secret
```

## Running the Application

1. Start all services:
```bash
make docker-up
```

2. Start the development server:
```bash
make start-dev
```

3. Access the services:
- API Documentation: http://localhost:8000/docs
- Grafana Dashboard: http://localhost:3000
- Prometheus: http://localhost:9090

## Testing

### Running Tests

1. Run all tests:
```bash
make test
```

2. Run specific test categories:
```bash
# Run market data tests
pytest tests/test_api/test_market_data.py

# Run strategy tests
pytest tests/test_api/test_strategy.py
```

### Manual Testing

1. Test market data ingestion:
```bash
curl http://localhost:9000/api/v1/market-data/latest/binance/BTC-USD
```

2. Test strategy generation:
```bash
curl -X POST http://localhost:9000/api/v1/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{"market_data": {"symbol": "BTC-USD", "timeframe": "1h"}}'
```

3. Check system health:
```bash
curl http://localhost:9000/health
```

4. View metrics:
```bash
curl http://localhost:9000/metrics
```

## Monitoring and Analytics

### Grafana Dashboards

1. Access Grafana at http://localhost:3000
2. Default credentials:
   - Username: admin
   - Password: (from GRAFANA_ADMIN_PASSWORD in .env)

### Available Dashboards:
- Trading Performance
- Market Data Metrics
- System Health
- Error Tracking

### Logs and Metrics

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Metrics: http://localhost:8000/metrics

## Development

### Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Create database migrations:
```bash
make create-migration message="Add new feature tables"
```

3. Run linters:
```bash
make lint
```

### Code Structure

```
src/
├── api/            # API routes
├── core/           # Core configuration
├── db/             # Database models
├── services/       # Business logic
├── schemas/        # Pydantic models
├── agents/         # Trading agents
└── utils/          # Utilities
```

## Troubleshooting

### Common Issues

1. Database connection issues:
```bash
# Check database status
make db-shell

# Verify migrations
make migrate
```

2. Redis connection issues:
```bash
# Check Redis status
make redis-shell
```

3. Market data issues:
```bash
# Check exchange connectivity
curl http://localhost:8000/health
```

## Production Deployment

1. Update production settings:
```bash
# Edit .env for production
ENVIRONMENT=production
```

2. Build production images:
```bash
make docker-build
```

3. Start production services:
```bash
make start-prod
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE) 

## Step-by-Step Testing Walkthrough

### 1. Test Environment Setup

```bash
# Create test directory
mkdir ai-trading-test
cd ai-trading-test

# Initialize poetry and create virtual environment
poetry init --name=ai-trading-test-run --python=^3.11
poetry shell

# Install dependencies
poetry install
```

### 2. Test Configuration

Create a test environment file:
```bash
cat > .env << EOL
# API Settings
API_V1_STR=/api/v1
PROJECT_NAME="AI Trading System"

# Database Settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=testpassword123
POSTGRES_DB=trading_db_test
POSTGRES_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Exchange Settings
ENABLED_EXCHANGES=["binance"]
TRADING_PAIRS=["BTC-USDT"]

# OpenAI Settings
OPENAI_API_KEY=your_test_openai_key

# Binance Settings (using testnet)
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_secret
BINANCE_TESTNET=true

# Monitoring Settings
GRAFANA_ADMIN_PASSWORD=admin123
SENTRY_DSN=your_sentry_dsn
EOL
```

### 3. Test Database Setup

Create a test-specific docker-compose file:
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: timescale/timescaledb:latest-pg14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=testpassword123
      - POSTGRES_DB=trading_db_test
    ports:
      - "5432:5432"

  test-redis:
    image: redis/redis-stack:latest
    ports:
      - "6379:6379"
```

### 4. Running Tests

```bash
# Start test dependencies
docker-compose -f docker-compose.test.yml up -d

# Run all tests with verbose output
pytest tests/ -v --log-cli-level=INFO

# Run specific test categories
pytest tests/test_api/test_market_data.py -v
pytest tests/test_api/test_strategy.py -v
pytest tests/test_api/test_trading.py -v
```

### 5. Testing Individual Components

#### Test Market Data Ingestion
```bash
# Test market data endpoint
curl http://localhost:8000/api/v1/market-data/latest/binance/BTC-USDT

# Test historical data
curl "http://localhost:8000/api/v1/market-data/historical/binance/BTC-USDT?start_time=2024-01-01T00:00:00Z"
```

#### Test Strategy Generation
```bash
# Generate trading strategy
curl -X POST http://localhost:8000/api/v1/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {
      "symbol": "BTC-USDT",
      "timeframe": "1h",
      "exchange": "binance"
    }
  }'
```

#### Test Risk Management
```bash
# Validate trade
curl -X POST http://localhost:8000/api/v1/risk/validate-trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "action": "BUY",
    "entry_price": 50000,
    "stop_loss": 49000,
    "position_size": 0.1
  }'
```

#### Test Trade Execution
```bash
# Execute trade
curl -X POST http://localhost:8000/api/v1/trading/execute \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "action": "BUY",
    "quantity": 0.001,
    "price": 50000,
    "stop_loss": 49000,
    "take_profit": 52000
  }'
```

### 6. Monitoring Tests

```bash
# Check system health
curl http://localhost:8000/health

# View metrics
curl http://localhost:8000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Access Grafana dashboards
open http://localhost:3000
```

### 7. Common Issues and Solutions

1. Database Connection Issues:
```bash
# Check database status
docker-compose -f docker-compose.test.yml ps test-db
docker-compose -f docker-compose.test.yml logs test-db

# Verify database connection
psql -h localhost -U postgres -d trading_db_test
```

2. Redis Connection Issues:
```bash
# Check Redis status
docker-compose -f docker-compose.test.yml ps test-redis
docker-compose -f docker-compose.test.yml logs test-redis

# Test Redis connection
redis-cli ping
```

3. OpenAI API Issues:
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test OpenAI connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 8. Cleanup Test Environment

```bash
# Stop test services
docker-compose -f docker-compose.test.yml down

# Remove test database
docker volume rm ai-trading-test_postgres_data

# Deactivate virtual environment
deactivate
```

Note: Replace placeholder API keys and credentials with actual test credentials before running the tests. 

## Local Testing Setup

### Test Environment Configuration

1. Create a test environment file:
```bash
cp .env.test .env.local
```

2. Update the following critical values in `.env.local`:
```bash
# Get from Binance Testnet
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_secret

# Get from OpenAI
OPENAI_API_KEY=your_openai_api_key

# Get from Sentry (optional for testing)
SENTRY_DSN=your_sentry_dsn
```

3. Start the test environment:
```bash
# Start required services
docker-compose -f docker-compose.test.yml up -d

# Run database migrations
make migrate

# Start the application in test mode
ENV_FILE=.env.local make start-dev
```

### Getting Test API Keys

1. **Binance Testnet API Keys**:
   - Go to [Binance Testnet](https://testnet.binance.vision/)
   - Create an account and generate API keys
   - Fund your testnet account with fake BTC/USDT

2. **OpenAI API Key**:
   - Go to [OpenAI API](https://platform.openai.com/)
   - Create an account and generate an API key
   - Note: Keep rate limits in mind for testing

### Verifying Test Setup

1. Check service health:
```bash
curl http://localhost:8000/health
```

2. Test market data connection:
```bash
curl http://localhost:8000/api/v1/market-data/latest/binance/BTC-USDT
```

3. Verify database connection:
```bash
make db-shell
```

4. Check Redis connection:
```bash
make redis-shell
```

### Running Tests with Mock Data

For testing without real API connections, enable mock responses:
```bash
# In .env.local
ENABLE_MOCK_RESPONSES=true
```

This will use predefined test data instead of real API calls.