"""
MODULE: UTIL-001
FILE: UTIL-001-001
Module Name: Path Utilities
Version: 0.1.0
Purpose: Provides PyInstaller-compatible filesystem path resolution.
Dependencies: pathlib, sys
Change History:
- 0.1.0: Added runtime, resource, data, config, and log path helpers.
"""

from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    """Return the runtime root for source execution or PyInstaller bundles."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: str) -> Path:
    """Return an absolute path for a packaged application resource."""
    return application_root() / "sentinel_ai" / "resources" / relative_path


def user_data_dir() -> Path:
    """Return the writable user data directory for Sentinel AI."""
    if sys.platform.startswith("win"):
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".local" / "share"
    path = base / "SentinelAI"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_dir() -> Path:
    """Return the writable configuration directory."""
    path = user_data_dir() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_dir() -> Path:
    """Return the writable log directory."""
    path = user_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_dir() -> Path:
    """Return the writable database directory."""
    path = user_data_dir() / "database"
    path.mkdir(parents=True, exist_ok=True)
    return path
