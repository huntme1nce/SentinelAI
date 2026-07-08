"""
MODULE: MODEL-016
FILE: MODEL-016-001
Module Name: Learning Readiness Models
Version: 2.8.0
Purpose: Defines immutable review models for statistical learning readiness without automatic strategy mutation.
Dependencies: dataclasses, datetime, typing
Change History:
- 2.8.0: Added learning dataset, recurring failure pattern, and readiness snapshot models for Stage 9.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class LearningDatasetRow:
    """Represent one closed prediction row prepared for statistical learning review."""

    prediction_uid: str
    symbol: str
    timeframe: str
    direction: str
    confidence: float
    risk_reward: float | None
    outcome: str
    tp_hit: bool
    sl_hit: bool
    reason: str
    created_at: str
    closed_at: str | None
    duration_seconds: int | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningFailurePattern:
    """Represent a recurring failure grouping found in the closed prediction dataset."""

    pattern_id: str
    symbol: str
    timeframe: str
    direction: str
    confidence_bucket: str
    risk_reward_bucket: str
    sample_size: int
    losses: int
    wins: int
    breakeven: int
    loss_rate: float
    description: str


@dataclass(frozen=True)
class LearningReadinessSnapshot:
    """Represent Sentinel AI learning readiness without applying automatic parameter changes."""

    review_uid: str = field(default_factory=lambda: str(uuid4()))
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "COLLECTING_DATA"
    action: str = "NO_PARAMETER_CHANGE"
    recommendation: str = "Collect more verified closed trades before reviewing strategy parameters."
    sample_size: int = 0
    minimum_sample_size: int = 30
    wins: int = 0
    losses: int = 0
    breakeven: int = 0
    win_rate: float = 0.0
    loss_rate: float = 0.0
    average_confidence: float = 0.0
    average_risk_reward: float = 0.0
    review_window_days: int = 30
    ready_for_parameter_review: bool = False
    top_failure_pattern: LearningFailurePattern | None = None
    patterns: tuple[LearningFailurePattern, ...] = ()
    supplemental_ledger_closed_trades: int = 0
    unlinked_ledger_closed_trades: int = 0

    def dashboard_fields(self) -> dict[str, object]:
        """Return compact fields for the existing statistics dashboard."""
        if self.top_failure_pattern is None:
            pattern_text = "None yet"
        else:
            pattern_text = self.top_failure_pattern.description
        return {
            "learning_status": self.status,
            "learning_sample_size": f"{self.sample_size}/{self.minimum_sample_size}",
            "learning_pattern": pattern_text,
            "learning_action": self.action,
            "learning_recommendation": self.recommendation,
        }
