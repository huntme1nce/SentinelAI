"""
MODULE: SVC-001
FILE: SVC-001-001
Module Name: Service Contracts
1.5.1
Purpose: Defines replaceable service interfaces for analysis, market data, symbol management, prediction, trading, learning, and notifications.
Dependencies: abc, pandas, sentinel_ai.models.liquidity, sentinel_ai.models.market, sentinel_ai.models.market_structure, sentinel_ai.models.prediction
Change History:
- 2.4.0: Preserved trade service contracts for guarded auto-trade completion build.
- 2.3.0: Preserved close resolver contract for pending history repair.
- 2.2.0: Preserved close resolver contract for improved TP close settlement.
- 2.1.0: Preserved close resolver contract for ledger maintenance tool build.
- 2.0.1: Preserved close resolver contract for pending/backlog separation fix.
- 2.0.0: Preserved close resolver contract parameters for final stabilization build.
- 1.9.0.2: Preserved close resolver contract parameters for app helper binding hotfix.
- 1.9.0.1: Preserved close resolver contract parameters for MT5 resolver binding hotfix.
- 1.9.0: Added close resolver parameters to Sentinel statistics contract.
- 1.8.4.1: Preserved Sentinel statistics contract for startup binding hotfix.
- 1.8.4: Preserved Sentinel statistics contract for lifecycle diagnostics sprint.
- 1.8.3: Preserved Sentinel statistics contract for pending-close settlement sprint.
- 1.8.2: Preserved multi-ticket Sentinel statistics contract for active-ticket close guard.
- 1.8.1: Preserved multi-ticket Sentinel statistics contract for result verification dashboard.
- 1.8.0: Preserved multi-ticket statistics contract for ledger outcome persistence.
- 1.7.5: Added multi-ticket Sentinel ledger statistics contract parameter.
- 1.7.4: Added Sentinel comment recovery parameter to trade statistics contract.
- 1.7.3: Extended trade statistics contract for Sentinel-owned ticket-only matching.
- 1.7.2: Preserved service contracts for countdown removal and history fallback sprint.
- 1.7.1.3: Preserved service contracts for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved service contracts for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved service contracts for candle countdown timer hotfix.
- 1.7.1: Preserved service contracts for countdown timer and active-header priority sprint.
- 1.7.0: Preserved monitoring contracts for closed-trade lifecycle tracking sprint.
- 1.6.2: Preserved monitoring contracts for missing SL/TP warning patch.
- 1.6.1.2: Preserved monitoring contracts for missing TP chart-scale hotfix.
- 1.6.1.1: Preserved contracts for startup lock initialization hotfix.
- 1.6.1: Preserved monitoring contracts for active-trade chart lock patch.
- 0.1.0: Added runtime service contracts for modular expansion.
- 0.2.0: Added market data service contract for MT5 connection foundation.
- 0.3.0: Added candle feed contract for validated market data snapshots.
- 0.4.0: Preserved service contracts for chart rendering sprint without adding trading execution.
- 0.5.0: Added market refresh service contract for live feed updates.
- 0.6.0: Added symbol catalog and search methods to the market data service contract.
- 0.7.0: Added market structure engine contract for replaceable analysis modules.
- 0.8.0: Added support/resistance engine contract for replaceable analysis modules.
- 0.9.0: Added liquidity engine contract for replaceable analysis modules.
- 0.9.1: Preserved analysis service contracts for bounded overlay segment patch.
- 0.9.2: Added imbalance engine contract for FVG and order block analysis modules.
- 1.0.0: Added momentum engine contract for Sprint 10 analysis modules.
- 1.1.1: Preserved confidence contract for live refresh pipeline patch.
- 1.2.3: Preserved entry validation contract for neutral-momentum setup patch.
- 1.4.1: Preserved service contracts for polished manual review-modal patch.
- 1.6.0: Added position monitoring and daily trade statistics contracts.
- 1.5.1: Preserved manual trade contract for adaptive filling-mode fallback patch.
- 1.5.0: Added manual trade order placement contract for MT5 execution.
- 1.4.0: Preserved contracts for trade plan overlay and manual review gate sprint.
- 1.3.3: Preserved risk reward contract for extended TP target discovery patch.
- 1.3.2: Preserved risk reward contract for rejected-plan display and directional TP guard patch.
- 1.3.1: Preserved risk reward contract for smart TP target selection patch.
- 1.3.0: Added risk reward engine contract for TP/SL validation modules.
- 1.2.2: Preserved entry validation contract for pullback-aware setup patch.
- 1.2.1: Preserved entry validation contract for setup alignment patch.
- 1.2.0: Added entry validation engine contract for Sprint 12 setup validation.
- 1.1.0: Added confidence engine contract for Sprint 11 scoring modules.
"""

from __future__ import annotations

from datetime import datetime
from abc import ABC, abstractmethod

import pandas as pd

