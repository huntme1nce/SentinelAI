"""
MODULE: SVC-002
FILE: SVC-002-001
Module Name: Application Context
Version: 0.7.0
Purpose: Composes Sentinel AI services without coupling GUI to trading, symbol management, analysis, or persistence internals.
Dependencies: logging, sentinel_ai.analysis, sentinel_ai.config, sentinel_ai.database, sentinel_ai.logging_service, sentinel_ai.market_data, sentinel_ai.mt5, sentinel_ai.symbols
Change History:
- 0.1.0: Added root dependency composition for Sprint 1 foundation.
- 0.2.0: Added MT5 market data service composition.
- 0.3.0: Added validated market data feed service composition.
- 0.4.0: Preserved service composition while GUI chart rendering remains isolated.
- 0.5.0: Added live market refresh service composition.
- 0.6.0: Added symbol management service composition and config service exposure.
- 0.7.0: Added market structure engine composition.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sentinel_ai.analysis.market_structure_engine import MarketStructureEngine
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
from sentinel_ai.symbols.symbol_management_service import SymbolManagementService


@dataclass(frozen=True)
class ApplicationContext:
    """Store composed services for the running Sentinel AI application."""

    config: SentinelConfig
    config_service: ConfigService
    logger: logging.Logger
    database_service: DatabaseService
    prediction_repository: PredictionRepository
    mt5_service: MetaTrader5Service
    symbol_service: SymbolManagementService
    market_data_feed_service: MarketDataFeedService
    market_refresh_service: MarketRefreshService
    market_structure_engine: MarketStructureEngine


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
        mt5_service = MetaTrader5Service(config.mt5, logger)
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
        logger.info("Application context initialized.")
        return ApplicationContext(
            config=config,
            config_service=config_service,
            logger=logger,
            database_service=database_service,
            prediction_repository=prediction_repository,
            mt5_service=mt5_service,
            symbol_service=symbol_service,
            market_data_feed_service=market_data_feed_service,
            market_refresh_service=market_refresh_service,
            market_structure_engine=market_structure_engine,
        )
