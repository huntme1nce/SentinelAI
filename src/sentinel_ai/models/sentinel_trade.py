"""
MODULE: MODEL-015
FILE: MODEL-015-001
Module Name: Sentinel-Owned Trade Models
2.5.0
Purpose: Defines immutable app-owned trade tracking records used to separate Sentinel AI trades from outside MT5 history.
Dependencies: dataclasses, datetime
Change History:
- 2.5.0: Added optional prediction UID link for database lifecycle persistence.
- 2.4.0: Preserved ledger model for manual and auto Sentinel trades.
- 2.3.0: Preserved ledger model for pending history repair.
- 2.2.0: Preserved ledger model for improved TP close settlement.
- 2.1.0: Preserved pending close ledger fields for ledger maintenance tool build.
- 2.0.1: Preserved pending close ledger fields for pending/backlog separation fix.
- 2.0.0: Preserved pending close model for final stabilization build.
- 1.9.0.2: Preserved pending close model for app helper binding hotfix.
- 1.9.0.1: Preserved pending close model for MT5 resolver binding hotfix.
- 1.9.0: Preserved pending close model for full stabilization audit.
- 1.8.4.1: Preserved pending-close fields for startup binding hotfix.
- 1.8.4: Preserved pending-close fields for lifecycle diagnostics sprint.
- 1.8.3: Added pending-close settlement fields for MT5 history delay handling.
- 1.8.2: Preserved close-result ledger fields for active-ticket close guard.
- 1.8.1: Preserved close-result ledger fields for result verification dashboard.
- 1.8.0: Added persisted close-result fields for long-term ledger-based performance statistics.
- 1.7.5: Preserved JSON trade records for persistent multi-trade Sentinel ledger.
- 1.7.4: Added JSON persistence helpers for Sentinel-owned trade recovery across app restarts.
- 1.7.3: Added Sentinel-owned manual trade tracking model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SentinelOwnedTrade:
    """Represent one trade created from Sentinel AI manual confirmation."""

    symbol: str
    direction: str
    order_ticket: int | None
    deal_ticket: int | None
    position_ticket: int | None
    entry_price: float | None
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    confidence_percentage: float
    timeframe: str
    opened_at: datetime
    source: str = "SENTINEL_APP_MANUAL"
    closed: bool = False
    close_ticket: int | None = None
    close_profit: float | None = None
    close_result: str = "NONE"
    close_type: str = ""
    close_reason: str = ""
    closed_at: datetime | None = None
    history_match_mode: str = ""
    pending_close: bool = False
    pending_close_since: datetime | None = None
    prediction_uid: str | None = None


    def to_dict(self) -> dict[str, Any]:
        """Serialize the Sentinel-owned trade for local JSON persistence."""
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "order_ticket": self.order_ticket,
            "deal_ticket": self.deal_ticket,
            "position_ticket": self.position_ticket,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_reward_ratio": self.risk_reward_ratio,
            "confidence_percentage": self.confidence_percentage,
            "timeframe": self.timeframe,
            "opened_at": self.opened_at.isoformat(),
            "source": self.source,
            "closed": self.closed,
            "close_ticket": self.close_ticket,
            "close_profit": self.close_profit,
            "close_result": self.close_result,
            "close_type": self.close_type,
            "close_reason": self.close_reason,
            "closed_at": self.closed_at.isoformat() if self.closed_at is not None else None,
            "history_match_mode": self.history_match_mode,
            "pending_close": self.pending_close,
            "pending_close_since": self.pending_close_since.isoformat() if self.pending_close_since is not None else None,
            "prediction_uid": self.prediction_uid,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentinelOwnedTrade":
        """Hydrate a Sentinel-owned trade from local JSON persistence."""
        opened_at_raw = str(data.get("opened_at", ""))
        try:
            opened_at = datetime.fromisoformat(opened_at_raw)
            if opened_at.tzinfo is None:
                opened_at = opened_at.replace(tzinfo=timezone.utc)
        except ValueError:
            opened_at = datetime.now(timezone.utc)
        return cls(
            symbol=str(data.get("symbol", "")),
            direction=str(data.get("direction", "")),
            order_ticket=_optional_int(data.get("order_ticket")),
            deal_ticket=_optional_int(data.get("deal_ticket")),
            position_ticket=_optional_int(data.get("position_ticket")),
            entry_price=_optional_float(data.get("entry_price")),
            stop_loss=float(data.get("stop_loss", 0.0) or 0.0),
            take_profit=float(data.get("take_profit", 0.0) or 0.0),
            risk_reward_ratio=float(data.get("risk_reward_ratio", 0.0) or 0.0),
            confidence_percentage=float(data.get("confidence_percentage", 0.0) or 0.0),
            timeframe=str(data.get("timeframe", "")),
            opened_at=opened_at,
            source=str(data.get("source", "SENTINEL_APP_MANUAL")),
            closed=bool(data.get("closed", False)),
            close_ticket=_optional_int(data.get("close_ticket")),
            close_profit=_optional_float(data.get("close_profit")),
            close_result=str(data.get("close_result", "NONE")),
            close_type=str(data.get("close_type", "")),
            close_reason=str(data.get("close_reason", "")),
            closed_at=_optional_datetime(data.get("closed_at")),
            history_match_mode=str(data.get("history_match_mode", "")),
            pending_close=bool(data.get("pending_close", False)),
            pending_close_since=_optional_datetime(data.get("pending_close_since")),
            prediction_uid=_optional_str(data.get("prediction_uid")),
        )


def _optional_datetime(value: Any) -> datetime | None:
    """Safely convert a persisted JSON value to an optional timezone-aware datetime."""
    if value in {None, ""}:
        return None
    try:
        converted = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    if converted.tzinfo is None:
        return converted.replace(tzinfo=timezone.utc)
    return converted


def _optional_int(value: Any) -> int | None:
    """Safely convert a persisted JSON value to an optional integer."""
    if value in {None, ""}:
        return None
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return None
    return converted if converted > 0 else None


def _optional_float(value: Any) -> float | None:
    """Safely convert a persisted JSON value to an optional float."""
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    """Safely convert a persisted JSON value to an optional stripped string."""
    if value in {None, ""}:
        return None
    converted = str(value).strip()
    return converted or None
