from dataclasses import dataclass
from typing import List, Dict
import pandas as pd
import numpy as np
from loguru import logger

@dataclass
class CryptoPattern:
    pattern_type: str
    confidence: float
    price_target: float
    stop_loss: float
    volume_profile: Dict
    liquidation_levels: List[float]  # Important for crypto due to leverage
    funding_rate: float              # Perpetual futures specific
    open_interest_impact: float

class CryptoPatternAnalyzer:
    """Crypto-specific chart pattern analyzer"""
    
    def analyze_patterns(self, df: pd.DataFrame) -> List[CryptoPattern]:
        patterns = []
        
        # Wyckoff Patterns (very important in crypto)
        patterns.extend(self._find_wyckoff_accumulation(df))
        patterns.extend(self._find_wyckoff_distribution(df))
        
        # Orderblock Patterns (institutional levels)
        patterns.extend(self._find_orderblocks(df))
        
        # Liquidation Levels (unique to crypto)
        patterns.extend(self._find_liquidation_cascades(df))
        
        # Volume Profile Patterns
        patterns.extend(self._analyze_volume_profile(df))
        
        return patterns

    def _find_wyckoff_accumulation(self, df: pd.DataFrame) -> List[CryptoPattern]:
        """
        Identify Wyckoff Accumulation Patterns:
        - Phase A (SC - Spring)
        - Phase B (Secondary Test)
        - Phase C (LPS - Last Point of Support)
        - Phase D (Sign of Strength)
        """
        patterns = []
        window = 30  # Typical Wyckoff pattern window
        
        for i in range(window, len(df)):
            slice_df = df.iloc[i-window:i]
            
            # Look for Spring pattern (key Wyckoff signal)
            if self._is_spring_pattern(slice_df):
                patterns.append(CryptoPattern(
                    pattern_type="wyckoff_spring",
                    confidence=self._calculate_spring_confidence(slice_df),
                    price_target=self._calculate_wyckoff_target(slice_df, "spring"),
                    stop_loss=slice_df['low'].min(),
                    volume_profile=self._get_volume_profile(slice_df),
                    liquidation_levels=self._find_nearby_liquidations(slice_df),
                    funding_rate=self._get_current_funding_rate(slice_df),
                    open_interest_impact=self._calculate_oi_impact(slice_df)
                ))
        
        return patterns

    def _find_orderblocks(self, df: pd.DataFrame) -> List[CryptoPattern]:
        """
        Identify Institutional Orderblocks:
        - Bullish Orderblocks (strong rejection from below)
        - Bearish Orderblocks (strong rejection from above)
        - Focus on high volume nodes
        """
        patterns = []
        window = 15  # Orderblock formation window
        
        for i in range(window, len(df)):
            slice_df = df.iloc[i-window:i]
            
            # Look for high volume rejection candles
            if self._is_orderblock_candle(slice_df):
                patterns.append(CryptoPattern(
                    pattern_type="orderblock",
                    confidence=self._calculate_orderblock_strength(slice_df),
                    price_target=self._calculate_orderblock_target(slice_df),
                    stop_loss=self._calculate_orderblock_invalidation(slice_df),
                    volume_profile=self._get_volume_profile(slice_df),
                    liquidation_levels=self._find_nearby_liquidations(slice_df),
                    funding_rate=self._get_current_funding_rate(slice_df),
                    open_interest_impact=self._calculate_oi_impact(slice_df)
                ))
        
        return patterns

    def _find_liquidation_cascades(self, df: pd.DataFrame) -> List[CryptoPattern]:
        """
        Identify potential liquidation cascades:
        - Large open interest levels
        - Historical liquidation points
        - Funding rate extremes
        """
        patterns = []
        
        # Look for high concentration of liquidation levels
        liquidation_levels = self._aggregate_liquidation_levels(df)
        for level in liquidation_levels:
            if self._is_significant_liquidation_level(level, df):
                patterns.append(CryptoPattern(
                    pattern_type="liquidation_cascade",
                    confidence=self._calculate_liquidation_probability(level, df),
                    price_target=self._calculate_cascade_target(level, df),
                    stop_loss=self._calculate_cascade_stop(level, df),
                    volume_profile=self._get_volume_profile(df),
                    liquidation_levels=[level],
                    funding_rate=self._get_current_funding_rate(df),
                    open_interest_impact=self._calculate_oi_impact(df)
                ))
        
        return patterns

    def _analyze_volume_profile(self, df: pd.DataFrame) -> List[CryptoPattern]:
        """
        Analyze Volume Profile for key levels:
        - High Volume Nodes (HVN)
        - Low Volume Nodes (LVN)
        - Point of Control (POC)
        """
        patterns = []
        
        # Calculate Volume Profile
        volume_profile = self._calculate_volume_profile(df)
        
        # Find significant volume levels
        hvn_levels = self._find_high_volume_nodes(volume_profile)
        lvn_levels = self._find_low_volume_nodes(volume_profile)
        poc = self._find_point_of_control(volume_profile)
        
        # Add significant levels as patterns
        for level in hvn_levels:
            patterns.append(CryptoPattern(
                pattern_type="high_volume_node",
                confidence=self._calculate_hvn_significance(level, volume_profile),
                price_target=self._calculate_hvn_target(level, df),
                stop_loss=self._calculate_hvn_stop(level, df),
                volume_profile=volume_profile,
                liquidation_levels=self._find_nearby_liquidations(df, level),
                funding_rate=self._get_current_funding_rate(df),
                open_interest_impact=self._calculate_oi_impact(df)
            ))
        
        return patterns

    # Helper methods for pattern validation and calculations... 