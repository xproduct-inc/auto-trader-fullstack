import yaml
from typing import Dict, Any
from pathlib import Path
from loguru import logger

class IndicatorConfig:
    def __init__(self, config_path: str = "config/indicators.yml"):
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(Path(path)) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading indicator config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails"""
        return {
            "technical_analysis": {
                "enabled": True,
                "timeframes": ["5m", "15m", "1h"],
                "options_indicators": {
                    "enabled": True,
                    "indicators": {
                        "iv_rank": {"enabled": True},
                        "gamma_exposure": {"enabled": True}
                    }
                },
                "chart_patterns": {
                    "enabled": True,
                    "patterns": {
                        "wyckoff": {"enabled": True},
                        "orderblocks": {"enabled": True}
                    }
                }
            }
        }

    def is_indicator_enabled(self, category: str, indicator: str) -> bool:
        """Check if specific indicator is enabled"""
        try:
            return (
                self.config["technical_analysis"]["enabled"] and
                self.config["technical_analysis"][category]["enabled"] and
                self.config["technical_analysis"][category]["indicators"][indicator]["enabled"]
            )
        except KeyError:
            return False

    def get_indicator_config(self, category: str, indicator: str) -> Dict:
        """Get configuration for specific indicator"""
        try:
            return self.config["technical_analysis"][category]["indicators"][indicator]
        except KeyError:
            return {} 