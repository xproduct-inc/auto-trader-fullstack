from typing import Dict, List
import numpy as np
import pandas as pd
from loguru import logger
from dataclasses import dataclass

@dataclass
class OptionsAnalysis:
    iv_rank: float  # Implied Volatility Rank
    iv_percentile: float  # IV Percentile
    historical_volatility: float
    term_structure: Dict[str, float]  # Volatility term structure
    skew: Dict[str, float]  # Volatility skew
    gamma_exposure: float
    put_call_ratio: float
    open_interest: Dict[str, int]
    max_pain: float

@dataclass
class PriceAnalysis:
    # Traditional Technical Indicators
    sma: Dict[str, float]        # Multiple timeframes (20, 50, 200)
    ema: Dict[str, float]        # Multiple timeframes (9, 21, 55)
    vwap: float
    rsi: float
    macd: Dict[str, float]       # MACD line, Signal line, Histogram
    stochastic: Dict[str, float] # %K and %D lines
    bollinger: Dict[str, float]  # Upper, Middle, Lower bands
    atr: float

    # Options-Specific Context
    trend_strength: float        # How strong is the underlying trend
    support_resistance: List[float]  # Key price levels
    volatility_regime: str       # "high", "low", "normal"

@dataclass
class ChartPattern:
    pattern_type: str      # e.g., "double_top", "head_shoulders", etc.
    confidence: float      # Pattern confidence score (0-1)
    price_target: float    # Expected price target
    stop_loss: float      # Suggested stop loss
    formation_points: List[Dict[str, float]]  # Key points forming the pattern
    volume_confirms: bool  # Whether volume confirms the pattern

@dataclass
class CandlestickPattern:
    pattern_type: str      # e.g., "doji", "hammer", "engulfing"
    bullish: bool         # True for bullish patterns, False for bearish
    strength: float       # Pattern strength score (0-1)
    context: str          # "trend_reversal", "continuation", etc.

