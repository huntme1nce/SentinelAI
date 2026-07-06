"""
MODULE: DB-002
FILE: DB-002-001
Module Name: Prediction Repository
Version: 0.1.0
Purpose: Provides permanent SQLite persistence for Sentinel AI predictions.
Dependencies: sqlite3, sentinel_ai.database.database_service, sentinel_ai.models.prediction
Change History:
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
