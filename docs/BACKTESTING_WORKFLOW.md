# Backtesting Setup and Execution Guide

## 1. Exchange API Setup

### Binance Setup
1. Create Binance Account:
   - Go to [Binance Registration](https://www.binance.com/en/register)
   - Complete KYC verification

2. Create API Keys:
   - Login to Binance
   - Go to Profile → API Management
   - Click "Create API"
   - Set restrictions:
     - Enable "Read Data" permissions
     - Enable IP whitelist (add your local IP)
     - Disable trading permissions for testing
   - Save API Key and Secret Key securely

3. Configure .env:
```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret_key
BINANCE_TESTNET=false
```

### Deribit Setup (Optional for Options Data)
1. Create Deribit Account:
   - Go to [Deribit Registration](https://www.deribit.com/register)
   - Complete verification

2. Create API Keys:
   - Login to Deribit
   - Go to Account → API
   - Create new key with "Read" permissions
   - Save credentials

3. Add to .env:
```env
DERIBIT_API_KEY=your_api_key
DERIBIT_API_SECRET=your_secret_key
```

## 2. Local Environment Setup

1. Install Dependencies:
```bash
# Install poetry if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
make setup
```

2. Configure Data Collection:
```bash
# Copy and edit backtest configuration
cp config/backtest_data.yml config/backtest_data.local.yml

# Edit parameters in backtest_data.local.yml:
timeframe: "Last 6 months"
instruments:
  - "BTC-USDT"
  - "ETH-USDT"
data_types:
  - "OHLCV"
  - "Options chain"
  - "IV history"
```

## 3. Data Collection

1. Collect Historical Data:
```bash
# Create data directories
mkdir -p data/historical

# Run data collection
make setup-backtest-data

# Validate collected data
make validate-backtest-data
```

2. Verify Data Quality:
```bash
# Check data completeness
python -m src.backtesting.data_validator \
  --data data/historical \
  --config config/backtest_data.local.yml
```

## 4. Running Backtests

1. Test Individual Components:
```bash
# Test market observer
make test-market-observer

# Test strategy generator
make test-strategy-generator

# Test risk manager
make test-risk-manager
```

2. Run Full System Backtest:
```bash
# Run all agent tests
make run-all-agent-tests
```

## 5. Analyzing Results

Results are saved in `results/backtests/` with the following structure:
```
results/backtests/
├── market_observer_YYYYMMDD_HHMMSS.json
├── strategy_generator_YYYYMMDD_HHMMSS.json
└── risk_manager_YYYYMMDD_HHMMSS.json
```

Each result file contains:
- Performance metrics
- Pattern recognition accuracy
- Strategy adaptation scores
- Risk management effectiveness

## 6. Common Issues & Solutions

1. Rate Limits:
   - Binance: 1200 requests/minute for data endpoints
   - Solution: Use data caching and batch requests

2. Data Gaps:
   - Issue: Missing candles in historical data
   - Solution: Run data validation and fill gaps with interpolation

3. API Connection:
   - Issue: Connection timeouts
   - Solution: Check IP whitelist and API permissions

## 7. Performance Optimization

1. Data Storage:
   - Use parquet files for efficient storage
   - Implement Redis caching for frequent queries

2. Computation:
   - Use pandas operations instead of loops
   - Implement parallel processing for pattern recognition

## 8. Next Steps

1. Fine-tuning:
   - Adjust pattern recognition thresholds
   - Optimize strategy parameters
   - Refine risk management rules

2. Production Preparation:
   - Compare backtest vs paper trading results
   - Monitor system resource usage
   - Set up alerting for data issues

## 9. Monitoring Backtests

1. Real-time Monitoring:
```bash
# Watch backtest progress
tail -f logs/backtest.log

# Monitor system resources
htop
```

2. Performance Metrics:
```bash
# Generate performance report
python -m src.backtesting.generate_report

# View results summary
python -m src.backtesting.show_summary
```

## 10. Troubleshooting

1. Data Collection Issues:
```bash
# Check API status
curl https://api.binance.com/api/v3/ping

# Verify data integrity
make validate-backtest-data
```

2. Processing Issues:
```bash
# Check system logs
tail -f logs/error.log

# Monitor memory usage
watch -n 1 free -m
```

## 11. Configuration Reference

Key configuration files:
- `config/backtest_data.yml`: Data collection settings
- `config/indicators.yml`: Technical indicator parameters
- `.env`: API keys and environment settings
- `pyproject.toml`: Project dependencies

## 12. Support Resources

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [Deribit API Documentation](https://docs.deribit.com/)
- [Project Issues](https://github.com/yourusername/project/issues)

## 13. Interpreting Backtest Results

### Success Metrics

1. Pattern Recognition Success:
```json
{
    "pattern_recognition_accuracy": 0.85,  // Should be > 0.80
    "false_positives": 0.15,              // Should be < 0.20
    "average_processing_time": 0.5,        // Should be < 1.0 second
    "pattern_distribution": {
        "wyckoff_accumulation": 0.25,
        "orderblocks": 0.35,
        "liquidity_levels": 0.40
    }
}
```

2. Strategy Performance:
```json
{
    "win_rate": 0.65,                     // Should be > 0.60
    "profit_factor": 2.1,                 // Should be > 1.5
    "max_drawdown": 0.12,                 // Should be < 0.15
    "sharpe_ratio": 1.8,                  // Should be > 1.5
    "recovery_factor": 2.5,               // Should be > 2.0
    "average_trade_duration": "4h",
    "best_performing_patterns": [
        "wyckoff_accumulation",
        "liquidity_sweep"
    ]
}
```

3. Risk Management Effectiveness:
```json
{
    "position_size_accuracy": 0.98,        // Should be > 0.95
    "risk_limit_breaches": 0,             // Must be 0
    "max_correlation": 0.4,               // Should be < 0.5
    "portfolio_heat": 0.25,               // Should be < 0.3
    "largest_drawdown": 0.12,             // Should be < 0.15
    "risk_reward_ratio": 2.5              // Should be > 2.0
}
```

### Refinement Process

1. Pattern Recognition Refinement:
```yaml
if pattern_recognition_accuracy < 0.80:
    actions:
        - Adjust detection thresholds
        - Increase minimum volume requirements
        - Add more confirmation signals
        - Extend pattern formation window

if false_positives > 0.20:
    actions:
        - Increase confidence thresholds
        - Add more validation rules
        - Implement multi-timeframe confirmation
```

2. Strategy Refinement:
```yaml
if win_rate < 0.60:
    actions:
        - Adjust entry criteria
        - Add more confluence factors
        - Increase minimum setup quality threshold
        - Review stop loss placement

if profit_factor < 1.5:
    actions:
        - Adjust take profit levels
        - Implement trailing stops
        - Review position sizing
        - Add partial profit taking
```

3. Risk Management Refinement:
```yaml
if max_drawdown > 0.15:
    actions:
        - Reduce position sizes
        - Tighten stop losses
        - Add correlation limits
        - Implement portfolio heat rules

if position_size_accuracy < 0.95:
    actions:
        - Adjust risk per trade
        - Review volatility adjustments
        - Implement dynamic sizing
```

### Example Refinement Workflow

1. Initial Assessment:
```bash
# Generate detailed performance report
python -m src.backtesting.analyze_results \
    --results-dir results/backtests \
    --output-format detailed

# Identify weak points
python -m src.backtesting.identify_weaknesses \
    --threshold 0.8
```

2. Parameter Optimization:
```bash
# Run optimization for specific parameters
python -m src.backtesting.optimize_params \
    --target win_rate \
    --min-threshold 0.6 \
    --max-iterations 100
```

3. Validation:
```bash
# Run validation on different market conditions
python -m src.backtesting.validate_strategy \
    --market-conditions all \
    --time-periods "2023-01-01,2024-01-01"
```

### Common Refinement Scenarios

1. Low Win Rate but High Profit Factor:
- Indicates good risk management but poor entry timing
- Focus on entry criteria refinement
- Consider adding more confirmation signals

2. High Win Rate but Low Profit Factor:
- Indicates good entry but poor exit management
- Review take profit strategies
- Implement trailing stops
- Consider scaling out positions

3. Good Performance but High Drawdown:
- Indicates position sizing issues
- Review correlation between trades
- Implement portfolio heat rules
- Add market regime filters

4. Pattern Recognition Issues:
- Review and adjust detection thresholds
- Add volume confirmation requirements
- Implement multi-timeframe validation
- Consider market context filters

### Continuous Improvement Process

1. Weekly Review:
```bash
# Generate weekly performance report
make generate-weekly-report

# Compare against benchmarks
make compare-benchmarks

# Update parameters if needed
make update-parameters
```

2. Monthly Optimization:
```bash
# Run full optimization
make optimize-full

# Validate changes
make validate-changes

# Apply updates if improved
make apply-updates
```

3. Quarterly Deep Review:
```bash
# Generate quarterly analysis
make quarterly-analysis

# Review market adaptation
make review-adaptation

# Update strategy rules
make update-rules
```

### Production Readiness Criteria

Before deploying to live trading, ensure:

1. Performance Metrics:
- Consistent profit factor > 1.5 across all test periods
- Maximum drawdown < 15% in all market conditions
- Win rate > 60% in most recent quarter
- Risk management effectiveness > 95%

2. Technical Metrics:
- Processing time < 1 second for all operations
- No memory leaks in long-running tests
- Stable database performance
- Reliable API connections

3. Risk Controls:
- All position sizing accurate to 95%+
- No risk limit breaches
- Portfolio heat always under 30%
- Correlation management effective

4. Documentation:
- All parameters documented
- Refinement process recorded
- Performance metrics tracked
- Incident response plan ready