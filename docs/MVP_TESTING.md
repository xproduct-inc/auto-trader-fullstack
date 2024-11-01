# AI Trading System MVP Testing Guide

## MVP Focus Areas
For initial testing, we'll focus on the most critical indicators for crypto options trading:

1. Primary Indicators:
   - IV Rank/Percentile
   - Gamma Exposure
   - Put/Call Ratio
   - Orderblock Analysis

2. Chart Patterns:
   - Wyckoff Accumulation/Distribution
   - Liquidation Levels

## Setup Instructions

1. Configure Indicators:
```bash
# Copy default config
cp config/indicators.yml config/indicators.local.yml

# Edit to enable only MVP indicators
nano config/indicators.local.yml
```

2. Set Up Test Environment:
```bash
# Start infrastructure
make infra-up

# Run migrations
make migrate

# Start API with MVP config
CONFIG_PATH=config/indicators.local.yml make dev
```

## Testing Scenarios

1. IV Analysis Test:
```bash
# Check current IV metrics
curl http://localhost:9000/api/v1/market-data/options/metrics/BTC-USDT

# Expected output:
{
    "iv_rank": 45.5,
    "iv_percentile": 60.2,
    "current_iv": 85.5
}
```

2. Pattern Recognition Test:
```bash
# Check for Wyckoff patterns
curl http://localhost:9000/api/v1/market-data/patterns/BTC-USDT

# Expected output:
{
    "pattern_type": "wyckoff_accumulation",
    "phase": "phase_b",
    "confidence": 0.85
}
```

3. Strategy Generation Test:
```bash
# Generate strategy based on current market conditions
curl -X POST http://localhost:9000/api/v1/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "timeframe": "1h"
  }'
```

## Validation Criteria

1. Performance Metrics:
   - Response time < 15 seconds
   - Pattern recognition accuracy > 80%
   - Strategy generation success rate > 90%

2. Risk Management:
   - Position sizing within limits
   - Stop-loss placement validation
   - Maximum drawdown checks

3. Real-time Updates:
   - Market data latency < 5 seconds
   - Pattern updates every 15 seconds
   - Strategy adjustments within 1 minute

## Common Issues & Solutions

1. High Latency:
   - Check network connectivity
   - Verify Redis cache is working
   - Monitor system resources

2. Pattern Recognition Issues:
   - Validate data quality
   - Check timeframe alignment
   - Verify volume data availability

3. Strategy Generation Delays:
   - Monitor OpenAI API response times
   - Check data preprocessing pipeline
   - Verify cache hit rates 