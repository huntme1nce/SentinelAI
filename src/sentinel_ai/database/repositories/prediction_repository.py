"""
MODULE: DB-002
FILE: DB-002-001
Module Name: Prediction Repository
Version: 2.8.0
Purpose: Provides permanent SQLite persistence and learning dataset queries for Sentinel AI predictions.
Dependencies: sqlite3, sentinel_ai.database.database_service, sentinel_ai.models.prediction
Change History:
- 2.8.0: Added closed learning dataset query for Stage 9 statistical readiness.
- 0.1.0: Added create, status update, outcome update, and statistics queries.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.models.prediction import PredictionOutcome, PredictionRecord, PredictionStatus


class PredictionRepository:
    """Persist and query prediction records in SQLite."""

    def __init__(self, database_service: DatabaseService) -> None:
        """Initialize repository with a database service dependency."""
        self._database_service = database_service

    def create(self, prediction: PredictionRecord) -> str:
        """Persist a new prediction and return its stable prediction UID."""
        with self._database_service.connection() as connection:
            connection.execute(
                """
                INSERT INTO predictions(
                    prediction_uid, symbol, timeframe, direction, confidence, reason,
                    entry_price, stop_loss, take_profit, risk_reward, status, outcome,
                    tp_hit, sl_hit, created_at, updated_at, closed_at, duration_seconds,
                    engine_version, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    prediction.prediction_uid,
                    prediction.symbol,
                    prediction.timeframe,
                    prediction.direction.value,
                    prediction.confidence,
                    prediction.reason,
                    prediction.entry_price,
                    prediction.stop_loss,
                    prediction.take_profit,
                    prediction.risk_reward,
                    prediction.status.value,
                    prediction.outcome.value if prediction.outcome else None,
                    int(prediction.tp_hit),
                    int(prediction.sl_hit),
                    PredictionRecord.format_datetime(prediction.created_at),
                    PredictionRecord.format_datetime(prediction.updated_at),
                    PredictionRecord.format_datetime(prediction.closed_at),
                    prediction.duration_seconds,
                    prediction.engine_version,
                    prediction.metadata_json(),
                ),
            )
            connection.commit()
        return prediction.prediction_uid

    def update_status(self, prediction_uid: str, status: PredictionStatus) -> None:
        """Update the lifecycle status for an existing prediction."""
        now = datetime.now(timezone.utc).isoformat()
        with self._database_service.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE predictions
                SET status = ?, updated_at = ?
                WHERE prediction_uid = ?
                """,
                (status.value, now, prediction_uid),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Prediction not found: {prediction_uid}")
            connection.commit()

    def close_prediction(
        self,
        prediction_uid: str,
        outcome: PredictionOutcome,
        tp_hit: bool,
        sl_hit: bool,
    ) -> None:
        """Close an existing prediction with a final outcome."""
        now = datetime.now(timezone.utc).isoformat()
        with self._database_service.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE predictions
                SET status = ?, outcome = ?, tp_hit = ?, sl_hit = ?, closed_at = ?,
                    updated_at = ?,
                    duration_seconds = CAST((julianday(?) - julianday(created_at)) * 86400 AS INTEGER)
                WHERE prediction_uid = ?
                """,
                (
                    PredictionStatus.CLOSED.value,
                    outcome.value,
                    int(tp_hit),
                    int(sl_hit),
                    now,
                    now,
                    now,
                    prediction_uid,
                ),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Prediction not found: {prediction_uid}")
            connection.commit()


    def closed_learning_dataset(self, review_window_days: int) -> list[dict[str, Any]]:
        """Return closed prediction rows prepared for learning-readiness review."""
        window_days = max(1, int(review_window_days))
        with self._database_service.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    prediction_uid, symbol, timeframe, direction, confidence, risk_reward,
                    outcome, tp_hit, sl_hit, reason, created_at, closed_at,
                    duration_seconds, metadata_json
                FROM predictions
                WHERE status = 'CLOSED'
                  AND outcome IN ('WIN', 'LOSS', 'BREAKEVEN')
                  AND closed_at IS NOT NULL
                  AND datetime(closed_at) >= datetime('now', ?)
                ORDER BY closed_at ASC, id ASC
                """,
                (f"-{window_days} days",),
            ).fetchall()
        dataset: list[dict[str, Any]] = []
        for row in rows:
            try:
                import json

                metadata = json.loads(row["metadata_json"] or "{}")
            except (TypeError, ValueError):
                metadata = {}
            dataset.append(
                {
                    "prediction_uid": str(row["prediction_uid"]),
                    "symbol": str(row["symbol"]),
                    "timeframe": str(row["timeframe"]),
                    "direction": str(row["direction"]),
                    "confidence": float(row["confidence"] or 0.0),
                    "risk_reward": None if row["risk_reward"] is None else float(row["risk_reward"]),
                    "outcome": str(row["outcome"]),
                    "tp_hit": bool(row["tp_hit"]),
                    "sl_hit": bool(row["sl_hit"]),
                    "reason": str(row["reason"]),
                    "created_at": str(row["created_at"]),
                    "closed_at": None if row["closed_at"] is None else str(row["closed_at"]),
                    "duration_seconds": None if row["duration_seconds"] is None else int(row["duration_seconds"]),
                    "metadata": metadata if isinstance(metadata, dict) else {},
                }
            )
        return dataset

    def summary_statistics(self) -> dict[str, Any]:
        """Return stable aggregate statistics for dashboard display."""
        with self._database_service.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_predictions,
                    SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END) AS losses,
                    AVG(confidence) AS average_confidence,
                    SUM(CASE WHEN date(created_at) = date('now') THEN 1 ELSE 0 END) AS todays_trades
                FROM predictions
                """
            ).fetchone()

        total = int(row["total_predictions"] or 0)
        wins = int(row["wins"] or 0)
        losses = int(row["losses"] or 0)
        average_confidence = float(row["average_confidence"] or 0.0)
        todays_trades = int(row["todays_trades"] or 0)
        closed_total = wins + losses
        win_rate = (wins / closed_total * 100) if closed_total else 0.0
        loss_rate = (losses / closed_total * 100) if closed_total else 0.0

        return {
            "total_predictions": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "average_confidence": round(average_confidence, 2),
            "todays_trades": todays_trades,
        }
