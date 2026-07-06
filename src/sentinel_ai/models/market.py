"""
MODULE: MODEL-002
FILE: MODEL-002-001
Module Name: Market Data Models
Version: 0.4.0
Purpose: Defines immutable market connectivity, symbol, account, OHLC, and chart-feed data models.
Dependencies: dataclasses, datetime
Change History:
- 0.2.0: Added MT5 foundation models for connection status, account snapshots, symbol validation, and market bars.
- 0.3.0: Added market data snapshot and Lightweight Charts candle models for Sprint 3 feed foundation.
- 0.4.0: Preserved immutable candle models for Sprint 4 chart rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Mt5ConnectionStatus:
    """Represent the current MetaTrader 5 connection state."""

    connected: bool
    message: str
    terminal_name: str | None = None
    company: str | None = None
    server: str | None = None
    login: int | None = None


@dataclass(frozen=True)
class Mt5AccountSnapshot:
    """Represent read-only account details returned by MT5."""

    login: int
    server: str
    name: str
    company: str
    currency: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    leverage: int


@dataclass(frozen=True)
class SymbolValidationResult:
    """Represent the result of validating a broker symbol in MT5."""

    symbol: str
    valid: bool
    visible: bool
    selected: bool
    message: str
    digits: int | None = None
    point: float | None = None
    spread: int | None = None


@dataclass(frozen=True)
class MarketBar:
    """Represent one normalized OHLCV candle returned by a market data source."""

    time: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int


@dataclass(frozen=True)
class ChartCandle:
    """Represent one candle formatted for TradingView Lightweight Charts."""

    time: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class MarketDataSnapshot:
    """Represent a validated candle-feed snapshot for one symbol and timeframe."""

    symbol: str
    timeframe: str
    candles: tuple[MarketBar, ...]
    chart_candles: tuple[ChartCandle, ...]
    source: str
    loaded_at: datetime

    @property
    def candle_count(self) -> int:
        """Return the number of normalized candles in the snapshot."""
        return len(self.candles)

    @property
    def latest_candle(self) -> MarketBar | None:
        """Return the newest candle when the snapshot contains market data."""
        if not self.candles:
            return None
        return self.candles[-1]

    @property
    def is_empty(self) -> bool:
        """Return True when the snapshot contains no candles."""
        return not self.candles
