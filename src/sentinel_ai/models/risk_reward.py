"""
MODULE: MODEL-012
FILE: MODEL-012-001
Module Name: Risk Reward Models
1.4.0
Purpose: Defines immutable TP, SL, and risk/reward validation results used by the replaceable Risk Reward Engine.
Dependencies: dataclasses, datetime
Change History:
- 1.6.0: Preserved risk/reward models for position monitoring sprint.
- 1.5.0: Preserved risk/reward models for Sprint 15 manual execution.
- 1.4.1: Preserved risk/reward models for reviewed-plan snapshot patch.
- 1.4.0: Preserved immutable risk/reward models for trade plan overlay and manual review gate sprint.
- 1.3.3: Preserved immutable risk/reward models for extended TP target discovery patch.
- 1.3.2: Preserved immutable risk/reward models for rejected-plan display and directional TP guard patch.
- 1.3.1: Preserved immutable risk/reward models for smart TP target selection patch.
- 1.3.0: Added BUY_READY / SELL_READY / WAIT risk validation snapshot for Sprint 13.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RiskRewardPlan:
    """Represent a validated or rejected TP/SL plan."""

    setup_direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_points: float
    reward_points: float
    risk_reward_ratio: float
    stop_reason: str
    target_reason: str
    valid: bool
    rejection_reason: str


@dataclass(frozen=True)
class RiskRewardSnapshot:
    """Represent TP/SL and risk/reward validation without trade execution permission."""

    symbol: str
    timeframe: str
    direction: str
    confidence_percentage: float
    plan: RiskRewardPlan | None
    generated_at: datetime
    summary: str
    reason: str

    @property
    def entry_price(self) -> float | None:
        """Return planned entry price when available."""
        return None if self.plan is None else self.plan.entry_price

    @property
    def stop_loss(self) -> float | None:
        """Return planned stop loss when available."""
        return None if self.plan is None else self.plan.stop_loss

    @property
    def take_profit(self) -> float | None:
        """Return planned take profit when available."""
        return None if self.plan is None else self.plan.take_profit

    @property
    def risk_reward_ratio(self) -> float | None:
        """Return planned risk/reward ratio when available."""
        return None if self.plan is None else self.plan.risk_reward_ratio
