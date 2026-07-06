"""
MODULE: MT5-001
FILE: MT5-001-002
Module Name: MT5 Timeframe Mapper
Version: 0.2.0
Purpose: Maps Sentinel AI timeframe labels to MetaTrader5 timeframe constants.
Dependencies: typing, sentinel_ai.mt5.exceptions
Change History:
- 0.2.0: Added explicit timeframe mapping for safe MT5 market-data requests.
"""

from __future__ import annotations

from typing import Any

from sentinel_ai.mt5.exceptions import Mt5TimeframeError


class Mt5TimeframeMapper:
    """Map approved timeframe strings to MT5 constants."""

    SUPPORTED_TIMEFRAMES = ("M1", "M5", "M15", "M30", "H1", "H4", "D1")

    @classmethod
    def to_mt5_constant(cls, timeframe: str, mt5_module: Any) -> int:
        """Return the MT5 timeframe constant for a Sentinel AI timeframe label."""
        normalized = timeframe.strip().upper()
        attribute_name = f"TIMEFRAME_{normalized}"
        if normalized not in cls.SUPPORTED_TIMEFRAMES or not hasattr(mt5_module, attribute_name):
            raise Mt5TimeframeError(f"Unsupported MT5 timeframe: {timeframe}")
        return int(getattr(mt5_module, attribute_name))
