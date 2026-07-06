"""
MODULE: SVC-002
FILE: SVC-002-001
Module Name: Application Context
Version: 0.1.0
Purpose: Composes Sentinel AI services without coupling GUI to trading or persistence internals.
Dependencies: logging, sentinel_ai.config, sentinel_ai.database, sentinel_ai.logging_service
Change History:
- 0.1.0: Added root dependency composition for Sprint 1 foundation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sentinel_ai.config.config_schema import SentinelConfig
from sentinel_ai.config.config_service import ConfigService
from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.logging_service.logging_service import LoggingService


@dataclass(frozen=True)
class ApplicationContext:
    """Store composed services for the running Sentinel AI application."""

    config: SentinelConfig
    logger: logging.Logger
    database_service: DatabaseService
    prediction_repository: PredictionRepository


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
        logger.info("Application context initialized.")
        return ApplicationContext(
            config=config,
            logger=logger,
            database_service=database_service,
            prediction_repository=prediction_repository,
        )
