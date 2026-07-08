"""
MODULE: SVC-002
FILE: SVC-002-001
Module Name: Application Context
Version: 2.7.0
Purpose: Composes Sentinel AI services without coupling GUI to trading, symbol management, analysis, persistence, Auto Trade diagnostics, or trade lifecycle management internals.
Dependencies: logging, sentinel_ai.analysis, sentinel_ai.config, sentinel_ai.database, sentinel_ai.logging_service, sentinel_ai.market_data, sentinel_ai.mt5, sentinel_ai.symbols
Change History:
- 2.7.0: Composed TradeManagerService for Stage 8 lifecycle-service extraction.
- 2.6.0: Added Auto Trade diagnostics service composition for transparent execution gating.
- 2.5.0: Added prediction lifecycle service composition for persistence stabilization.
- 2.4.0: Preserved service composition for guarded auto-trade completion build.
- 2.3.0: Preserved service composition for completion build.
- 2.2.0: Preserved service composition for dashboard simplification and close settlement fix.
- 2.1.0: Preserved service composition for ledger maintenance tool build.
- 2.0.1: Preserved service composition for pending/backlog separation fix.
- 2.0.0: Preserved service composition for final stabilization build.
- 1.9.0.2: Preserved service composition for app helper binding hotfix.
- 1.9.0.1: Preserved service composition for MT5 resolver binding hotfix.
- 1.9.0: Preserved service composition for full stabilization audit.
- 1.8.4.1: Preserved service composition for startup binding hotfix.
- 1.8.4: Preserved service composition for lifecycle diagnostics sprint.
- 1.8.3: Preserved service composition for pending-close settlement sprint.
- 1.8.2: Preserved service composition for active-ticket close guard sprint.
- 1.8.1: Preserved service composition for trade result verification sprint.
- 1.8.0: Preserved service composition for ledger outcome persistence sprint.
- 1.7.5: Preserved service composition for persistent Sentinel trade ledger sprint.
- 1.7.4: Preserved service composition for persistent Sentinel-owned trade recovery sprint.
- 1.7.3: Preserved service composition for Sentinel-owned trade tracking sprint.
- 1.7.2: Preserved service composition for countdown removal and history fallback sprint.
- 1.7.1.3: Preserved service composition for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved service composition for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved service composition for candle countdown timer hotfix.
- 1.7.1: Preserved service composition for countdown timer and active-header priority sprint.
- 1.7.0: Preserved service composition for closed-trade lifecycle tracking sprint.
- 1.6.2: Preserved service composition for missing SL/TP warning patch.
- 1.6.1.2: Preserved service composition for missing TP chart-scale hotfix.
- 1.6.1.1: Preserved service composition for startup lock initialization hotfix.
- 1.6.1: Preserved service composition for active-trade chart lock patch.
- 1.6.0: Preserved MT5 service composition for position monitoring integration.
- 0.1.0: Added root dependency composition for Sprint 1 foundation.
- 0.2.0: Added MT5 market data service composition.
- 0.3.0: Added validated market data feed service composition.
- 0.4.0: Preserved service composition while GUI chart rendering remains isolated.
- 0.5.0: Added live market refresh service composition.
- 0.6.0: Added symbol management service composition and config service exposure.
- 0.7.0: Added market structure engine composition.
- 0.8.0: Added support/resistance engine composition.
- 0.9.0: Added liquidity engine composition.
- 0.9.1: Preserved service composition for bounded overlay segment patch.
- 0.9.2: Added imbalance engine composition for FVG and order block overlays.
- 1.0.0: Added momentum engine composition for Sprint 10 analysis foundation.
- 1.1.1: Preserved confidence engine composition for live refresh pipeline patch.
- 1.2.3: Preserved entry validation service composition for neutral-momentum setup patch.
- 1.5.1: Preserved MT5 service composition for adaptive filling-mode fallback patch.
- 1.5.0: Preserved service composition while MT5 service gained manual order placement.
- 1.4.1: Preserved service composition for polished manual review-modal patch.
- 1.4.0: Preserved service composition for trade plan overlay and manual review gate sprint.
- 1.3.3: Preserved risk reward service composition for extended TP target discovery patch.
- 1.3.2: Preserved risk reward service composition for rejected-plan display and directional TP guard patch.
- 1.3.1: Preserved risk reward service composition for smart TP target selection patch.
- 1.3.0: Added risk reward engine composition for Sprint 13 TP/SL validation.
- 1.2.2: Preserved entry validation service composition for pullback-aware setup patch.
- 1.2.1: Preserved entry validation service composition for setup alignment patch.
- 1.2.0: Added entry validation engine composition for Sprint 12 setup validation.
- 1.1.0: Added confidence engine composition for Sprint 11 context scoring foundation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sentinel_ai.analysis.confidence_engine import ConfidenceEngine
from sentinel_ai.analysis.entry_validation_engine import EntryValidationEngine
from sentinel_ai.analysis.imbalance_engine import ImbalanceEngine
from sentinel_ai.analysis.liquidity_engine import LiquidityEngine
from sentinel_ai.analysis.momentum_engine import MomentumEngine
from sentinel_ai.analysis.risk_reward_engine import RiskRewardEngine
from sentinel_ai.analysis.market_structure_engine import MarketStructureEngine
from sentinel_ai.analysis.support_resistance_engine import SupportResistanceEngine
from sentinel_ai.config.config_schema import SentinelConfig
from sentinel_ai.config.config_service import ConfigService
from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.logging_service.logging_service import LoggingService
from sentinel_ai.market_data.candle_validator import CandleDataValidator
from sentinel_ai.market_data.lightweight_chart_feed import LightweightChartFeedAdapter
from sentinel_ai.market_data.market_data_feed import MarketDataFeedService
from sentinel_ai.market_data.market_refresh_service import MarketRefreshService
from sentinel_ai.mt5.mt5_service import MetaTrader5Service
from sentinel_ai.services.prediction_lifecycle_service import PredictionLifecycleService
from sentinel_ai.services.auto_trade_diagnostics_service import AutoTradeDiagnosticsService
from sentinel_ai.services.trade_manager_service import TradeManagerService
from sentinel_ai.symbols.symbol_management_service import SymbolManagementService


@dataclass(frozen=True)
class ApplicationContext:
    """Store composed services for the running Sentinel AI application."""

    config: SentinelConfig
    config_service: ConfigService
    logger: logging.Logger
    database_service: DatabaseService
    prediction_repository: PredictionRepository
    prediction_lifecycle_service: PredictionLifecycleService
    auto_trade_diagnostics_service: AutoTradeDiagnosticsService
    trade_manager_service: TradeManagerService
    mt5_service: MetaTrader5Service
    symbol_service: SymbolManagementService
    market_data_feed_service: MarketDataFeedService
    market_refresh_service: MarketRefreshService
    market_structure_engine: MarketStructureEngine
    support_resistance_engine: SupportResistanceEngine
    liquidity_engine: LiquidityEngine
    imbalance_engine: ImbalanceEngine
    momentum_engine: MomentumEngine
    confidence_engine: ConfidenceEngine
    entry_validation_engine: EntryValidationEngine
    risk_reward_engine: RiskRewardEngine


class ApplicationContextFactory:
    """Build the application context from production services."""

    def build(self) -> ApplicationContext:
        """Create, initialize, and return the application context."""
        config_service = ConfigService()
        config = config_service.load()
        logger = LoggingService(config.logging).configure()
        database_service = DatabaseService(config.database)
        database_service.initialize()
        prediction_repository = PredictionRepository(database_service)
        prediction_lifecycle_service = PredictionLifecycleService(
            repository=prediction_repository,
            engine_version=config.application.version,
            logger=logger,
        )
        auto_trade_diagnostics_service = AutoTradeDiagnosticsService()
        mt5_service = MetaTrader5Service(config.mt5, logger)
        trade_manager_service = TradeManagerService(
            mt5_service=mt5_service,
            manual_config=config.manual_trading,
            prediction_lifecycle_service=prediction_lifecycle_service,
            logger=logger,
        )
        symbol_service = SymbolManagementService(
            market_data_gateway=mt5_service,
            config_service=config_service,
            logger=logger,
        )
        market_data_feed_service = MarketDataFeedService(
            market_data_gateway=mt5_service,
            validator=CandleDataValidator(),
            chart_feed_adapter=LightweightChartFeedAdapter(),
            logger=logger,
        )
        market_refresh_service = MarketRefreshService(
            market_data_feed_service=market_data_feed_service,
            logger=logger,
        )
        market_structure_engine = MarketStructureEngine(
            config=config.market_structure,
            logger=logger,
        )
        support_resistance_engine = SupportResistanceEngine(
            config=config.support_resistance,
            logger=logger,
        )
        liquidity_engine = LiquidityEngine(
            config=config.liquidity,
            logger=logger,
        )
        imbalance_engine = ImbalanceEngine(
            config=config.imbalance,
            logger=logger,
        )
        momentum_engine = MomentumEngine(
            config=config.momentum,
            logger=logger,
        )
        confidence_engine = ConfidenceEngine(
            config=config.confidence,
            logger=logger,
        )
        entry_validation_engine = EntryValidationEngine(
            config=config.entry_validation,
            logger=logger,
        )
        risk_reward_engine = RiskRewardEngine(
            config=config.risk_reward,
            logger=logger,
        )
        logger.info("Application context initialized.")
        return ApplicationContext(
            config=config,
            config_service=config_service,
            logger=logger,
            database_service=database_service,
            prediction_repository=prediction_repository,
            prediction_lifecycle_service=prediction_lifecycle_service,
            auto_trade_diagnostics_service=auto_trade_diagnostics_service,
            trade_manager_service=trade_manager_service,
            mt5_service=mt5_service,
            symbol_service=symbol_service,
            market_data_feed_service=market_data_feed_service,
            market_refresh_service=market_refresh_service,
            market_structure_engine=market_structure_engine,
            support_resistance_engine=support_resistance_engine,
            liquidity_engine=liquidity_engine,
            imbalance_engine=imbalance_engine,
            momentum_engine=momentum_engine,
            confidence_engine=confidence_engine,
            entry_validation_engine=entry_validation_engine,
            risk_reward_engine=risk_reward_engine,
        )
