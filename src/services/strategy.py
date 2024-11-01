from typing import Dict, Optional, List
import json
from datetime import datetime
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from src.core.config import get_settings
from src.utils.redis_client import RedisClient
from src.db.session import get_db
from src.db.models.trading import Trade, PerformanceMetrics
from src.services.technical_analysis import TechnicalAnalysis

settings = get_settings()

class StrategyGenerator:
    def __init__(self):
        self.client = None
        self.redis_client = RedisClient()
        self.assistant_id = None
        self.thread_id = None
        self.mock_mode = settings.ENABLE_MOCK_RESPONSES

    async def initialize(self):
        """Initialize OpenAI assistant and thread"""
        try:
            await self.redis_client.connect()
            
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('your_'):
                logger.warning("No valid OpenAI API key provided - running in mock mode")
                self.mock_mode = True
                return

            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Create or load assistant with enhanced options trading expertise
            assistant = await self.client.beta.assistants.create(
                name="Options Trading Strategy Generator",
                instructions="""
                You are an expert crypto options trading strategist specializing in advanced volatility trading and options strategies.

                Key Responsibilities:
                1. Analyze Market Context:
                   - Evaluate IV Rank and IV Percentile for volatility regime identification
                   - Assess volatility term structure for contango/backwardation
                   - Analyze volatility skew for market sentiment
                   - Monitor gamma exposure levels and potential market impact
                   - Track put/call ratios for sentiment shifts
                   - Evaluate open interest distribution for key strike levels

                2. Strategy Generation:
                   - Design delta-neutral strategies when appropriate
                   - Utilize calendar spreads during volatility term structure opportunities
                   - Implement iron condors/butterflies in range-bound markets
                   - Deploy ratio spreads for directional plays with volatility edge
                   - Use covered calls and cash-secured puts for premium harvesting
                   - Consider diagonal spreads for complex volatility views

                3. Risk Management:
                   - Set position sizes based on portfolio VaR
                   - Calculate optimal stop-loss levels using options Greeks
                   - Monitor and adjust for vega risk exposure
                   - Track and manage theta decay
                   - Assess gamma risk at key price levels
                   - Consider rolling strategies near expiration

                4. Market Mechanics:
                   - Account for options expiration cycles
                   - Consider liquidity at different strikes
                   - Monitor implied volatility surface changes
                   - Track max pain points for potential pin risk
                   - Evaluate market maker positioning
                   - Consider funding rates for crypto-specific impacts

                Provide clear trade recommendations with:
                - Strategy type and rationale
                - Specific strikes and expiries
                - Entry/exit criteria
                - Greeks exposure
                - Risk parameters
                - Adjustment triggers
                - Expected scenario analysis
                """,
                model="gpt-4-turbo-preview",
                tools=[{"type": "code_interpreter"}]
            )
            self.assistant_id = assistant.id

            # Create thread for ongoing conversation
            thread = await self.client.beta.threads.create()
            self.thread_id = thread.id
            
            logger.info("Strategy generator initialized successfully")
            
        except Exception as e:
            logger.warning(f"Error initializing strategy generator: {e} - falling back to mock mode")
            self.mock_mode = True

    async def generate_strategy(self, market_data: Dict) -> Dict:
        """Generate trading strategy based on market data"""
        try:
            # Enrich market data with technical analysis
            enriched_data = await self._enrich_market_data(market_data)
            
            if self.mock_mode:
                return self._generate_mock_strategy(enriched_data)
                
            # Format market data for the assistant
            prompt = self._format_market_data(enriched_data)
            
            # Add message to thread
            message = await self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=prompt
            )

            # Run assistant
            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )

            # Wait for completion
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break
                await asyncio.sleep(1)

            # Get response
            messages = await self.client.beta.threads.messages.list(
                thread_id=self.thread_id
            )
            
            # Parse and validate strategy
            strategy = self._parse_strategy_response(messages.data[0].content[0].text.value)
            if await self.validate_strategy(strategy):
                return strategy
            
            raise ValueError("Invalid strategy generated")

        except Exception as e:
            logger.error(f"Error generating strategy: {e} - falling back to mock strategy")
            return self._generate_mock_strategy(market_data)

    def _generate_mock_strategy(self, market_data: Dict) -> Dict:
        """Generate a mock strategy for testing"""
        return {
            "action": "BUY",
            "symbol": market_data.get("symbol", "BTC-USDT"),
            "entry_price": 50000.0,
            "stop_loss": 49000.0,
            "take_profit": 52000.0,
            "position_size": 0.1,
            "timeframe": "1h",
            "confidence": 0.8,
            "strategy_type": "mock_strategy",
            "indicators": {
                "rsi": 45,
                "macd": "bullish",
                "trend": "upward"
            }
        }

    async def validate_strategy(self, strategy: Dict) -> bool:
        """Validate generated strategy"""
        required_fields = [
            "action", "symbol", "entry_price", "stop_loss", 
            "take_profit", "position_size", "timeframe"
        ]
        
        try:
            # Check required fields
            if not all(field in strategy for field in required_fields):
                return False
                
            # Validate price levels
            if strategy["action"] == "BUY":
                if not (strategy["stop_loss"] < strategy["entry_price"] < strategy["take_profit"]):
                    return False
            elif strategy["action"] == "SELL":
                if not (strategy["stop_loss"] > strategy["entry_price"] > strategy["take_profit"]):
                    return False
                    
            # Validate position size against risk limits
            if strategy["position_size"] > settings.RISK_LIMITS["max_position_size"]:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Strategy validation error: {e}")
            return False

    async def update_performance_metrics(self, strategy_id: str, trade: Trade):
        """Update strategy performance metrics"""
        async for db in get_db():
            try:
                # Calculate metrics
                trades = await db.query(Trade).filter(Trade.strategy_id == strategy_id).all()
                
                total_trades = len(trades)
                winning_trades = len([t for t in trades if t.pnl and t.pnl > 0])
                win_rate = winning_trades / total_trades if total_trades > 0 else 0
                
                total_pnl = sum(t.pnl for t in trades if t.pnl)
                
                # Calculate other metrics (Sharpe ratio, drawdown etc.)
                metrics = PerformanceMetrics(
                    strategy_id=strategy_id,
                    timestamp=datetime.utcnow(),
                    total_trades=total_trades,
                    win_rate=win_rate,
                    total_pnl=total_pnl,
                    # Add other calculated metrics
                )
                
                db.add(metrics)
                await db.commit()
                
            except Exception as e:
                logger.error(f"Error updating performance metrics: {e}")
                await db.rollback()

    def _format_market_data(self, market_data: Dict) -> str:
        """Format market data for the assistant"""
        return json.dumps({
            "request": "Generate options trading strategy",
            "market_data": market_data,
            "options_analysis": market_data.get("options_analysis", {}),
            "market_context": {
                "current_trend": market_data.get("trend", "neutral"),
                "recent_volatility": market_data.get("historical_volatility", 0),
                "major_levels": market_data.get("support_resistance", []),
                "upcoming_events": market_data.get("events", [])
            },
            "risk_parameters": {
                "max_position_size": settings.RISK_LIMITS["max_position_size"],
                "max_risk_per_trade": settings.RISK_LIMITS["stop_loss_percentage"],
                "max_vega_exposure": settings.RISK_LIMITS.get("max_vega_exposure", 0.1),
                "max_gamma_exposure": settings.RISK_LIMITS.get("max_gamma_exposure", 0.1),
                "portfolio_margin_used": market_data.get("margin_used", 0)
            },
            "required_output_format": {
                "strategy_type": "string",  # e.g., "iron_condor", "calendar_spread"
                "rationale": "string",      # Strategy selection reasoning
                "legs": [
                    {
                        "option_type": "string",  # "call" or "put"
                        "strike": "float",
                        "expiry": "string",
                        "action": "string",       # "buy" or "sell"
                        "quantity": "integer"
                    }
                ],
                "entry_rules": {},          # Entry criteria
                "exit_rules": {},           # Exit criteria
                "greeks": {                 # Expected Greeks exposure
                    "delta": "float",
                    "gamma": "float",
                    "theta": "float",
                    "vega": "float"
                },
                "risk_metrics": {           # Risk parameters
                    "max_loss": "float",
                    "profit_potential": "float",
                    "probability_of_profit": "float"
                },
                "adjustments": ["string"]   # Adjustment triggers and actions
            }
        }, indent=2)

    def _parse_strategy_response(self, response: str) -> Dict:
        """Parse and structure the assistant's response"""
        try:
            # Extract JSON strategy from response
            strategy_start = response.find('{')
            strategy_end = response.rfind('}') + 1
            strategy_json = response[strategy_start:strategy_end]
            
            return json.loads(strategy_json)
            
        except Exception as e:
            logger.error(f"Error parsing strategy response: {e}")
            raise ValueError("Invalid strategy format")

    async def stop(self):
        """Cleanup resources"""
        await self.redis_client.disconnect() 

    async def _enrich_market_data(self, market_data: Dict) -> Dict:
        """Enrich market data with technical analysis"""
        try:
            ta = TechnicalAnalysis()
            options_analysis = await ta.analyze_options_market(market_data)
            
            return {
                **market_data,
                "options_analysis": {
                    "iv_rank": options_analysis.iv_rank,
                    "iv_percentile": options_analysis.iv_percentile,
                    "historical_volatility": options_analysis.historical_volatility,
                    "term_structure": options_analysis.term_structure,
                    "skew": options_analysis.skew,
                    "gamma_exposure": options_analysis.gamma_exposure,
                    "put_call_ratio": options_analysis.put_call_ratio,
                    "open_interest": options_analysis.open_interest,
                    "max_pain": options_analysis.max_pain
                }
            }
        except Exception as e:
            logger.error(f"Error enriching market data: {e}")
            return market_data