"""
MODULE: SVC-011
FILE: SVC-011-001
Module Name: Auto Trade Diagnostics Service
Version: 2.6.0
Purpose: Explains Auto Trade execution readiness and blocking reasons without placing trades.
Dependencies: dataclasses, sentinel_ai.config.config_schema, sentinel_ai.models
Change History:
- 2.6.0: Added explicit Auto Trade diagnostic states for locked, disabled, waiting, blocked, armed, order-sent, and order-failed conditions.
"""

from __future__ import annotations

from dataclasses import dataclass

from sentinel_ai.config.config_schema import ManualTradingConfig, TradingConfig
from sentinel_ai.models.position_monitoring import PositionMonitorSnapshot
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.trade_execution import ManualTradeOrderResult


@dataclass(frozen=True)
class AutoTradeDiagnostic:
    """Represent the current Auto Trade readiness state and user-facing reason."""

    status: str
    reason: str
    actionable: bool = False
    direction: str = "-"
    confidence_percentage: float = 0.0
    risk_reward_ratio: float | None = None
    plan_key: str = ""


class AutoTradeDiagnosticsService:
    """Evaluate why Auto Trade can or cannot submit the current plan."""

    def evaluate(
        self,
        *,
        auto_trade_enabled: bool,
        trading_config: TradingConfig,
        manual_config: ManualTradingConfig,
        snapshot: RiskRewardSnapshot | None,
        position_snapshot: PositionMonitorSnapshot | None,
        last_plan_key: str | None,
    ) -> AutoTradeDiagnostic:
        """Return the current Auto Trade state without sending an order."""
        if trading_config.auto_trade_locked:
            return AutoTradeDiagnostic(
                status="LOCKED",
                reason="Auto Trade is locked until manual-mode lifecycle results are verified.",
            )
        if not auto_trade_enabled:
            return AutoTradeDiagnostic(
                status="DISABLED",
                reason="Auto Trade is OFF. Manual lifecycle validation remains the active stage.",
            )
        if snapshot is None:
            return AutoTradeDiagnostic(
                status="WAITING",
                reason="Waiting for a risk/reward snapshot from the latest market analysis.",
            )
        if snapshot.plan is None:
            return AutoTradeDiagnostic(
                status="WAITING",
                reason="Waiting for a valid TP/SL plan before Auto Trade can submit an order.",
                direction=snapshot.direction,
                confidence_percentage=float(snapshot.confidence_percentage),
            )

        plan = snapshot.plan
        plan_key = self.plan_key(snapshot)
        risk_reward_ratio = float(plan.risk_reward_ratio)
        direction = snapshot.direction
        confidence = float(snapshot.confidence_percentage)

        if not plan.valid:
            rejection = plan.rejection_reason or "Risk/reward plan is invalid."
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason=f"Plan invalid: {rejection}",
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if direction not in {"BUY_READY", "SELL_READY"}:
            return AutoTradeDiagnostic(
                status="WAITING",
                reason=f"Waiting for BUY_READY or SELL_READY. Current recommendation is {direction}.",
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if trading_config.one_trade_at_a_time and position_snapshot is not None and position_snapshot.has_open_position:
            ticket = position_snapshot.ticket if position_snapshot.ticket is not None else "unknown"
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason=f"One-trade-at-a-time guard is active and position {ticket} is still open.",
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if confidence < float(trading_config.minimum_confidence):
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason=(
                    f"Confidence {confidence:.2f}% is below the required "
                    f"{float(trading_config.minimum_confidence):.2f}%."
                ),
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if risk_reward_ratio < float(trading_config.default_risk_reward):
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason=(
                    f"Risk/reward {risk_reward_ratio:.2f} is below the required "
                    f"{float(trading_config.default_risk_reward):.2f}."
                ),
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if float(manual_config.default_volume) <= 0:
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason="Default trade volume must be greater than 0.00 before Auto Trade can submit.",
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if float(manual_config.default_volume) > float(manual_config.max_volume):
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason=(
                    f"Default volume {float(manual_config.default_volume):.2f} exceeds max volume "
                    f"{float(manual_config.max_volume):.2f}."
                ),
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        if plan_key == last_plan_key:
            return AutoTradeDiagnostic(
                status="BLOCKED",
                reason="Duplicate plan guard is active. This exact Auto Trade plan was already submitted.",
                direction=direction,
                confidence_percentage=confidence,
                risk_reward_ratio=risk_reward_ratio,
                plan_key=plan_key,
            )
        return AutoTradeDiagnostic(
            status="ARMED",
            reason="All Auto Trade guardrails passed. The app may submit this plan when Auto Trade is unlocked and enabled.",
            actionable=True,
            direction=direction,
            confidence_percentage=confidence,
            risk_reward_ratio=risk_reward_ratio,
            plan_key=plan_key,
        )

    def from_order_result(self, result: ManualTradeOrderResult) -> AutoTradeDiagnostic:
        """Return the post-submission diagnostic state for a completed order attempt."""
        if result.accepted:
            return AutoTradeDiagnostic(
                status="ORDER_SENT",
                reason=f"MT5 accepted the {result.direction} order. {result.message}",
                actionable=False,
                direction=result.direction,
            )
        return AutoTradeDiagnostic(
            status="ORDER_FAILED",
            reason=f"MT5 rejected or did not accept the order. {result.message}",
            actionable=False,
            direction=result.direction,
        )

    @staticmethod
    def plan_key(snapshot: RiskRewardSnapshot) -> str:
        """Return a stable key so one ready plan cannot be submitted repeatedly."""
        if snapshot.plan is None:
            return "NO_PLAN"
        plan = snapshot.plan
        return (
            f"{snapshot.symbol}:{snapshot.timeframe}:{snapshot.direction}:"
            f"{round(float(plan.entry_price), 3)}:{round(float(plan.stop_loss), 3)}:"
            f"{round(float(plan.take_profit), 3)}:{round(float(snapshot.confidence_percentage), 2)}"
        )
