"""
MODULE: MODEL-006
FILE: MODEL-006-001
Module Name: Liquidity Models
Version: 0.9.0
Purpose: Defines immutable liquidity pool and liquidity sweep analysis results used by replaceable analysis engines.
Dependencies: dataclasses, datetime
Change History:
- 0.9.0: Added liquidity pool, liquidity sweep, and liquidity snapshot models for Sprint 9.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LiquidityPool:
    """Represent a liquidity pool resting above a swing high or below a swing low."""

    side: str
    price: float
    reference_time: datetime
    reference_kind: str
    swept: bool
    inducement_candidate: bool
    distance_from_price: float
    label: str

    @property
    def is_buy_side(self) -> bool:
        """Return True when the pool is buy-side liquidity above a swing high."""
        return self.side == "BUY_SIDE"

    @property
    def is_sell_side(self) -> bool:
        """Return True when the pool is sell-side liquidity below a swing low."""
        return self.side == "SELL_SIDE"


@dataclass(frozen=True)
class LiquiditySweep:
    """Represent a confirmed liquidity sweep using wick violation and close-back confirmation."""

    direction: str
    swept_side: str
    reference_price: float
    reference_time: datetime
    swept_at: datetime
    wick_price: float
    close_price: float
    label: str

    @property
    def is_bullish(self) -> bool:
        """Return True when the sweep is bullish after sell-side liquidity was taken."""
        return self.direction == "BULLISH"

    @property
    def is_bearish(self) -> bool:
        """Return True when the sweep is bearish after buy-side liquidity was taken."""
        return self.direction == "BEARISH"


@dataclass(frozen=True)
class LiquiditySnapshot:
    """Represent a read-only liquidity analysis snapshot."""

    symbol: str
    timeframe: str
    pools: tuple[LiquidityPool, ...]
    sweeps: tuple[LiquiditySweep, ...]
    latest_bullish_sweep: LiquiditySweep | None
    latest_bearish_sweep: LiquiditySweep | None
    generated_at: datetime
    analyzed_candle_count: int
    summary: str

    @property
    def active_pools(self) -> tuple[LiquidityPool, ...]:
        """Return liquidity pools that have not yet been swept."""
        return tuple(pool for pool in self.pools if not pool.swept)

    @property
    def inducement_candidates(self) -> tuple[LiquidityPool, ...]:
        """Return active pools close enough to price to be tracked as possible inducement."""
        return tuple(pool for pool in self.pools if pool.inducement_candidate)
