"""
MODULE: DB-003
FILE: DB-003-001
Module Name: Learning Repository
Version: 2.8.0
Purpose: Persists read-only statistical learning readiness reviews without applying strategy changes.
Dependencies: json, sentinel_ai.database.database_service, sentinel_ai.models.learning
Change History:
- 2.8.0: Added persisted learning review snapshots for Stage 9 readiness.
"""

from __future__ import annotations

import json

from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.models.learning import LearningReadinessSnapshot


class LearningRepository:
    """Persist learning-readiness review snapshots in SQLite."""

    def __init__(self, database_service: DatabaseService) -> None:
        """Initialize repository with the active database service."""
        self._database_service = database_service

    def create_review(self, snapshot: LearningReadinessSnapshot) -> str:
        """Persist one material learning-readiness review and return its UID."""
        top_pattern_json = "{}"
        if snapshot.top_failure_pattern is not None:
            top_pattern_json = json.dumps(snapshot.top_failure_pattern.__dict__, sort_keys=True, ensure_ascii=False)
        metadata = {
            "patterns": [pattern.__dict__ for pattern in snapshot.patterns],
            "recommendation": snapshot.recommendation,
            "supplemental_ledger_closed_trades": snapshot.supplemental_ledger_closed_trades,
            "unlinked_ledger_closed_trades": snapshot.unlinked_ledger_closed_trades,
        }
        with self._database_service.connection() as connection:
            connection.execute(
                """
                INSERT INTO learning_reviews(
                    review_uid, generated_at, status, action, sample_size,
                    minimum_sample_size, wins, losses, breakeven, win_rate,
                    loss_rate, average_confidence, average_risk_reward,
                    review_window_days, ready_for_parameter_review, top_failure_pattern_json,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.review_uid,
                    snapshot.generated_at.isoformat(),
                    snapshot.status,
                    snapshot.action,
                    snapshot.sample_size,
                    snapshot.minimum_sample_size,
                    snapshot.wins,
                    snapshot.losses,
                    snapshot.breakeven,
                    snapshot.win_rate,
                    snapshot.loss_rate,
                    snapshot.average_confidence,
                    snapshot.average_risk_reward,
                    snapshot.review_window_days,
                    int(snapshot.ready_for_parameter_review),
                    top_pattern_json,
                    json.dumps(metadata, sort_keys=True, ensure_ascii=False),
                ),
            )
            connection.commit()
        return snapshot.review_uid

    def latest_review(self) -> dict[str, object] | None:
        """Return the latest persisted review row for diagnostics and tests."""
        with self._database_service.connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM learning_reviews
                ORDER BY generated_at DESC, id DESC
                LIMIT 1
                """
            ).fetchone()
        return dict(row) if row is not None else None
