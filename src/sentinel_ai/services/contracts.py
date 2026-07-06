"""
MODULE: SVC-001
FILE: SVC-001-001
Module Name: Service Contracts
Version: 0.1.0
Purpose: Defines replaceable service interfaces for analysis, prediction, trading, learning, and notifications.
Dependencies: abc, sentinel_ai.models.prediction
Change History:
- 0.1.0: Added runtime service contracts for modular expansion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from sentinel_ai.models.prediction import PredictionRecord


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
