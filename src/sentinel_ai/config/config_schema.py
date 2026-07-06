"""
MODULE: CFG-001
FILE: CFG-001-001
Module Name: Configuration Schema
Version: 0.1.0
Purpose: Defines validated configuration models for Sentinel AI.
Dependencies: dataclasses, typing
Change History:
- 0.1.0: Added application, trading, database, logging, and UI configuration models.
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
    database: DatabaseConfig
    logging: LoggingConfig
    ui: UiConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentinelConfig":
        """Create a SentinelConfig from a dictionary."""
        return cls(
            application=ApplicationConfig.from_dict(data["application"]),
            trading=TradingConfig.from_dict(data["trading"]),
            database=DatabaseConfig.from_dict(data["database"]),
            logging=LoggingConfig.from_dict(data["logging"]),
            ui=UiConfig.from_dict(data["ui"]),
        )