class TechnicalAnalysis:
    def __init__(self):
        self.lookback_period = 30  # Default 30 days for historical calculations

    async def analyze_options_market(self, market_data: Dict) -> OptionsAnalysis:
        """Analyze options market data with key indicators"""
        try:
            # Calculate options-specific indicators
            iv_rank = self._calculate_iv_rank(market_data)
            iv_percentile = self._calculate_iv_percentile(market_data)
            hv = self._calculate_historical_volatility(market_data)
            term_structure = self._analyze_volatility_term_structure(market_data)
            skew = self._analyze_volatility_skew(market_data)
            gex = self._calculate_gamma_exposure(market_data)
            pcr = self._calculate_put_call_ratio(market_data)
            oi = self._analyze_open_interest(market_data)
            max_pain = self._calculate_max_pain(market_data)

            return OptionsAnalysis(
                iv_rank=iv_rank,
                iv_percentile=iv_percentile,
                historical_volatility=hv,
                term_structure=term_structure,
                skew=skew,
                gamma_exposure=gex,
                put_call_ratio=pcr,
                open_interest=oi,
                max_pain=max_pain
            )

        except Exception as e:
            logger.error(f"Error analyzing options market: {e}")
            raise

    async def analyze_price_action(self, data: Dict) -> PriceAnalysis:
        """Analyze underlying asset's price action"""
        df = pd.DataFrame(data['price_history'])
        
        # Calculate moving averages
        sma = {
            "20": self._calculate_sma(df, 20),
            "50": self._calculate_sma(df, 50),
            "200": self._calculate_sma(df, 200)
        }
        
        ema = {
            "9": self._calculate_ema(df, 9),
            "21": self._calculate_ema(df, 21),
            "55": self._calculate_ema(df, 55)
        }
        
        # Calculate other indicators
        vwap = self._calculate_vwap(df)
        rsi = self._calculate_rsi(df)
        macd = self._calculate_macd(df)
        stoch = self._calculate_stochastic(df)
        boll = self._calculate_bollinger_bands(df)
        atr = self._calculate_atr(df)

        # Analyze trend and volatility context
        trend_strength = self._analyze_trend_strength(df, ema, macd)
        support_resistance = self._find_support_resistance(df)
        vol_regime = self._determine_volatility_regime(df, boll["middle"], atr)

        return PriceAnalysis(
            sma=sma,
            ema=ema,
            vwap=vwap,
            rsi=rsi,
            macd=macd,
            stochastic=stoch,
            bollinger=boll,
            atr=atr,
            trend_strength=trend_strength,
            support_resistance=support_resistance,
            volatility_regime=vol_regime
        )

    def _calculate_iv_rank(self, data: Dict) -> float:
        """Calculate IV Rank (current IV's position between 52-week high and low)"""
        current_iv = data['current_iv']
        iv_high = data['iv_52week_high']
        iv_low = data['iv_52week_low']
        return (current_iv - iv_low) / (iv_high - iv_low) * 100

    def _calculate_iv_percentile(self, data: Dict) -> float:
        """Calculate IV Percentile (% of days IV was lower than current)"""
        historical_ivs = np.array(data['historical_ivs'])
        current_iv = data['current_iv']
        return (historical_ivs < current_iv).mean() * 100

    def _analyze_volatility_term_structure(self, data: Dict) -> Dict[str, float]:
        """Analyze volatility across different expiration dates"""
        return {
            expiry: iv 
            for expiry, iv in data['term_structure'].items()
        }

    def _analyze_volatility_skew(self, data: Dict) -> Dict[str, float]:
        """Analyze volatility skew (difference in IV between OTM puts and calls)"""
        return {
            strike: iv_diff 
            for strike, iv_diff in data['skew_data'].items()
        }

    def _calculate_gamma_exposure(self, data: Dict) -> float:
        """Calculate total gamma exposure at different price levels"""
        return sum(
            position['gamma'] * position['open_interest']
            for position in data['options_positions']
        )

    def _calculate_put_call_ratio(self, data: Dict) -> float:
        """Calculate put/call ratio based on volume and open interest"""
        put_volume = sum(data['put_volumes'].values())
        call_volume = sum(data['call_volumes'].values())
        return put_volume / call_volume if call_volume > 0 else float('inf')

    def _analyze_open_interest(self, data: Dict) -> Dict[str, int]:
        """Analyze open interest distribution across strikes"""
        return {
            strike: oi 
            for strike, oi in data['open_interest'].items()
        }

    def _calculate_max_pain(self, data: Dict) -> float:
        """Calculate max pain point (strike price where options sellers have least liability)"""
        total_value = {}
        for strike in data['strikes']:
            value = self._calculate_options_value_at_strike(data, strike)
            total_value[strike] = value
        return min(total_value.items(), key=lambda x: x[1])[0]

    def _calculate_historical_volatility(self, data: Dict) -> float:
        """Calculate historical volatility"""
        returns = np.log(data['closes'][1:] / data['closes'][:-1])
        return np.std(returns) * np.sqrt(365) * 100 

    def _calculate_sma(self, df: pd.DataFrame, period: int) -> float:
        return df['close'].rolling(window=period).mean().iloc[-1]

    def _calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        return df['close'].ewm(span=period, adjust=False).mean().iloc[-1]

    def _calculate_vwap(self, df: pd.DataFrame) -> float:
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).sum() / df['volume'].sum()

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs.iloc[-1]))

    def _calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            "macd": macd_line.iloc[-1],
            "signal": signal_line.iloc[-1],
            "histogram": histogram.iloc[-1]
        }

    def _calculate_stochastic(self, df: pd.DataFrame) -> Dict[str, float]:
        low_min = df['low'].rolling(14).min()
        high_max = df['high'].rolling(14).max()
        k = 100 * (df['close'] - low_min) / (high_max - low_min)
        d = k.rolling(3).mean()
        return {"k": k.iloc[-1], "d": d.iloc[-1]}

    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, float]:
        middle = df['close'].rolling(20).mean()
        std = df['close'].rolling(20).std()
        return {
            "upper": middle + (2 * std),
            "middle": middle,
            "lower": middle - (2 * std)
        }

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean().iloc[-1]

    def analyze_chart_patterns(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify chart patterns in price action"""
        patterns = []
        
        # Check for common patterns
        patterns.extend(self._find_double_tops_bottoms(df))
        patterns.extend(self._find_head_and_shoulders(df))
        patterns.extend(self._find_triangles(df))
        patterns.extend(self._find_channels(df))
        patterns.extend(self._find_wedges(df))
        
        return patterns

    def analyze_candlestick_patterns(self, df: pd.DataFrame) -> List[CandlestickPattern]:
        """Identify Japanese candlestick patterns"""
        patterns = []
        
        # Single candlestick patterns
        patterns.extend(self._find_doji(df))
        patterns.extend(self._find_hammer_shooting_star(df))
        
        # Multiple candlestick patterns
        patterns.extend(self._find_engulfing_patterns(df))
        patterns.extend(self._find_three_line_strike(df))
        patterns.extend(self._find_morning_evening_stars(df))
        
        return patterns

    def _find_double_tops_bottoms(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify double top/bottom reversal patterns"""
        patterns = []
        window = 20  # Look back period
        
        for i in range(window, len(df)):
            slice_df = df.iloc[i-window:i]
            peaks = self._find_peaks(slice_df['high'])
            troughs = self._find_peaks(-slice_df['low'])
            
            # Check for double tops
            if len(peaks) >= 2:
                if self._validate_double_top(slice_df, peaks):
                    patterns.append(ChartPattern(
                        pattern_type="double_top",
                        confidence=self._calculate_pattern_confidence(slice_df, peaks),
                        price_target=self._calculate_price_target(slice_df, peaks, pattern="double_top"),
                        stop_loss=max(peaks) + (slice_df['atr'].iloc[-1] * 1.5),
                        formation_points=[{"price": p, "time": slice_df.index[i]} for i, p in enumerate(peaks)],
                        volume_confirms=self._check_volume_confirmation(slice_df, peaks)
                    ))
            
            # Check for double bottoms
            if len(troughs) >= 2:
                if self._validate_double_bottom(slice_df, troughs):
                    patterns.append(ChartPattern(
                        pattern_type="double_bottom",
                        confidence=self._calculate_pattern_confidence(slice_df, troughs),
                        price_target=self._calculate_price_target(slice_df, troughs, pattern="double_bottom"),
                        stop_loss=min(troughs) - (slice_df['atr'].iloc[-1] * 1.5),
                        formation_points=[{"price": p, "time": slice_df.index[i]} for i, p in enumerate(troughs)],
                        volume_confirms=self._check_volume_confirmation(slice_df, troughs)
                    ))
        
        return patterns

    def _find_head_and_shoulders(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify head and shoulders patterns (both regular and inverse)"""
        patterns = []
        window = 30
        
        for i in range(window, len(df)):
            slice_df = df.iloc[i-window:i]
            peaks = self._find_peaks(slice_df['high'])
            troughs = self._find_peaks(-slice_df['low'])
            
            # Check for regular H&S
            if len(peaks) >= 3:
                if self._validate_head_and_shoulders(slice_df, peaks):
                    patterns.append(ChartPattern(
                        pattern_type="head_and_shoulders",
                        confidence=self._calculate_pattern_confidence(slice_df, peaks),
                        price_target=self._calculate_hs_target(slice_df, peaks),
                        stop_loss=max(peaks) + (slice_df['atr'].iloc[-1] * 2),
                        formation_points=self._get_hs_points(slice_df, peaks),
                        volume_confirms=self._check_hs_volume(slice_df, peaks)
                    ))
            
            # Check for inverse H&S
            if len(troughs) >= 3:
                if self._validate_inverse_head_and_shoulders(slice_df, troughs):
                    patterns.append(ChartPattern(
                        pattern_type="inverse_head_and_shoulders",
                        confidence=self._calculate_pattern_confidence(slice_df, troughs),
                        price_target=self._calculate_ihs_target(slice_df, troughs),
                        stop_loss=min(troughs) - (slice_df['atr'].iloc[-1] * 2),
                        formation_points=self._get_ihs_points(slice_df, troughs),
                        volume_confirms=self._check_ihs_volume(slice_df, troughs)
                    ))
        
        return patterns

    def _find_triangles(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify ascending, descending, and symmetric triangles"""
        # Implementation for triangle patterns
        pass

    def _find_channels(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify price channels (ascending, descending, horizontal)"""
        # Implementation for channel patterns
        pass

    def _find_wedges(self, df: pd.DataFrame) -> List[ChartPattern]:
        """Identify rising and falling wedges"""
        # Implementation for wedge patterns
        pass

    def _calculate_pattern_confidence(self, df: pd.DataFrame, points: List[float]) -> float:
        """Calculate confidence score for a pattern"""
        # Implement confidence calculation based on:
        # - Pattern formation quality
        # - Volume confirmation
        # - Market context
        # - Support/resistance levels
        pass