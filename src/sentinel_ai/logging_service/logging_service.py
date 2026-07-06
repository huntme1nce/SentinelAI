"""
MODULE: LOG-001
FILE: LOG-001-001
Module Name: Logging Service
Version: 0.1.0
Purpose: Configures application logging for file and console diagnostics.
Dependencies: logging, pathlib, sentinel_ai.config.config_schema, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added centralized logger setup with Windows-writable log storage.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sentinel_ai.config.config_schema import LoggingConfig
from sentinel_ai.utils.paths import log_dir


class LoggingService:
    """Create and configure Sentinel AI loggers."""

    def __init__(self, config: LoggingConfig) -> None:
        """Initialize the logging service from validated logging configuration."""
        self._config = config
        self._log_path = log_dir() / self._config.filename

    @property
    def log_path(self) -> Path:
        """Return the active log file path."""
        return self._log_path

    def configure(self) -> logging.Logger:
        """Configure root logging and return the Sentinel AI application logger."""
        level = getattr(logging, self._config.level.upper(), logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.handlers.clear()

        file_handler = logging.FileHandler(self._log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        logger = logging.getLogger("sentinel_ai")
        logger.info("Logging initialized at %s", self._log_path)
        return logger
