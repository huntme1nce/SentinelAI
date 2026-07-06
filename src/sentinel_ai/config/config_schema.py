"""
MODULE: CFG-001
FILE: CFG-001-001
Module Name: Configuration Schema
Version: 0.7.0
Purpose: Defines validated configuration models for Sentinel AI, including analysis-engine settings.
Dependencies: dataclasses, typing
Change History:
- 0.1.0: Added application, trading, database, logging, and UI configuration models.
- 0.2.0: Added MT5 connection configuration for Sprint 2.
- 0.3.0: Added market data feed configuration for Sprint 3.
- 0.4.0: Preserved schema for Sprint 4 chart rendering without adding trading settings.
- 0.5.0: Added market-data live refresh configuration with timeframe-specific intervals.
- 0.5.1: Preserved validated refresh configuration while allowing one-second synchronization defaults.
- 0.6.0: Added symbol-management configuration for account-specific MT5 symbol resolution.
- 0.7.0: Added market structure engine configuration for Sprint 7 analysis foundation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApplicationConfig:
    """Represent application identity and runtime mode settings."""

    name: str
    version: str
    environment: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApplicationConfig":
        """Create an ApplicationConfig from a dictionary."""
        return cls(
            name=str(data["name"]),
            version=str(data["version"]),
            environment=str(data["environment"]),
        )


@dataclass(frozen=True)
class TradingConfig:
    """Represent conservative default trading control settings."""

    symbol: str
    default_timeframe: str
    auto_trade_enabled: bool
    one_trade_at_a_time: bool
    minimum_confidence: float
    default_risk_reward: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingConfig":
        """Create a TradingConfig from a dictionary."""
        return cls(
            symbol=str(data["symbol"]),
            default_timeframe=str(data["default_timeframe"]),
            auto_trade_enabled=bool(data["auto_trade_enabled"]),
            one_trade_at_a_time=bool(data["one_trade_at_a_time"]),
            minimum_confidence=float(data["minimum_confidence"]),
            default_risk_reward=float(data["default_risk_reward"]),
        )


@dataclass(frozen=True)
class SymbolManagementConfig:
    """Represent broker/account-specific symbol management settings."""

    auto_resolve_enabled: bool
    preferred_aliases: tuple[str, ...]
    toolbar_max_symbols: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolManagementConfig":
        """Create a SymbolManagementConfig from a dictionary."""
        raw_aliases = data["preferred_aliases"]
        if not isinstance(raw_aliases, list):
            raise ValueError("symbol_management.preferred_aliases must be a JSON array.")
        aliases = tuple(str(alias).strip() for alias in raw_aliases if str(alias).strip())
        toolbar_max_symbols = int(data["toolbar_max_symbols"])
        if toolbar_max_symbols < 1:
            raise ValueError("symbol_management.toolbar_max_symbols must be greater than zero.")
        return cls(
            auto_resolve_enabled=bool(data["auto_resolve_enabled"]),
            preferred_aliases=aliases,
            toolbar_max_symbols=toolbar_max_symbols,
        )


@dataclass(frozen=True)
class Mt5Config:
    """Represent MetaTrader 5 connection and market-data settings."""

    startup_connect: bool
    terminal_path: str | None
    default_bar_count: int
    max_bars_per_request: int
    require_visible_symbol: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mt5Config":
        """Create an Mt5Config from a dictionary."""
        terminal_path = data.get("terminal_path")
        return cls(
            startup_connect=bool(data["startup_connect"]),
            terminal_path=str(terminal_path) if terminal_path else None,
            default_bar_count=int(data["default_bar_count"]),
            max_bars_per_request=int(data["max_bars_per_request"]),
            require_visible_symbol=bool(data["require_visible_symbol"]),
        )


@dataclass(frozen=True)
class MarketDataConfig:
    """Represent market data feed behavior settings."""

    startup_load: bool
    default_feed_bar_count: int
    max_chart_candles: int
    auto_refresh_enabled: bool
    refresh_intervals_seconds: dict[str, int]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketDataConfig":
        """Create a MarketDataConfig from a dictionary."""
        raw_intervals = data["refresh_intervals_seconds"]
        if not isinstance(raw_intervals, dict):
            raise ValueError("market_data.refresh_intervals_seconds must be a JSON object.")
        intervals = {str(key).upper(): int(value) for key, value in raw_intervals.items()}
        if not intervals:
            raise ValueError("market_data.refresh_intervals_seconds must define at least one timeframe interval.")
        for timeframe, interval_seconds in intervals.items():
            if not timeframe:
                raise ValueError("market_data.refresh_intervals_seconds contains an empty timeframe key.")
            if interval_seconds < 1:
                raise ValueError(f"Refresh interval for {timeframe} must be at least one second.")
        return cls(
            startup_load=bool(data["startup_load"]),
            default_feed_bar_count=int(data["default_feed_bar_count"]),
            max_chart_candles=int(data["max_chart_candles"]),
            auto_refresh_enabled=bool(data["auto_refresh_enabled"]),
            refresh_intervals_seconds=intervals,
        )

    def refresh_interval_for(self, timeframe: str) -> int:
        """Return the configured refresh interval for a timeframe."""
        normalized_timeframe = str(timeframe).strip().upper()
        if normalized_timeframe in self.refresh_intervals_seconds:
            return self.refresh_intervals_seconds[normalized_timeframe]
        return self.refresh_intervals_seconds.get("DEFAULT", 5)


@dataclass(frozen=True)
class MarketStructureConfig:
    """Represent market structure engine behavior settings."""

    enabled: bool
    lookback_candles: int
    swing_window: int
    minimum_swing_distance_price: float
    max_chart_markers: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketStructureConfig":
        """Create a MarketStructureConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        swing_window = int(data["swing_window"])
        minimum_distance = float(data["minimum_swing_distance_price"])
        max_chart_markers = int(data["max_chart_markers"])
        if lookback_candles < 20:
            raise ValueError("analysis.market_structure.lookback_candles must be at least 20.")
        if swing_window < 1:
            raise ValueError("analysis.market_structure.swing_window must be at least 1.")
        if lookback_candles <= swing_window * 2:
            raise ValueError("analysis.market_structure.lookback_candles must exceed twice the swing window.")
        if minimum_distance < 0:
            raise ValueError("analysis.market_structure.minimum_swing_distance_price cannot be negative.")
        if max_chart_markers < 1:
            raise ValueError("analysis.market_structure.max_chart_markers must be greater than zero.")
        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            swing_window=swing_window,
            minimum_swing_distance_price=minimum_distance,
            max_chart_markers=max_chart_markers,
        )


