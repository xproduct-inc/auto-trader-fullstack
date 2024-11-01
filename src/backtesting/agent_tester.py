from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
from loguru import logger
from pathlib import Path

from src.services.technical_analysis import TechnicalAnalysis
from src.services.strategy import StrategyGenerator
from src.services.risk_manager import RiskManager
from src.backtesting.pattern_analyzer import PatternAnalyzer

class AgentTester:
    def __init__(self, config_path: str = "config/backtest_data.yml"):
        self.ta = TechnicalAnalysis()
        self.strategy_generator = StrategyGenerator()
        self.risk_manager = RiskManager()
        self.results_dir = Path("results/backtests")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def test_market_observer(self, data: pd.DataFrame) -> Dict:
        """Test pattern recognition and indicator calculation accuracy"""
        try:
            logger.info("Starting Market Observer testing...")
            results = {
                "pattern_recognition": [],
                "indicator_calculation": [],
                "processing_times": []
            }

            for i in range(len(data) - 100):  # Use 100-candle windows
                window = data.iloc[i:i+100]
                start_time = datetime.now()

                # Test pattern recognition
                patterns = await self.ta.analyze_chart_patterns(window)
                options_analysis = await self.ta.analyze_options_market(window.to_dict())
                
                # Record processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                results["processing_times"].append(processing_time)

                # Validate pattern completion
                if patterns:
                    for pattern in patterns:
                        completion = self._validate_pattern_completion(
                            pattern, 
                            data.iloc[i+100:i+200]  # Look ahead for validation
                        )
                        results["pattern_recognition"].append(completion)

                # Validate indicator calculations
                indicator_accuracy = self._validate_indicator_calculations(
                    options_analysis,
                    window
                )
                results["indicator_calculation"].append(indicator_accuracy)

            return self._summarize_observer_results(results)

        except Exception as e:
            logger.error(f"Error testing Market Observer: {e}")
            raise

    async def test_strategy_generator(self, data: pd.DataFrame) -> Dict:
        """Test strategy generation and adaptation"""
        try:
            logger.info("Starting Strategy Generator testing...")
            results = {
                "strategies": [],
                "adaptations": [],
                "performance": []
            }

            # Test different market regimes
            regimes = self._identify_market_regimes(data)
            
            for regime, period in regimes.items():
                regime_data = data.loc[period["start"]:period["end"]]
                
                # Generate and test strategies for this regime
                strategies = await self._test_regime_strategies(regime_data, regime)
                results["strategies"].extend(strategies)

                # Test adaptation to regime changes
                if len(results["strategies"]) > 1:
                    adaptation = self._test_strategy_adaptation(
                        results["strategies"][-2:],
                        regime
                    )
                    results["adaptations"].append(adaptation)

            return self._summarize_strategy_results(results)

        except Exception as e:
            logger.error(f"Error testing Strategy Generator: {e}")
            raise

    async def test_risk_manager(self, data: pd.DataFrame) -> Dict:
        """Test risk management rules and position sizing"""
        try:
            logger.info("Starting Risk Manager testing...")
            results = {
                "position_sizing": [],
                "risk_limits": [],
                "drawdown_prevention": []
            }

            # Test position sizing
            for i in range(0, len(data), 100):  # Test every 100 candles
                window = data.iloc[i:i+100]
                
                # Generate test trades
                test_trades = self._generate_test_trades(window)
                
                for trade in test_trades:
                    # Test position sizing
                    position_size = await self.risk_manager.calculate_position_size(
                        trade,
                        account_balance=100000  # Test with fixed balance
                    )
                    
                    # Validate position size
                    position_validation = self._validate_position_size(
                        position_size,
                        trade,
                        window
                    )
                    results["position_sizing"].append(position_validation)

                    # Test risk limits
                    risk_validation = await self._test_risk_limits(trade, window)
                    results["risk_limits"].append(risk_validation)

                    # Test drawdown prevention
                    drawdown_test = self._test_drawdown_prevention(
                        trade,
                        window,
                        previous_trades=results["position_sizing"]
                    )
                    results["drawdown_prevention"].append(drawdown_test)

            return self._summarize_risk_results(results)

        except Exception as e:
            logger.error(f"Error testing Risk Manager: {e}")
            raise

    async def test_pattern_analysis(self, data: pd.DataFrame) -> Dict:
        """Test pattern analysis accuracy"""
        try:
            logger.info("Starting Pattern Analysis testing...")
            pattern_analyzer = PatternAnalyzer()
            
            results = {
                "patterns": [],
                "accuracy": [],
                "profit_potential": []
            }
            
            # Analyze patterns
            patterns = pattern_analyzer.analyze_patterns(data)
            
            # Test each pattern type
            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    # Get future data for validation
                    future_data = self._get_future_data(data, pattern)
                    
                    # Validate pattern outcome
                    outcome = self._validate_pattern_outcome(pattern, future_data)
                    results["patterns"].append({
                        "type": pattern_type,
                        "confidence": pattern.get("ml_confidence", 0),
                        "outcome": outcome
                    })
                    
                    # Calculate accuracy and profit metrics
                    if outcome["success"]:
                        results["accuracy"].append(1)
                        results["profit_potential"].append(outcome["profit"])
                    else:
                        results["accuracy"].append(0)
                        results["profit_potential"].append(0)
            
            return {
                "pattern_accuracy": np.mean(results["accuracy"]),
                "average_profit": np.mean(results["profit_potential"]),
                "pattern_distribution": self._calculate_pattern_distribution(results["patterns"]),
                "ml_correlation": self._calculate_ml_correlation(results["patterns"])
            }
            
        except Exception as e:
            logger.error(f"Error testing pattern analysis: {e}")
            raise

    def _validate_pattern_completion(self, pattern: Dict, future_data: pd.DataFrame) -> Dict:
        """Validate if a detected pattern played out as expected"""
        target_hit = False
        stop_hit = False
        profit = 0.0

        if pattern["pattern_type"] in ["double_top", "head_and_shoulders"]:
            target_hit = future_data["low"].min() <= pattern["price_target"]
            stop_hit = future_data["high"].max() >= pattern["stop_loss"]
        else:
            target_hit = future_data["high"].max() >= pattern["price_target"]
            stop_hit = future_data["low"].min() <= pattern["stop_loss"]

        if target_hit and not stop_hit:
            profit = abs(pattern["price_target"] - pattern["formation_points"][-1]["price"])

        return {
            "pattern_type": pattern["pattern_type"],
            "target_hit": target_hit,
            "stop_hit": stop_hit,
            "profit": profit,
            "confidence": pattern["confidence"]
        }

    def _validate_indicator_calculations(self, analysis: Dict, data: pd.DataFrame) -> Dict:
        """Validate technical indicator calculations"""
        # Implementation for indicator validation
        pass

    def _summarize_observer_results(self, results: Dict) -> Dict:
        """Summarize Market Observer test results"""
        pattern_accuracy = np.mean([r["target_hit"] for r in results["pattern_recognition"]])
        avg_processing_time = np.mean(results["processing_times"])
        
        return {
            "pattern_recognition_accuracy": pattern_accuracy,
            "average_processing_time": avg_processing_time,
            "indicator_calculation_accuracy": np.mean(results["indicator_calculation"]),
            "real_time_capable": avg_processing_time < 1.0  # Sub-second processing
        }

    def _summarize_strategy_results(self, results: Dict) -> Dict:
        """Summarize Strategy Generator test results"""
        return {
            "strategies_generated": len(results["strategies"]),
            "regime_adaptation_score": np.mean(results["adaptations"]),
            "average_profit_factor": np.mean([s["profit_factor"] for s in results["strategies"]]),
            "win_rate": np.mean([s["win_rate"] for s in results["strategies"]])
        }

    def _summarize_risk_results(self, results: Dict) -> Dict:
        """Summarize Risk Manager test results"""
        return {
            "position_size_accuracy": np.mean(results["position_sizing"]),
            "risk_limit_adherence": np.mean(results["risk_limits"]),
            "drawdown_prevention_effectiveness": np.mean(results["drawdown_prevention"])
        }

    async def save_results(self, results: Dict, test_name: str):
        """Save test results to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"{test_name}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to {results_file}") 