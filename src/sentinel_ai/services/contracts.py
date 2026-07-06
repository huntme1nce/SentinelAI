"""
MODULE: SVC-001
FILE: SVC-001-001
Module Name: Service Contracts
Version: 0.5.0
Purpose: Defines replaceable service interfaces for analysis, market data, prediction, trading, learning, and notifications.
Dependencies: abc, pandas, sentinel_ai.models.market, sentinel_ai.models.prediction
Change History:
- 0.1.0: Added runtime service contracts for modular expansion.
- 0.2.0: Added market data service contract for MT5 connection foundation.
- 0.3.0: Added candle feed contract for validated market data snapshots.
- 0.4.0: Preserved service contracts for chart rendering sprint without adding trading execution.
- 0.5.0: Added market refresh service contract for live feed updates.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from sentinel_ai.models.market import (
    MarketDataSnapshot,
    Mt5AccountSnapshot,
    Mt5ConnectionStatus,
    SymbolValidationResult,
)
from sentinel_ai.models.prediction import PredictionRecord


class MarketDataServiceContract(ABC):
    """Define the contract for read-only market data gateways."""

    @abstractmethod
    def connect(self) -> Mt5ConnectionStatus:
        """Connect to a market data source and return connection status."""
        raise NotImplementedError("MarketDataServiceContract.connect must be implemented by a market data adapter.")

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the active market data source."""
        raise NotImplementedError("MarketDataServiceContract.disconnect must be implemented by a market data adapter.")

    @abstractmethod
    def connection_status(self) -> Mt5ConnectionStatus:
        """Return the latest known market data connection status."""
        raise NotImplementedError("MarketDataServiceContract.connection_status must be implemented by a market data adapter.")

    @abstractmethod
    def account_snapshot(self) -> Mt5AccountSnapshot | None:
        """Return account details when available from the market data source."""
        raise NotImplementedError("MarketDataServiceContract.account_snapshot must be implemented by a market data adapter.")

    @abstractmethod
    def validate_symbol(self, symbol: str) -> SymbolValidationResult:
        """Validate whether a symbol is available and usable."""
        raise NotImplementedError("MarketDataServiceContract.validate_symbol must be implemented by a market data adapter.")

    @abstractmethod
    def fetch_ohlc(self, symbol: str, timeframe: str, bar_count: int | None = None) -> pd.DataFrame:
        """Fetch normalized OHLCV market data."""
        raise NotImplementedError("MarketDataServiceContract.fetch_ohlc must be implemented by a market data adapter.")


class CandleFeedServiceContract(ABC):
    """Define the contract for validated candle feed services."""

    @abstractmethod
    def load_snapshot(self, symbol: str, timeframe: str, bar_count: int) -> MarketDataSnapshot:
        """Load and return one validated market data snapshot."""
        raise NotImplementedError("CandleFeedServiceContract.load_snapshot must be implemented by a feed service.")

    @abstractmethod
    def latest_snapshot(self) -> MarketDataSnapshot | None:
        """Return the latest validated market data snapshot when available."""
        raise NotImplementedError("CandleFeedServiceContract.latest_snapshot must be implemented by a feed service.")

    @abstractmethod
    def chart_payload(self) -> list[dict[str, float | int]]:
        """Return a JSON-serializable chart payload for the latest snapshot."""
        raise NotImplementedError("CandleFeedServiceContract.chart_payload must be implemented by a feed service.")


class MarketRefreshServiceContract(ABC):
    """Define the contract for timed market data refresh services."""

    @abstractmethod
    def start(self, symbol: str, timeframe: str, bar_count: int, interval_seconds: int) -> None:
        """Start timed refresh for a symbol and timeframe."""
        raise NotImplementedError("MarketRefreshServiceContract.start must be implemented by a refresh service.")

    @abstractmethod
    def stop(self) -> None:
        """Stop timed market refresh."""
        raise NotImplementedError("MarketRefreshServiceContract.stop must be implemented by a refresh service.")

    @abstractmethod
    def refresh_once(self) -> None:
        """Run one market refresh cycle."""
        raise NotImplementedError("MarketRefreshServiceContract.refresh_once must be implemented by a refresh service.")


class AnalysisPipelineContract(ABC):
    """Define the contract for market analysis pipelines."""

    @abstractmethod
    def analyze(self, symbol: str, timeframe: str) -> PredictionRecord:
        """Analyze market data and return a persisted-ready prediction record."""
        raise NotImplementedError("AnalysisPipelineContract.analyze must be implemented by an engine.")


class TradingServiceContract(ABC):
    """Define the contract for manual and automated trade execution services."""

    @abstractmethod
    def place_manual_trade(self, prediction: PredictionRecord) -> str:
        """Place one manual trade based on a validated prediction."""
        raise NotImplementedError("TradingServiceContract.place_manual_trade must be implemented by a trading adapter.")

    @abstractmethod
    def enable_auto_trade(self) -> None:
        """Enable automatic trade execution mode."""
        raise NotImplementedError("TradingServiceContract.enable_auto_trade must be implemented by a trading adapter.")

    @abstractmethod
    def disable_auto_trade(self) -> None:
        """Disable automatic trade execution mode."""
        raise NotImplementedError("TradingServiceContract.disable_auto_trade must be implemented by a trading adapter.")


class LearningServiceContract(ABC):
    """Define the contract for statistical learning review services."""

    @abstractmethod
    def review_closed_predictions(self, minimum_sample_size: int) -> list[str]:
        """Review closed predictions and return applied learning adjustment UIDs."""
        raise NotImplementedError("LearningServiceContract.review_closed_predictions must be implemented by a learning engine.")


class NotificationServiceContract(ABC):
    """Define the contract for user-facing notifications."""

    @abstractmethod
    def publish_status(self, message: str) -> None:
        """Publish a status message without coupling services to GUI widgets."""
        raise NotImplementedError("NotificationServiceContract.publish_status must be implemented by a notification service.")