from sentinel_ai.models.confidence import ConfidenceSnapshot
from sentinel_ai.models.entry_validation import EntryValidationSnapshot
from sentinel_ai.models.imbalance import ImbalanceSnapshot
from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.momentum import MomentumSnapshot
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.market import (
    MarketDataSnapshot,
    Mt5AccountSnapshot,
    Mt5ConnectionStatus,
    SymbolValidationResult,
)
from sentinel_ai.models.symbol import SymbolCatalogItem
from sentinel_ai.models.trade_execution import ManualTradeOrderRequest, ManualTradeOrderResult
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot
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
    def list_symbols(self) -> tuple[SymbolCatalogItem, ...]:
        """Return all symbols available from the active market data source."""
        raise NotImplementedError("MarketDataServiceContract.list_symbols must be implemented by a market data adapter.")

    @abstractmethod
    def search_symbols(self, query: str, limit: int) -> tuple[SymbolCatalogItem, ...]:
        """Return ranked symbols matching a user or configuration query."""
        raise NotImplementedError("MarketDataServiceContract.search_symbols must be implemented by a market data adapter.")

    @abstractmethod
    def fetch_ohlc(self, symbol: str, timeframe: str, bar_count: int | None = None) -> pd.DataFrame:
        """Fetch normalized OHLCV market data."""
        raise NotImplementedError("MarketDataServiceContract.fetch_ohlc must be implemented by a market data adapter.")


    @abstractmethod
    def place_manual_market_order(
        self,
        request: ManualTradeOrderRequest,
        one_position_per_symbol: bool,
    ) -> ManualTradeOrderResult:
        """Place one user-confirmed manual market order."""
        raise NotImplementedError("MarketDataServiceContract.place_manual_market_order must be implemented by a trading adapter.")


    @abstractmethod
    def monitor_symbol_position(self, symbol: str, magic_number: int | None = None) -> PositionMonitorSnapshot:
        """Return current open-position monitoring data for one symbol."""
        raise NotImplementedError("MarketDataServiceContract.monitor_symbol_position must be implemented by a trading adapter.")

    @abstractmethod
    def daily_trade_statistics(
        self,
        symbol: str,
        magic_number: int | None = None,
        owned_position_ticket: int | None = None,
        owned_position_tickets: tuple[int, ...] | None = None,
        sentinel_owned_only: bool = True,
        sentinel_comment: str | None = None,
        owned_trade_opened_at: datetime | None = None,
        settlement_search_hours: int = 168,
    ) -> DailyTradeStatisticsSnapshot:
        """Return closed-trade statistics, restricted to Sentinel-owned tickets by default."""
        raise NotImplementedError("MarketDataServiceContract.daily_trade_statistics must be implemented by a trading adapter.")


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


class MarketStructureEngineContract(ABC):
    """Define the contract for replaceable market structure engines."""

    @abstractmethod
    def analyze(self, market_snapshot: MarketDataSnapshot) -> MarketStructureSnapshot:
        """Analyze a validated market snapshot and return structure context."""
        raise NotImplementedError("MarketStructureEngineContract.analyze must be implemented by an analysis engine.")


class SupportResistanceEngineContract(ABC):
    """Define the contract for replaceable support/resistance engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
    ) -> SupportResistanceSnapshot:
        """Analyze validated market and structure snapshots and return support/resistance context."""
        raise NotImplementedError("SupportResistanceEngineContract.analyze must be implemented by an analysis engine.")


class LiquidityEngineContract(ABC):
    """Define the contract for replaceable liquidity analysis engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
    ) -> LiquiditySnapshot:
        """Analyze liquidity pools and sweeps without generating trade predictions."""
        raise NotImplementedError("LiquidityEngineContract.analyze must be implemented by a liquidity engine.")


class ImbalanceEngineContract(ABC):
    """Define the contract for replaceable imbalance analysis engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
    ) -> ImbalanceSnapshot:
        """Analyze fair value gaps and order blocks without generating trade predictions."""
        raise NotImplementedError("ImbalanceEngineContract.analyze must be implemented by an imbalance engine.")


class MomentumEngineContract(ABC):
    """Define the contract for replaceable momentum analysis engines."""

    @abstractmethod
    def analyze(self, market_snapshot: MarketDataSnapshot) -> MomentumSnapshot:
        """Analyze EMA, MACD, stochastic, and candle momentum without generating trade predictions."""
        raise NotImplementedError("MomentumEngineContract.analyze must be implemented by a momentum engine.")


class ConfidenceEngineContract(ABC):
    """Define the contract for replaceable confidence scoring engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: object | None,
        liquidity_snapshot: object | None,
        imbalance_snapshot: object | None,
        momentum_snapshot: object | None,
    ) -> ConfidenceSnapshot:
        """Score context confidence without generating trade predictions."""
        raise NotImplementedError("ConfidenceEngineContract.analyze must be implemented by a confidence engine.")


class EntryValidationEngineContract(ABC):
    """Define the contract for replaceable setup-only entry validation engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: object | None,
        liquidity_snapshot: object | None,
        imbalance_snapshot: object | None,
        momentum_snapshot: object | None,
        confidence_snapshot: ConfidenceSnapshot | None,
    ) -> EntryValidationSnapshot:
        """Validate setup-level entry context without creating executable trade signals."""
        raise NotImplementedError("EntryValidationEngineContract.analyze must be implemented by an entry validation engine.")


class RiskRewardEngineContract(ABC):
    """Define the contract for replaceable TP/SL and risk/reward validation engines."""

    @abstractmethod
    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_snapshot: EntryValidationSnapshot | None,
        support_resistance_snapshot: object | None,
        liquidity_snapshot: object | None,
        imbalance_snapshot: object | None,
    ) -> RiskRewardSnapshot:
        """Validate TP/SL and risk/reward without creating executable trade orders."""
        raise NotImplementedError("RiskRewardEngineContract.analyze must be implemented by a risk reward engine.")


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
