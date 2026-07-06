"""
MODULE: MODEL-001
FILE: MODEL-001-001
Module Name: Prediction Model
Version: 0.1.0
Purpose: Defines immutable domain models for Sentinel AI prediction records.
Dependencies: dataclasses, datetime, enum, json, uuid
Change History:
- 0.1.0: Added prediction direction, status, outcome, and record models.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class PredictionDirection(StrEnum):
    """Represent a prediction direction."""

    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


class PredictionStatus(StrEnum):
    """Represent the lifecycle status of a prediction."""

    PREDICTION = "PREDICTION"
    VALIDATED = "VALIDATED"
    WAITING = "WAITING"
    ENTRY_TRIGGERED = "ENTRY_TRIGGERED"
    TRADE_ACTIVE = "TRADE_ACTIVE"
    MONITORING = "MONITORING"
    CLOSED = "CLOSED"
    INVALIDATED = "INVALIDATED"
    CANCELLED = "CANCELLED"


class PredictionOutcome(StrEnum):
    """Represent the final outcome of a prediction."""

    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"
    CANCELLED = "CANCELLED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class PredictionRecord:
    """Represent a prediction record that can be permanently stored in SQLite."""

    symbol: str
    timeframe: str
    direction: PredictionDirection
    confidence: float
    reason: str
    engine_version: str
    prediction_uid: str = field(default_factory=lambda: str(uuid4()))
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    risk_reward: float | None = None
    status: PredictionStatus = PredictionStatus.PREDICTION
    outcome: PredictionOutcome | None = None
    tp_hit: bool = False
    sl_hit: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None
    duration_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate prediction invariants after dataclass initialization."""
        if not 0 <= self.confidence <= 100:
            raise ValueError("Prediction confidence must be between 0 and 100.")
        if self.direction != PredictionDirection.WAIT and self.entry_price is None:
            raise ValueError("BUY and SELL predictions require an entry price.")
        if not self.symbol.strip():
            raise ValueError("Prediction symbol cannot be empty.")
        if not self.timeframe.strip():
            raise ValueError("Prediction timeframe cannot be empty.")
        if not self.reason.strip():
            raise ValueError("Prediction reason cannot be empty.")

    def metadata_json(self) -> str:
        """Serialize prediction metadata into deterministic JSON."""
        return json.dumps(self.metadata, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def format_datetime(value: datetime | None) -> str | None:
        """Convert a datetime value into an SQLite-compatible UTC ISO string."""
        if value is None:
            return None
        return value.astimezone(timezone.utc).isoformat()
