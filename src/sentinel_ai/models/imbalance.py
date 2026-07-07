"""
MODULE: MODEL-007
FILE: MODEL-007-001
Module Name: Imbalance Models
Version: 0.9.2
Purpose: Defines immutable fair-value-gap and order-block analysis results used by replaceable analysis engines.
Dependencies: dataclasses, datetime
Change History:
- 0.9.2: Added fair value gap, order block, and imbalance snapshot models for boxed overlay rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FairValueGapZone:
    """Represent one bullish or bearish fair value gap zone."""

    direction: str
    lower_price: float
    upper_price: float
    created_at: datetime
    start_time: datetime
    end_time: datetime
    filled: bool
    partially_mitigated: bool
    source_candle_index: int

    @property
    def is_bullish(self) -> bool:
        return self.direction == "BULLISH"

    @property
    def is_bearish(self) -> bool:
        return self.direction == "BEARISH"

    @property
    def label(self) -> str:
        return "FVG↑" if self.is_bullish else "FVG↓"


@dataclass(frozen=True)
class OrderBlockZone:
    """Represent one bullish or bearish order block zone."""

    direction: str
    lower_price: float
    upper_price: float
    created_at: datetime
    start_time: datetime
    end_time: datetime
    mitigated: bool
    invalidated: bool
    source_candle_index: int
    source_break_time: datetime

    @property
    def is_bullish(self) -> bool:
        return self.direction == "BULLISH"

    @property
    def is_bearish(self) -> bool:
        return self.direction == "BEARISH"

    @property
    def label(self) -> str:
        return "OB↑" if self.is_bullish else "OB↓"


@dataclass(frozen=True)
class ImbalanceSnapshot:
    """Represent a read-only imbalance analysis snapshot."""

    symbol: str
    timeframe: str
    fair_value_gaps: tuple[FairValueGapZone, ...]
    order_blocks: tuple[OrderBlockZone, ...]
    latest_bullish_fvg: FairValueGapZone | None
    latest_bearish_fvg: FairValueGapZone | None
    latest_bullish_order_block: OrderBlockZone | None
    latest_bearish_order_block: OrderBlockZone | None
    generated_at: datetime
    analyzed_candle_count: int
    summary: str
