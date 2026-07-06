"""
MODULE: CFG-001
FILE: CFG-001-002
Module Name: Configuration Service
Version: 0.6.0
Purpose: Loads, persists, and validates JSON configuration for Sentinel AI.
Dependencies: copy, json, pathlib, shutil, sentinel_ai.config.config_schema, sentinel_ai.core.constants, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added production configuration loading from packaged defaults into writable user config.
- 0.2.0: Added backward-compatible configuration merge so Sprint 1 user configs receive Sprint 2 MT5 keys safely.
- 0.3.0: Preserved backward-compatible configuration merge for Sprint 3 market_data keys.
- 0.4.0: Preserved configuration merge behavior for Sprint 4 chart resources.
- 0.5.1: Added targeted configuration migration for one-second refresh defaults.
- 0.6.0: Added active trading-symbol persistence for symbol management.
"""

from __future__ import annotations

import copy
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
        default_payload = self._read_json(resource_path(DEFAULT_CONFIG_RESOURCE))
        user_payload = self._read_json(self._config_path)
        merged_payload = self._merge_missing_values(default_payload, user_payload)
        migrated_payload = self._apply_versioned_migrations(default_payload, merged_payload)
        if migrated_payload != user_payload:
            self._write_json(self._config_path, migrated_payload)
        return SentinelConfig.from_dict(migrated_payload)


    def update_trading_symbol(self, symbol: str) -> None:
        """Persist the selected trading symbol without resetting unrelated user settings."""
        clean_symbol = str(symbol).strip()
        if not clean_symbol:
            raise ValueError("Trading symbol cannot be empty.")
        self._ensure_config_file_exists()
        payload = self._read_json(self._config_path)
        trading_payload = payload.setdefault("trading", {})
        trading_payload["symbol"] = clean_symbol
        self._write_json(self._config_path, payload)

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

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        """Write a JSON configuration object to disk using deterministic formatting."""
        with path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=2, ensure_ascii=False)
            file_handle.write("\n")

    @classmethod
    def _apply_versioned_migrations(cls, defaults: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        """Apply narrow, version-aware configuration migrations without resetting unrelated user settings."""
        migrated = copy.deepcopy(current)
        current_version = str(migrated.get("application", {}).get("version", "0.0.0"))
        target_version = str(defaults.get("application", {}).get("version", current_version))

        if cls._is_version_older(current_version, "0.5.1"):
            default_intervals = defaults.get("market_data", {}).get("refresh_intervals_seconds", {})
            if isinstance(default_intervals, dict):
                market_data = migrated.setdefault("market_data", {})
                market_data["refresh_intervals_seconds"] = copy.deepcopy(default_intervals)

        application = migrated.setdefault("application", {})
        application["version"] = target_version
        return migrated

    @staticmethod
    def _is_version_older(current_version: str, target_version: str) -> bool:
        """Return True when current_version is numerically lower than target_version."""
        return ConfigService._version_tuple(current_version) < ConfigService._version_tuple(target_version)

    @staticmethod
    def _version_tuple(version: str) -> tuple[int, int, int]:
        """Convert a semantic version string into a comparable three-part integer tuple."""
        parts = str(version).strip().split(".")
        numeric_parts: list[int] = []
        for index in range(3):
            if index >= len(parts):
                numeric_parts.append(0)
                continue
            raw_part = "".join(character for character in parts[index] if character.isdigit())
            numeric_parts.append(int(raw_part or 0))
        return (numeric_parts[0], numeric_parts[1], numeric_parts[2])

    @classmethod
    def _merge_missing_values(cls, defaults: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        """Return current config with missing keys filled from packaged defaults."""
        merged = dict(current)
        for key, default_value in defaults.items():
            if key not in merged:
                merged[key] = default_value
                continue
            current_value = merged[key]
            if isinstance(default_value, dict) and isinstance(current_value, dict):
                merged[key] = cls._merge_missing_values(default_value, current_value)
        return merged
