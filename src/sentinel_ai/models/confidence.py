"""
MODULE: MODEL-010
FILE: MODEL-010-001
Module Name: Confidence Models
Version: 1.1.0
Purpose: Defines immutable confidence scoring results used by the replaceable Confidence Engine.
Dependencies: dataclasses, datetime
Change History:
- 1.1.0: Added context-only confidence scoring snapshot for Sprint 11.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConfidenceContribution:
    """Represent one confidence scoring component."""

    component: str
    score: float
    max_score: float
    bias: str
    reason: str

    @property
    def normalized_score(self) -> float:
        """Return component score normalized to 0-100."""
        if self.max_score <= 0:
            return 0.0
        return max(0.0, min(100.0, (self.score / self.max_score) * 100.0))


@dataclass(frozen=True)
class ConfidenceSnapshot:
    """Represent read-only confidence context without trade execution permission."""

    symbol: str
    timeframe: str
    direction: str
    bias: str
    score_percentage: float
    readiness: str
    contributions: tuple[ConfidenceContribution, ...]
    generated_at: datetime
    summary: str
    reason: str
