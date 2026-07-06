"""
MODULE: CFG-001
FILE: CFG-001-002
Module Name: Configuration Service
Version: 0.1.0
Purpose: Loads, persists, and validates JSON configuration for Sentinel AI.
Dependencies: json, pathlib, shutil, sentinel_ai.config.config_schema, sentinel_ai.core.constants, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added production configuration loading from packaged defaults into writable user config.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from sentinel_ai.config.config_schema import SentinelConfig
from sentinel_ai.core.constants import DEFAULT_CONFIG_RESOURCE
from sentinel_ai.utils.paths import config_dir, resource_path


class ConfigService:
    """Provide validated application configuration from JSON storage."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the service with an optional explicit configuration path."""
        self._config_path = config_path or config_dir() / "config.json"

    @property
    def config_path(self) -> Path:
        """Return the active writable configuration file path."""
        return self._config_path

    def load(self) -> SentinelConfig:
        """Load and validate the current Sentinel AI configuration."""
        self._ensure_config_file_exists()
        payload = self._read_json(self._config_path)
        return SentinelConfig.from_dict(payload)

    def _ensure_config_file_exists(self) -> None:
        """Create the writable configuration file from packaged defaults when absent."""
        if self._config_path.exists():
            return
        default_path = resource_path(DEFAULT_CONFIG_RESOURCE)
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(default_path, self._config_path)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        """Read a JSON object from disk and validate the top-level structure."""
        with path.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not isinstance(data, dict):
            raise ValueError(f"Configuration file must contain a JSON object: {path}")
        return data
