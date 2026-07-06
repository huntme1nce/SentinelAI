"""
MODULE: MODEL-005
FILE: MODEL-005-001
Module Name: Support and Resistance Models
Version: 0.9.1
Purpose: Defines immutable support/resistance zone analysis results used by replaceable analysis engines.
Dependencies: dataclasses, datetime
Change History:
- 0.8.0: Added support/resistance zone and snapshot models for Sprint 8.
- 0.9.1: Exposed bounded segment timing helpers for chart overlays.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SupportResistanceZone:
    """Represent one ranked support or resistance zone derived from confirmed market structure swings."""

    kind: str
    lower_price: float
    upper_price: float
    midpoint: float
    touch_count: int
    first_seen: datetime
    last_seen: datetime
    distance_from_price: float
    strength_score: float
    rank: int

    @property
    def is_support(self) -> bool:
        """Return True when this zone is classified as support."""
        return self.kind == "SUPPORT"

    @property
    def is_resistance(self) -> bool:
        """Return True when this zone is classified as resistance."""
        return self.kind == "RESISTANCE"

    @property
    def label(self) -> str:
        """Return the compact chart label for this zone."""
        prefix = "S" if self.is_support else "R"
        return f"{prefix}{self.rank}"

    @property
    def segment_start_time(self) -> datetime:
        """Return the first candle time used by the chart to start this bounded zone segment."""
        return self.first_seen

    @property
    def segment_end_time(self) -> datetime:
        """Return the last candle time used by the chart to end this bounded zone segment."""
        return self.last_seen

    def contains_price(self, price: float) -> bool:
        """Return True when the supplied price is inside this zone boundary."""
        numeric_price = float(price)
        return self.lower_price <= numeric_price <= self.upper_price


@dataclass(frozen=True)
class SupportResistanceSnapshot:
    """Represent a read-only support/resistance analysis snapshot."""

    symbol: str
    timeframe: str
    support_zones: tuple[SupportResistanceZone, ...]
    resistance_zones: tuple[SupportResistanceZone, ...]
    nearest_support: SupportResistanceZone | None
    nearest_resistance: SupportResistanceZone | None
    generated_at: datetime
    analyzed_swing_count: int
    zone_tolerance_price: float
    summary: str

    @property
    def all_zones(self) -> tuple[SupportResistanceZone, ...]:
        """Return all zones ordered by type and rank for chart display."""
        return (*self.support_zones, *self.resistance_zones)
