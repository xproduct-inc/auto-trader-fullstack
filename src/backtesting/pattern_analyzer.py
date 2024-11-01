from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from loguru import logger

class PatternAnalyzer:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.lstm_model = self._build_lstm_model()
        
    def analyze_patterns(self, data: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Analyze all significant crypto chart patterns"""
        patterns = {
            "wyckoff": self._analyze_wyckoff(data),
            "orderblocks": self._analyze_orderblocks(data),
            "liquidity_levels": self._analyze_liquidity_levels(data),
            "smart_money_concepts": self._analyze_smc(data)
        }
        
        # Use ML to validate patterns
        validated_patterns = self._validate_patterns_with_ml(patterns, data)
        return validated_patterns

    def _analyze_wyckoff(self, data: pd.DataFrame) -> List[Dict]:
        """Identify Wyckoff accumulation/distribution patterns"""
        patterns = []
        window = 100  # Typical Wyckoff pattern window
        
        for i in range(len(data) - window):
            slice_df = data.iloc[i:i+window]
            
            # Phase identification using volume and price action
            if self._is_wyckoff_accumulation(slice_df):
                patterns.append({
                    "type": "wyckoff_accumulation",
                    "start_idx": i,
                    "end_idx": i + window,
                    "confidence": self._calculate_wyckoff_confidence(slice_df),
                    "phase": self._identify_wyckoff_phase(slice_df)
                })
                
        return patterns

    def _analyze_orderblocks(self, data: pd.DataFrame) -> List[Dict]:
        """Identify institutional orderblock patterns"""
        patterns = []
        
        # Look for strong rejection candles with high volume
        for i in range(len(data) - 1):
            if self._is_orderblock_candle(data.iloc[i]):
                patterns.append({
                    "type": "orderblock",
                    "position": "bullish" if self._is_bullish_orderblock(data.iloc[i]) else "bearish",
                    "price_level": data.iloc[i].close,
                    "volume_ratio": data.iloc[i].volume / data.volume.mean(),
                    "strength": self._calculate_orderblock_strength(data.iloc[i:i+10])
                })
                
        return patterns

    def _analyze_liquidity_levels(self, data: pd.DataFrame) -> List[Dict]:
        """Identify liquidity levels and sweeps"""
        levels = []
        
        # Identify swing highs/lows with stop clusters
        swings = self._find_swing_points(data)
        for swing in swings:
            if self._has_stop_cluster(data, swing["price"]):
                levels.append({
                    "type": "liquidity_level",
                    "price": swing["price"],
                    "side": swing["type"],  # "high" or "low"
                    "strength": self._calculate_liquidity_strength(data, swing),
                    "stop_density": self._calculate_stop_density(data, swing["price"])
                })
                
        return levels

    def _analyze_smc(self, data: pd.DataFrame) -> List[Dict]:
        """Smart Money Concepts analysis"""
        patterns = []
        
        # Identify manipulation and institutional moves
        patterns.extend(self._find_stop_hunts(data))
        patterns.extend(self._find_liquidity_grabs(data))
        patterns.extend(self._find_institutional_moves(data))
        
        return patterns

    def _build_lstm_model(self) -> tf.keras.Model:
        """Build LSTM model for pattern validation"""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(100, 5)),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def _validate_patterns_with_ml(self, patterns: Dict, data: pd.DataFrame) -> Dict:
        """Validate detected patterns using ML models"""
        validated_patterns = {}
        
        for pattern_type, pattern_list in patterns.items():
            features = self._extract_pattern_features(data, pattern_list)
            
            # Random Forest validation
            rf_scores = self.rf_model.predict_proba(features)
            
            # LSTM validation
            lstm_scores = self._validate_with_lstm(data, pattern_list)
            
            # Combine scores and filter patterns
            validated_patterns[pattern_type] = [
                {**pattern, "ml_confidence": (rf + lstm) / 2}
                for pattern, rf, lstm in zip(pattern_list, rf_scores[:, 1], lstm_scores)
                if (rf + lstm) / 2 > 0.7  # Only keep high confidence patterns
            ]
            
        return validated_patterns

    def _extract_pattern_features(self, data: pd.DataFrame, patterns: List[Dict]) -> np.ndarray:
        """Extract features for ML validation"""
        features = []
        for pattern in patterns:
            if "start_idx" in pattern and "end_idx" in pattern:
                window = data.iloc[pattern["start_idx"]:pattern["end_idx"]]
            else:
                # For point patterns, take surrounding context
                idx = data.index.get_loc(pattern.get("timestamp", data.index[-1]))
                window = data.iloc[max(0, idx-50):min(len(data), idx+50)]
            
            features.append([
                self._calculate_volume_profile(window),
                self._calculate_price_momentum(window),
                self._calculate_volatility_features(window),
                self._calculate_pattern_specific_features(window, pattern["type"])
            ])
        
        return np.array(features)

    def _validate_with_lstm(self, data: pd.DataFrame, patterns: List[Dict]) -> np.ndarray:
        """Validate patterns using LSTM model"""
        sequences = []
        for pattern in patterns:
            if "start_idx" in pattern and "end_idx" in pattern:
                window = data.iloc[pattern["start_idx"]:pattern["end_idx"]]
            else:
                idx = data.index.get_loc(pattern.get("timestamp", data.index[-1]))
                window = data.iloc[max(0, idx-50):min(len(data), idx+50)]
            
            # Prepare sequence data
            sequence = np.column_stack([
                window.open, window.high, window.low, window.close, window.volume
            ])
            sequences.append(sequence)
            
        sequences = tf.keras.preprocessing.sequence.pad_sequences(
            sequences, maxlen=100, padding='post'
        )
        
        return self.lstm_model.predict(sequences) 