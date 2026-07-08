"""
MODULE: DB-001
FILE: DB-001-001
Module Name: Database Schema
Version: 0.2.0
Purpose: Defines the permanent SQLite schema for Sentinel AI prediction storage, statistics foundations, and learning-readiness reviews.
Dependencies: None
Change History:
- 0.2.0: Added learning_reviews table for Stage 9 statistical readiness snapshots.
- 0.1.0: Added prediction, learning adjustment, and application metadata tables.
"""

SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS app_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_uid TEXT NOT NULL UNIQUE,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        direction TEXT NOT NULL CHECK(direction IN ('BUY', 'SELL', 'WAIT')),
        confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 100),
        reason TEXT NOT NULL,
        entry_price REAL,
        stop_loss REAL,
        take_profit REAL,
        risk_reward REAL,
        status TEXT NOT NULL CHECK(status IN ('PREDICTION', 'VALIDATED', 'WAITING', 'ENTRY_TRIGGERED', 'TRADE_ACTIVE', 'MONITORING', 'CLOSED', 'INVALIDATED', 'CANCELLED')),
        outcome TEXT CHECK(outcome IN ('WIN', 'LOSS', 'BREAKEVEN', 'CANCELLED', 'INVALIDATED')),
        tp_hit INTEGER NOT NULL DEFAULT 0 CHECK(tp_hit IN (0, 1)),
        sl_hit INTEGER NOT NULL DEFAULT 0 CHECK(sl_hit IN (0, 1)),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        closed_at TEXT,
        duration_seconds INTEGER,
        engine_version TEXT NOT NULL,
        metadata_json TEXT NOT NULL DEFAULT '{}'
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_predictions_symbol_timeframe
    ON predictions(symbol, timeframe)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_predictions_created_at
    ON predictions(created_at)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_predictions_status
    ON predictions(status)
    """,

    """
    CREATE TABLE IF NOT EXISTS learning_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_uid TEXT NOT NULL UNIQUE,
        generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        action TEXT NOT NULL,
        sample_size INTEGER NOT NULL DEFAULT 0,
        minimum_sample_size INTEGER NOT NULL DEFAULT 0,
        wins INTEGER NOT NULL DEFAULT 0,
        losses INTEGER NOT NULL DEFAULT 0,
        breakeven INTEGER NOT NULL DEFAULT 0,
        win_rate REAL NOT NULL DEFAULT 0,
        loss_rate REAL NOT NULL DEFAULT 0,
        average_confidence REAL NOT NULL DEFAULT 0,
        average_risk_reward REAL NOT NULL DEFAULT 0,
        review_window_days INTEGER NOT NULL DEFAULT 0,
        ready_for_parameter_review INTEGER NOT NULL DEFAULT 0 CHECK(ready_for_parameter_review IN (0, 1)),
        top_failure_pattern_json TEXT NOT NULL DEFAULT '{}',
        metadata_json TEXT NOT NULL DEFAULT '{}'
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_learning_reviews_generated_at
    ON learning_reviews(generated_at)
    """,
    """
    CREATE TABLE IF NOT EXISTS learning_adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adjustment_uid TEXT NOT NULL UNIQUE,
        parameter_name TEXT NOT NULL,
        previous_value TEXT NOT NULL,
        new_value TEXT NOT NULL,
        sample_size INTEGER NOT NULL CHECK(sample_size > 0),
        evidence_summary TEXT NOT NULL,
        confidence_level REAL NOT NULL CHECK(confidence_level >= 0 AND confidence_level <= 100),
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        engine_version TEXT NOT NULL
    )
    """,
)

SCHEMA_VERSION = "0.2.0"
