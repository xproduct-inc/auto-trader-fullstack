from typing import Dict, List
from tradingview_ta import TA_Handler, Interval
import plotly.graph_objects as go
from dataclasses import dataclass

@dataclass
class ChartAnalysis:
    patterns: List[Dict]
    support_resistance: List[float]
    trend_lines: List[Dict]
    chart_url: str  # TradingView chart URL

class ChartAnalyzer:
    def __init__(self):
        self.tv = TA_Handler(
            symbol="BTCUSDT",
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_4_HOURS
        )

    async def analyze_chart(self, symbol: str, timeframe: str) -> ChartAnalysis:
        """Analyze chart using TradingView"""
        self.tv.symbol = symbol
        self.tv.interval = timeframe
        
        analysis = self.tv.get_analysis()
        
        # Create interactive chart
        chart = self._create_interactive_chart(analysis)
        
        # Save chart to HTML
        chart_path = f"charts/{symbol}_{timeframe}.html"
        chart.write_html(chart_path)
        
        return ChartAnalysis(
            patterns=self._extract_patterns(analysis),
            support_resistance=self._find_support_resistance(analysis),
            trend_lines=self._find_trend_lines(analysis),
            chart_url=chart_path
        )

    def _create_interactive_chart(self, analysis) -> go.Figure:
        """Create interactive chart with Plotly"""
        fig = go.Figure(data=[go.Candlestick(
            x=analysis.time,
            open=analysis.open,
            high=analysis.high,
            low=analysis.low,
            close=analysis.close
        )])
        
        # Add patterns
        self._add_patterns_to_chart(fig, analysis)
        
        # Add support/resistance
        self._add_support_resistance(fig, analysis)
        
        # Add trend lines
        self._add_trend_lines(fig, analysis)
        
        return fig 