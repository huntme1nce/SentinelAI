"""
MODULE: DB-001
FILE: DB-001-002
Module Name: Database Service
Version: 0.1.0
Purpose: Manages SQLite connections and schema initialization for Sentinel AI.
Dependencies: contextlib, pathlib, sqlite3, sentinel_ai.config.config_schema, sentinel_ai.database.schema, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added SQLite connection lifecycle and schema bootstrapping.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sentinel_ai.config.config_schema import DatabaseConfig
from sentinel_ai.database.schema import SCHEMA_STATEMENTS, SCHEMA_VERSION
from sentinel_ai.utils.paths import database_dir


class DatabaseService:
    """Provide SQLite initialization and managed connection access."""

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize the database service using validated database configuration."""
        self._database_path = database_dir() / config.filename

    @property
    def database_path(self) -> Path:
        """Return the active SQLite database file path."""
        return self._database_path

    def initialize(self) -> None:
        """Create required database objects and stamp the active schema version."""
        with self.connection() as connection:
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.execute(
                """
                INSERT INTO app_metadata(key, value, updated_at)
                VALUES('schema_version', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
                """,
                (SCHEMA_VERSION,),
            )
            connection.commit()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured SQLite connection and ensure it closes safely."""
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
        finally:
            connection.close()
