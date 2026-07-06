"""
MODULE: SVC-002
FILE: SVC-002-001
Module Name: Application Context
Version: 0.3.0
Purpose: Composes Sentinel AI services without coupling GUI to trading or persistence internals.
Dependencies: logging, sentinel_ai.config, sentinel_ai.database, sentinel_ai.logging_service, sentinel_ai.market_data, sentinel_ai.mt5
Change History:
- 0.1.0: Added root dependency composition for Sprint 1 foundation.
- 0.2.0: Added MT5 market data service composition.
- 0.3.0: Added validated market data feed service composition.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sentinel_ai.config.config_schema import SentinelConfig
from sentinel_ai.config.config_service import ConfigService
from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.logging_service.logging_service import LoggingService
from sentinel_ai.market_data.candle_validator import CandleDataValidator
from sentinel_ai.market_data.lightweight_chart_feed import LightweightChartFeedAdapter
from sentinel_ai.market_data.market_data_feed import MarketDataFeedService
from sentinel_ai.mt5.mt5_service import MetaTrader5Service


@dataclass(frozen=True)
class ApplicationContext:
    """Store composed services for the running Sentinel AI application."""

    config: SentinelConfig
    logger: logging.Logger
    database_service: DatabaseService
    prediction_repository: PredictionRepository
    mt5_service: MetaTrader5Service
    market_data_feed_service: MarketDataFeedService


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
        market_data_feed_service = MarketDataFeedService(
            market_data_gateway=mt5_service,
            validator=CandleDataValidator(),
            chart_feed_adapter=LightweightChartFeedAdapter(),
            logger=logger,
        )
        logger.info("Application context initialized.")
        return ApplicationContext(
            config=config,
            logger=logger,
            database_service=database_service,
            prediction_repository=prediction_repository,
            mt5_service=mt5_service,
            market_data_feed_service=market_data_feed_service,
        )