@dataclass(frozen=True)
class DatabaseConfig:
    """Represent database file settings."""

    filename: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DatabaseConfig":
        """Create a DatabaseConfig from a dictionary."""
        return cls(filename=str(data["filename"]))


@dataclass(frozen=True)
class LoggingConfig:
    """Represent logging output and severity settings."""

    filename: str
    level: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoggingConfig":
        """Create a LoggingConfig from a dictionary."""
        return cls(filename=str(data["filename"]), level=str(data["level"]))


@dataclass(frozen=True)
class UiConfig:
    """Represent GUI behavior settings."""

    theme: str
    welcome_required: bool
    default_width: int
    default_height: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UiConfig":
        """Create a UiConfig from a dictionary."""
        return cls(
            theme=str(data["theme"]),
            welcome_required=bool(data["welcome_required"]),
            default_width=int(data["default_width"]),
            default_height=int(data["default_height"]),
        )


@dataclass(frozen=True)
class SentinelConfig:
    """Represent the complete Sentinel AI configuration."""

    application: ApplicationConfig
    trading: TradingConfig
    mt5: Mt5Config
    symbol_management: SymbolManagementConfig
    market_data: MarketDataConfig
    market_structure: MarketStructureConfig
    database: DatabaseConfig
    logging: LoggingConfig
    ui: UiConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentinelConfig":
        """Create a SentinelConfig from a dictionary."""
        return cls(
            application=ApplicationConfig.from_dict(data["application"]),
            trading=TradingConfig.from_dict(data["trading"]),
            mt5=Mt5Config.from_dict(data["mt5"]),
            symbol_management=SymbolManagementConfig.from_dict(data["symbol_management"]),
            market_data=MarketDataConfig.from_dict(data["market_data"]),
            market_structure=MarketStructureConfig.from_dict(data["analysis"]["market_structure"]),
            database=DatabaseConfig.from_dict(data["database"]),
            logging=LoggingConfig.from_dict(data["logging"]),
            ui=UiConfig.from_dict(data["ui"]),
        )
