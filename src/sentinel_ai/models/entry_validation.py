"""
MODULE: MODEL-011
FILE: MODEL-011-001
Module Name: Entry Validation Models
Version: 1.2.0
Purpose: Defines immutable entry-validation setup results used by the replaceable Entry Validation Engine.
Dependencies: dataclasses, datetime
Change History:
- 1.2.0: Added context-only BUY_SETUP / SELL_SETUP / WAIT validation snapshot for Sprint 12.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EntryZone:
    """Represent the nearest valid entry-zone candidate."""

    source: str
    direction: str
    lower_price: float
    upper_price: float
    distance_from_price: float
    valid: bool
    reason: str

    @property
    def label(self) -> str:
        """Return a compact label for the entry-zone candidate."""
        return f"{self.direction} {self.source}"


@dataclass(frozen=True)
class EntryValidationSnapshot:
    """Represent entry setup validation without trade execution permission."""

    symbol: str
    timeframe: str
    direction: str
    confidence_percentage: float
    readiness: str
    entry_zone: EntryZone | None
    generated_at: datetime
    summary: str
    reason: str
