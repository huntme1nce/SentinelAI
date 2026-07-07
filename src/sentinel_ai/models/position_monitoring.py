"""
MODULE: MODEL-014
FILE: MODEL-014-001
Module Name: Position Monitoring Models
2.0.1
Purpose: Defines immutable MT5 open-position and trade-statistics monitoring snapshots.
Dependencies: dataclasses, datetime
Change History:
- 2.4.0: Preserved trade statistics model for guarded auto-trade completion build.
- 2.3.0: Preserved simplified-dashboard and backend diagnostics fields for completion build.
- 2.2.0: Preserved backend pending/resolver fields while dashboard is simplified.
- 2.1.0: Preserved pending/backlog fields for ledger maintenance tool build.
- 2.0.1: Clarified pending close count as current settlement only, with stale records separated as backlog.
- 2.0.0: Added final stabilization dashboard fields for current trade priority, ledger repair, and stage completion.
- 1.9.0.2: Preserved resolver/audit fields for app helper binding hotfix.
- 1.9.0.1: Preserved resolver/audit fields for MT5 resolver binding hotfix.
- 1.9.0: Added close resolver status and audit warning fields.
- 1.8.4.1: Preserved lifecycle diagnostic fields for startup binding hotfix.
- 1.8.4: Added lifecycle stage, tracked ticket, and pending age diagnostics.
- 1.8.3: Added pending-close ledger counter for MT5 close-history settlement stage.
- 1.8.2: Preserved open/closed ledger counters for active-ticket close guard.
- 1.8.1: Added open/closed ledger counters and result status for trade result verification dashboard.
- 1.8.0: Added ledger-based Sentinel performance fields to the statistics snapshot.
- 1.7.5: Preserved Sentinel-only statistics fields for persistent multi-trade ledger statistics.
- 1.7.4: Preserved Sentinel-only statistics fields for persistent trade recovery.
- 1.7.3: Added Sentinel-owned statistics mode for app-created trade accuracy tracking.
- 1.7.2: Added history match mode and close type fields for MT5 history fallback tracking.
- 1.7.1.3: Preserved lifecycle models for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved lifecycle models for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved lifecycle models for candle countdown timer hotfix.
- 1.7.1: Preserved lifecycle models for countdown timer and active-header priority sprint.
- 1.7.0: Added last closed trade result fields for trade lifecycle tracking.
- 1.6.2: Added active-position protection status and missing SL/TP warning fields.
- 1.6.1.2: Preserved optional active-position TP/SL model fields for chart-scale hotfix.
- 1.6.1.1: Preserved position monitoring models for startup lock initialization hotfix.
- 1.6.1: Preserved position monitoring models for active-trade chart lock patch.
- 1.6.0: Added position monitoring and daily trade result statistics models for Sprint 16.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PositionMonitorSnapshot:
    """Represent the current monitored MT5 position state for one symbol."""

    symbol: str
    has_open_position: bool
    ticket: int | None
    direction: str
    volume: float
    open_price: float | None
    current_price: float | None
    stop_loss: float | None
    take_profit: float | None
    profit: float
    swap: float
    commission: float
    magic_number: int | None
    comment: str
    opened_at: datetime | None
    monitored_at: datetime
    message: str
    missing_stop_loss: bool = False
    missing_take_profit: bool = False
    protection_status: str = "UNKNOWN"


@dataclass(frozen=True)
class DailyTradeStatisticsSnapshot:
    """Represent simple same-day closed-deal statistics from MT5 history."""

    symbol: str
    total_closed_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate: float
    loss_rate: float
    net_profit: float
    generated_at: datetime
    message: str
    last_closed_ticket: int | None = None
    last_closed_profit: float | None = None
    last_closed_result: str = "NONE"
    last_closed_at: datetime | None = None
    last_close_reason: str = ""
    last_close_type: str = ""
    history_match_mode: str = "NONE"
    sentinel_owned_only: bool = True
    ledger_total_trades: int = 0
    ledger_open_trades: int = 0
    ledger_pending_close_trades: int = 0
    ledger_closed_trades: int = 0
    ledger_total_records: int = 0
    ledger_wins: int = 0
    ledger_losses: int = 0
    ledger_breakeven: int = 0
    ledger_win_rate: float = 0.0
    ledger_net_profit: float = 0.0
    result_status: str = ""
    lifecycle_stage: str = ""
    tracked_sentinel_ticket: int | None = None
    pending_close_age_seconds: int = 0
    close_resolver_status: str = ""
    audit_warning: str = ""
    pending_backlog_trades: int = 0
    stale_pending_trades: int = 0
    ledger_health: str = ""
    build_stage: str = ""
    completion_status: str = ""
