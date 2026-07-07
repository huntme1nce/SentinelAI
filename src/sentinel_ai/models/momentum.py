"""
MODULE: MODEL-009
FILE: MODEL-009-001
Module Name: Momentum Models
Version: 1.0.0
Purpose: Defines immutable momentum analysis results used by the replaceable Momentum Engine.
Dependencies: dataclasses, datetime
Change History:
- 1.0.0: Added EMA, MACD, stochastic, candle momentum, and composite momentum snapshot models.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmaMomentumState:
    """Represent EMA alignment and slope context."""

    fast_ema: float
    slow_ema: float
    spread: float
    slope: float
    bias: str
    summary: str


@dataclass(frozen=True)
class MacdMomentumState:
    """Represent MACD line, signal line, histogram, and directional context."""

    macd_line: float
    signal_line: float
    histogram: float
    previous_histogram: float
    bias: str
    summary: str


@dataclass(frozen=True)
class StochasticMomentumState:
    """Represent stochastic oscillator context."""

    percent_k: float
    percent_d: float
    bias: str
    zone: str
    summary: str


@dataclass(frozen=True)
class CandleMomentumState:
    """Represent recent candle-body momentum context."""

    average_body_ratio: float
    latest_body_ratio: float
    bullish_body_count: int
    bearish_body_count: int
    bias: str
    summary: str


@dataclass(frozen=True)
class MomentumSnapshot:
    """Represent a read-only momentum analysis snapshot."""

    symbol: str
    timeframe: str
    bias: str
    ema: EmaMomentumState | None
    macd: MacdMomentumState | None
    stochastic: StochasticMomentumState | None
    candle_momentum: CandleMomentumState | None
    generated_at: datetime
    analyzed_candle_count: int
    summary: str
    confirmation_score: int
