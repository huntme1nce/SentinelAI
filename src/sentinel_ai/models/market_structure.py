"""
MODULE: MODEL-004
FILE: MODEL-004-001
Module Name: Market Structure Models
Version: 0.7.0
Purpose: Defines immutable market-structure analysis results used by replaceable analysis engines.
Dependencies: dataclasses, datetime
Change History:
- 0.7.0: Added swing point, structure break, and market structure snapshot models for Sprint 7.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SwingPoint:
    """Represent a confirmed swing high or swing low detected from candle structure."""

    kind: str
    time: datetime
    price: float
    candle_index: int

    @property
    def is_high(self) -> bool:
        """Return True when this swing represents a swing high."""
        return self.kind == "HIGH"

    @property
    def is_low(self) -> bool:
        """Return True when this swing represents a swing low."""
        return self.kind == "LOW"


@dataclass(frozen=True)
class StructureBreak:
    """Represent the latest confirmed break of market structure when present."""

    direction: str
    reference_price: float
    reference_time: datetime
    broken_at: datetime
    close_price: float

    @property
    def is_bullish(self) -> bool:
        """Return True when the structure break is bullish."""
        return self.direction == "BULLISH"

    @property
    def is_bearish(self) -> bool:
        """Return True when the structure break is bearish."""
        return self.direction == "BEARISH"


@dataclass(frozen=True)
class MarketStructureSnapshot:
    """Represent a read-only market-structure analysis snapshot."""

    symbol: str
    timeframe: str
    bias: str
    swing_highs: tuple[SwingPoint, ...]
    swing_lows: tuple[SwingPoint, ...]
    latest_break: StructureBreak | None
    analyzed_candle_count: int
    generated_at: datetime
    summary: str

    @property
    def latest_swing_high(self) -> SwingPoint | None:
        """Return the most recent confirmed swing high when available."""
        if not self.swing_highs:
            return None
        return self.swing_highs[-1]

    @property
    def latest_swing_low(self) -> SwingPoint | None:
        """Return the most recent confirmed swing low when available."""
        if not self.swing_lows:
            return None
        return self.swing_lows[-1]

    @property
    def has_sufficient_structure(self) -> bool:
        """Return True when there are enough confirmed swings for structural interpretation."""
        return len(self.swing_highs) >= 2 and len(self.swing_lows) >= 2

    @property
    def marker_points(self) -> tuple[SwingPoint, ...]:
        """Return all swing markers ordered by candle index for chart display."""
        return tuple(sorted((*self.swing_highs, *self.swing_lows), key=lambda swing: swing.candle_index))
