import asyncio
import pandas as pd
from pathlib import Path
import yaml
from loguru import logger

from src.backtesting.agent_tester import AgentTester
from src.backtesting.data_collector import HistoricalDataCollector

async def run_agent_tests():
    try:
        # Load configuration
        with open("config/backtest_data.yml") as f:
            config = yaml.safe_load(f)

        # Load historical data
        data_path = Path("data/historical")
        price_data = pd.read_parquet(data_path / "price_data.parquet")
        options_data = pd.read_parquet(data_path / "options_data.parquet")

        # Initialize tester
        tester = AgentTester()

        # Test Market Observer
        logger.info("Testing Market Observer...")
        observer_results = await tester.test_market_observer(price_data)
        await tester.save_results(observer_results, "market_observer")

        # Test Strategy Generator
        logger.info("Testing Strategy Generator...")
        strategy_results = await tester.test_strategy_generator(price_data)
        await tester.save_results(strategy_results, "strategy_generator")

        # Test Risk Manager
        logger.info("Testing Risk Manager...")
        risk_results = await tester.test_risk_manager(price_data)
        await tester.save_results(risk_results, "risk_manager")

        # Print summary
        print("\nTest Results Summary:")
        print("=====================")
        print("\nMarket Observer:")
        print(f"Pattern Recognition Accuracy: {observer_results['pattern_recognition_accuracy']:.2%}")
        print(f"Average Processing Time: {observer_results['average_processing_time']:.3f}s")

        print("\nStrategy Generator:")
        print(f"Win Rate: {strategy_results['win_rate']:.2%}")
        print(f"Profit Factor: {strategy_results['average_profit_factor']:.2f}")

        print("\nRisk Manager:")
        print(f"Position Size Accuracy: {risk_results['position_size_accuracy']:.2%}")
        print(f"Risk Limit Adherence: {risk_results['risk_limit_adherence']:.2%}")

    except Exception as e:
        logger.error(f"Error running agent tests: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_agent_tests()) 