"""
MODULE: CFG-001
FILE: CFG-001-001
Module Name: Configuration Schema
Version: 0.4.0
Purpose: Defines validated configuration models for Sentinel AI.
Dependencies: dataclasses, typing
Change History:
- 0.1.0: Added application, trading, database, logging, and UI configuration models.
- 0.2.0: Added MT5 connection configuration for Sprint 2.
- 0.3.0: Added market data feed configuration for Sprint 3.
- 0.4.0: Preserved schema for Sprint 4 chart rendering without adding trading settings.
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketDataConfig":
        """Create a MarketDataConfig from a dictionary."""
        return cls(
            startup_load=bool(data["startup_load"]),
            default_feed_bar_count=int(data["default_feed_bar_count"]),
            max_chart_candles=int(data["max_chart_candles"]),
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
    market_data: MarketDataConfig
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
            market_data=MarketDataConfig.from_dict(data["market_data"]),
            database=DatabaseConfig.from_dict(data["database"]),
            logging=LoggingConfig.from_dict(data["logging"]),
            ui=UiConfig.from_dict(data["ui"]),
        )
