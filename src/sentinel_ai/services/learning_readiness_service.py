"""
MODULE: SVC-007
FILE: SVC-007-001
Module Name: Learning Readiness Service
Version: 2.8.0
Purpose: Builds statistical learning-readiness reviews from closed predictions and Sentinel ledger evidence without mutating strategy parameters.
Dependencies: collections, dataclasses, datetime, logging, sentinel_ai.config, sentinel_ai.models, sentinel_ai.database.repositories
Change History:
- 2.8.0: Added Stage 9 learning-readiness dataset review and recurring failure pattern summaries.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import LearningConfig
from sentinel_ai.database.repositories.learning_repository import LearningRepository
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.models.learning import LearningDatasetRow, LearningFailurePattern, LearningReadinessSnapshot
from sentinel_ai.models.sentinel_trade import SentinelOwnedTrade
from sentinel_ai.services.trade_manager_service import TradeManagerService


class LearningReadinessService:
    """Prepare evidence for future statistical learning without changing trading parameters."""

    def __init__(
        self,
        *,
        prediction_repository: PredictionRepository,
        learning_repository: LearningRepository,
        trade_manager_service: TradeManagerService,
        config: LearningConfig,
        logger: logging.Logger,
    ) -> None:
        """Initialize the read-only learning readiness service."""
        self._prediction_repository = prediction_repository
        self._learning_repository = learning_repository
        self._trade_manager_service = trade_manager_service
        self._config = config
        self._logger = logger
        self._latest_signature: str | None = None
        self._latest_snapshot: LearningReadinessSnapshot | None = None

    @property
    def latest_snapshot(self) -> LearningReadinessSnapshot | None:
        """Return the latest generated learning readiness snapshot for the current runtime."""
        return self._latest_snapshot

    def review(self, *, persist: bool = True) -> LearningReadinessSnapshot:
        """Build a current learning-readiness snapshot and persist it only if material evidence changed."""
        rows = self._prediction_repository.closed_learning_dataset(self._config.review_window_days)
        dataset = tuple(LearningDatasetRow(**row) for row in rows)
        ledger_records = self._trade_manager_service.ledger_records
        snapshot = self._build_snapshot(dataset, ledger_records)
        signature = self._build_signature(snapshot)
        if persist and signature != self._latest_signature:
            try:
                self._learning_repository.create_review(snapshot)
                self._latest_signature = signature
            except (OSError, ValueError, TypeError) as error:
                self._logger.warning("Learning readiness review persistence skipped: %s", error)
        self._latest_snapshot = snapshot
        return snapshot

    def _build_snapshot(
        self,
        dataset: tuple[LearningDatasetRow, ...],
        ledger_records: tuple[SentinelOwnedTrade, ...],
    ) -> LearningReadinessSnapshot:
        """Build the full statistical readiness snapshot from closed prediction rows."""
        sample_size = len(dataset)
        wins = len([row for row in dataset if row.outcome == "WIN"])
        losses = len([row for row in dataset if row.outcome == "LOSS"])
        breakeven = len([row for row in dataset if row.outcome == "BREAKEVEN"])
        win_rate = round((wins / sample_size * 100.0), 2) if sample_size else 0.0
        loss_rate = round((losses / sample_size * 100.0), 2) if sample_size else 0.0
        average_confidence = round(sum(row.confidence for row in dataset) / sample_size, 2) if sample_size else 0.0
        rr_values = [float(row.risk_reward) for row in dataset if row.risk_reward is not None and float(row.risk_reward) > 0]
        average_risk_reward = round(sum(rr_values) / len(rr_values), 2) if rr_values else 0.0
        patterns = self._failure_patterns(dataset)
        top_pattern = patterns[0] if patterns else None
        ready = sample_size >= self._config.minimum_closed_trades_for_review
        status = "COLLECTING_DATA"
        action = "NO_PARAMETER_CHANGE"
        recommendation = (
            f"Collect more verified closed predictions before parameter review. "
            f"Need {self._config.minimum_closed_trades_for_review}, current {sample_size}."
        )
        if ready and top_pattern is not None:
            status = "PATTERN_REVIEW_READY"
            recommendation = (
                f"Review recurring failure pattern before changing parameters: {top_pattern.description}. "
                "No automatic parameter change applied."
            )
        elif ready:
            status = "STATISTICAL_REVIEW_READY"
            recommendation = "Minimum sample reached. Review evidence manually. No automatic parameter change applied."

        supplemental_closed = [trade for trade in ledger_records if trade.closed and trade.close_result in {"WIN", "LOSS", "BREAKEVEN"}]
        linked_prediction_uids = {row.prediction_uid for row in dataset}
        unlinked_closed = [trade for trade in supplemental_closed if not trade.prediction_uid or trade.prediction_uid not in linked_prediction_uids]
        return LearningReadinessSnapshot(
            status=status,
            action=action,
            recommendation=recommendation,
            sample_size=sample_size,
            minimum_sample_size=self._config.minimum_closed_trades_for_review,
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate=win_rate,
            loss_rate=loss_rate,
            average_confidence=average_confidence,
            average_risk_reward=average_risk_reward,
            review_window_days=self._config.review_window_days,
            ready_for_parameter_review=ready,
            top_failure_pattern=top_pattern,
            patterns=patterns,
            supplemental_ledger_closed_trades=len(supplemental_closed),
            unlinked_ledger_closed_trades=len(unlinked_closed),
        )

    def _failure_patterns(self, dataset: tuple[LearningDatasetRow, ...]) -> tuple[LearningFailurePattern, ...]:
        """Return recurring loss-heavy groupings from the closed dataset."""
        grouped: dict[tuple[str, str, str, str, str], list[LearningDatasetRow]] = defaultdict(list)
        for row in dataset:
            key = (
                row.symbol,
                row.timeframe,
                row.direction,
                self._confidence_bucket(row.confidence),
                self._risk_reward_bucket(row.risk_reward),
            )
            grouped[key].append(row)

        patterns: list[LearningFailurePattern] = []
        for key, rows in grouped.items():
            losses = len([row for row in rows if row.outcome == "LOSS"])
            if losses < self._config.minimum_pattern_losses:
                continue
            sample_size = len(rows)
            wins = len([row for row in rows if row.outcome == "WIN"])
            breakeven = len([row for row in rows if row.outcome == "BREAKEVEN"])
            loss_rate = round((losses / sample_size * 100.0), 2) if sample_size else 0.0
            symbol, timeframe, direction, confidence_bucket, rr_bucket = key
            description = (
                f"{direction} {symbol} {timeframe}, confidence {confidence_bucket}, "
                f"RR {rr_bucket}: {losses}/{sample_size} losses ({loss_rate:.2f}%)."
            )
            patterns.append(
                LearningFailurePattern(
                    pattern_id="|".join(key),
                    symbol=symbol,
                    timeframe=timeframe,
                    direction=direction,
                    confidence_bucket=confidence_bucket,
                    risk_reward_bucket=rr_bucket,
                    sample_size=sample_size,
                    losses=losses,
                    wins=wins,
                    breakeven=breakeven,
                    loss_rate=loss_rate,
                    description=description,
                )
            )
        return tuple(sorted(patterns, key=lambda item: (item.losses, item.loss_rate, item.sample_size), reverse=True)[: self._config.max_failure_patterns])

    @staticmethod
    def _confidence_bucket(confidence: float) -> str:
        """Bucket confidence for pattern grouping."""
        value = float(confidence)
        if value < 60:
            return "<60"
        if value < 70:
            return "60-69"
        if value < 80:
            return "70-79"
        if value < 90:
            return "80-89"
        return "90+"

    @staticmethod
    def _risk_reward_bucket(risk_reward: float | None) -> str:
        """Bucket risk/reward ratios for pattern grouping."""
        if risk_reward is None or float(risk_reward) <= 0:
            return "NO_RR"
        value = float(risk_reward)
        if value < 1.5:
            return "<1.5"
        if value < 2.0:
            return "1.5-1.99"
        if value < 3.0:
            return "2.0-2.99"
        return "3.0+"

    @staticmethod
    def _build_signature(snapshot: LearningReadinessSnapshot) -> str:
        """Build a material signature to avoid persisting duplicate one-second reviews."""
        top_id = snapshot.top_failure_pattern.pattern_id if snapshot.top_failure_pattern is not None else "NO_PATTERN"
        return "|".join(
            str(part)
            for part in (
                snapshot.status,
                snapshot.sample_size,
                snapshot.wins,
                snapshot.losses,
                snapshot.breakeven,
                snapshot.win_rate,
                snapshot.loss_rate,
                top_id,
                snapshot.unlinked_ledger_closed_trades,
            )
        )
