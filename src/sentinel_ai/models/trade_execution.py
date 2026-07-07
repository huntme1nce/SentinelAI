"""
MODULE: MODEL-013
FILE: MODEL-013-001
Module Name: Trade Execution Models
2.4.0
Purpose: Defines immutable manual MT5 order request and result models.
Dependencies: dataclasses, datetime
Change History:
- 2.4.0: Preserved market order model for guarded auto-trade execution.
- 2.3.0: Preserved manual trade result model for completion build.
- 2.2.0: Preserved manual trade model for improved TP close settlement.
- 2.1.0: Preserved manual trade model for ledger maintenance tool build.
- 2.0.1: Preserved manual trade model for pending/backlog separation fix.
- 2.0.0: Preserved manual trade result model for final stabilization build.
- 1.9.0.2: Preserved manual trade result model for app helper binding hotfix.
- 1.9.0.1: Preserved manual trade result model for MT5 resolver binding hotfix.
- 1.9.0: Preserved manual trade result model for full stabilization audit.
- 1.8.4.1: Preserved manual trade result model for startup binding hotfix.
- 1.8.4: Preserved manual trade result model for lifecycle diagnostics sprint.
- 1.8.3: Preserved manual trade result model for pending-close settlement sprint.
- 1.8.2: Preserved manual trade result model for active-ticket close guard sprint.
- 1.8.1: Preserved manual trade result model for result verification dashboard sprint.
- 1.8.0: Preserved manual trade result model for ledger outcome persistence.
- 1.7.5: Preserved manual trade result model for persistent multi-trade Sentinel ledger.
- 1.7.4: Preserved manual trade result model for persistent Sentinel-owned tracking.
- 1.7.3: Preserved manual trade result model for Sentinel-owned tracking registration.
- 1.6.0: Preserved manual trade execution models for position monitoring sprint.
- 1.5.1: Preserved manual trade execution models for adaptive filling-mode fallback patch.
- 1.5.0: Added manual market order request/result models for Sprint 15.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ManualTradeOrderRequest:
    """Represent one user-confirmed manual market order request."""

    symbol: str
    direction: str
    volume: float
    stop_loss: float
    take_profit: float
    deviation_points: int
    magic_number: int
    comment: str
    order_filling: str


@dataclass(frozen=True)
class ManualTradeOrderResult:
    """Represent the result of a manual MT5 order placement attempt."""

    accepted: bool
    symbol: str
    direction: str
    volume: float
    requested_price: float | None
    filled_price: float | None
    stop_loss: float
    take_profit: float
    retcode: int | None
    order_ticket: int | None
    deal_ticket: int | None
    comment: str
    message: str
    sent_at: datetime
