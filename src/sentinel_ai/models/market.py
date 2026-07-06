"""
MODULE: MODEL-002
FILE: MODEL-002-001
Module Name: Market Data Models
Version: 0.2.0
Purpose: Defines immutable market connectivity, symbol, account, and OHLC data models.
Dependencies: dataclasses, datetime
Change History:
- 0.2.0: Added MT5 foundation models for connection status, account snapshots, symbol validation, and market bars.
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
    """Represent one OHLCV candle returned by MT5."""

    time: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int
