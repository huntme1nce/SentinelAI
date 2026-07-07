"""
MODULE: SVC-003
FILE: SVC-003-001
Module Name: Prediction Lifecycle Service
Version: 2.5.0
Purpose: Persists material prediction lifecycle records without coupling GUI or trading execution to SQLite.
Dependencies: logging, sentinel_ai.database.repositories.prediction_repository, sentinel_ai.models.prediction, sentinel_ai.models.risk_reward
Change History:
- 2.5.0: Added deduplicated prediction persistence and trade-result lifecycle closure helpers.
"""

from __future__ import annotations

import logging
from datetime import timezone
from typing import Any

from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.models.prediction import (
    PredictionDirection,
    PredictionOutcome,
    PredictionRecord,
    PredictionStatus,
)
from sentinel_ai.models.risk_reward import RiskRewardSnapshot


class PredictionLifecycleService:
    """Persist and update material Sentinel AI prediction lifecycle states."""

    def __init__(
        self,
        repository: PredictionRepository,
        engine_version: str,
        logger: logging.Logger,
    ) -> None:
        """Initialize the lifecycle service with persistence and logging dependencies."""
        self._repository = repository
        self._engine_version = str(engine_version)
        self._logger = logger
        self._latest_prediction_uid: str | None = None
        self._latest_prediction_signature: str | None = None

    @property
    def latest_prediction_uid(self) -> str | None:
        """Return the latest persisted prediction UID for the current runtime session."""
        return self._latest_prediction_uid

    def record_from_risk_reward_snapshot(self, snapshot: RiskRewardSnapshot) -> str | None:
        """Persist one material risk/reward prediction snapshot and return its UID.

        The service intentionally deduplicates identical snapshots so a one-second
        chart refresh does not spam the database with the same prediction every
        cycle. A new row is created only when the material recommendation changes.
        """
        signature = self._build_signature(snapshot)
        if signature == self._latest_prediction_signature:
            return self._latest_prediction_uid

        try:
            record = self._build_record(snapshot)
            prediction_uid = self._repository.create(record)
        except (KeyError, ValueError, TypeError) as error:
            self._logger.warning("Prediction persistence skipped: %s", error)
            return None

        self._latest_prediction_signature = signature
        self._latest_prediction_uid = prediction_uid
        self._logger.info("Persisted prediction %s with signature %s.", prediction_uid, signature)
        return prediction_uid

    def mark_trade_active(self, prediction_uid: str | None) -> None:
        """Mark a persisted prediction as trade-active after MT5 accepts an order."""
        if not prediction_uid:
            return
        try:
            self._repository.update_status(prediction_uid, PredictionStatus.TRADE_ACTIVE)
        except KeyError as error:
            self._logger.warning("Prediction trade-active update skipped: %s", error)

    def close_from_ledger_result(
        self,
        prediction_uid: str | None,
        close_result: str,
        close_type: str,
    ) -> None:
        """Close a persisted prediction from a verified Sentinel ledger result."""
        if not prediction_uid:
            return
        normalized_result = str(close_result).strip().upper()
        if normalized_result not in {"WIN", "LOSS", "BREAKEVEN"}:
            return
        outcome = PredictionOutcome(normalized_result)
        normalized_close_type = str(close_type).strip().upper()
        tp_hit = "TP" in normalized_close_type or normalized_result == "WIN"
        sl_hit = "SL" in normalized_close_type or normalized_result == "LOSS"
        try:
            self._repository.close_prediction(
                prediction_uid=prediction_uid,
                outcome=outcome,
                tp_hit=tp_hit,
                sl_hit=sl_hit,
            )
        except KeyError as error:
            self._logger.warning("Prediction close update skipped: %s", error)

    def _build_record(self, snapshot: RiskRewardSnapshot) -> PredictionRecord:
        """Build a persistent prediction record from the latest risk/reward snapshot."""
        direction = self._prediction_direction(snapshot)
        status = self._prediction_status(snapshot)
        plan = snapshot.plan
        generated_at = snapshot.generated_at.astimezone(timezone.utc)
        metadata: dict[str, Any] = {
            "source_direction": snapshot.direction,
            "summary": snapshot.summary,
            "generated_at": generated_at.isoformat(),
        }
        if plan is not None:
            metadata.update(
                {
                    "plan_valid": plan.valid,
                    "stop_reason": plan.stop_reason,
                    "target_reason": plan.target_reason,
                    "rejection_reason": plan.rejection_reason,
                }
            )
        return PredictionRecord(
            symbol=snapshot.symbol,
            timeframe=snapshot.timeframe,
            direction=direction,
            confidence=float(snapshot.confidence_percentage),
            reason=snapshot.reason or snapshot.summary or "Risk/reward snapshot recorded.",
            engine_version=self._engine_version,
            entry_price=None if plan is None else float(plan.entry_price),
            stop_loss=None if plan is None else float(plan.stop_loss),
            take_profit=None if plan is None else float(plan.take_profit),
            risk_reward=None if plan is None else float(plan.risk_reward_ratio),
            status=status,
            created_at=generated_at,
            updated_at=generated_at,
            metadata=metadata,
        )

    @staticmethod
    def _prediction_direction(snapshot: RiskRewardSnapshot) -> PredictionDirection:
        """Translate risk/reward direction into a durable prediction direction."""
        if snapshot.direction == "BUY_READY":
            return PredictionDirection.BUY
        if snapshot.direction == "SELL_READY":
            return PredictionDirection.SELL
        return PredictionDirection.WAIT

    @staticmethod
    def _prediction_status(snapshot: RiskRewardSnapshot) -> PredictionStatus:
        """Return the initial lifecycle status for a risk/reward snapshot."""
        if snapshot.direction in {"BUY_READY", "SELL_READY"} and snapshot.plan is not None and snapshot.plan.valid:
            return PredictionStatus.VALIDATED
        return PredictionStatus.WAITING

    @staticmethod
    def _build_signature(snapshot: RiskRewardSnapshot) -> str:
        """Build a stable material signature for duplicate prediction suppression."""
        plan = snapshot.plan
        plan_parts: tuple[object, ...]
        if plan is None:
            plan_parts = ("NO_PLAN",)
        else:
            plan_parts = (
                round(float(plan.entry_price), 3),
                round(float(plan.stop_loss), 3),
                round(float(plan.take_profit), 3),
                round(float(plan.risk_reward_ratio), 2),
                bool(plan.valid),
                plan.rejection_reason,
            )
        return "|".join(
            str(part)
            for part in (
                snapshot.symbol,
                snapshot.timeframe,
                snapshot.direction,
                round(float(snapshot.confidence_percentage), 1),
                snapshot.reason,
                *plan_parts,
            )
        )
