"""
MODULE: TEST-005
FILE: TEST-005-001
Module Name: Learning Readiness Service Tests
Version: 2.8.0
Purpose: Verifies Stage 9 statistical learning-readiness reviews, sample-size gating, and recurring failure pattern detection.
Dependencies: datetime, logging, os, tempfile, unittest, sentinel_ai.config, sentinel_ai.database, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.8.0: Added learning-readiness tests without automatic strategy mutation.
"""

from __future__ import annotations

import logging
import os
import tempfile
import unittest
from datetime import datetime, timezone
from uuid import uuid4

from sentinel_ai.config.config_schema import DatabaseConfig, LearningConfig
from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.database.repositories.learning_repository import LearningRepository
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.models.prediction import PredictionDirection, PredictionOutcome, PredictionRecord
from sentinel_ai.services.learning_readiness_service import LearningReadinessService


class _TradeManagerStub:
    """Expose deterministic ledger records for learning-readiness tests."""

    @property
    def ledger_records(self) -> tuple[object, ...]:
        """Return no supplemental ledger records for isolated tests."""
        return ()


class LearningReadinessServiceTests(unittest.TestCase):
    """Validate Stage 9 learning-readiness behavior."""

    def setUp(self) -> None:
        """Create an isolated SQLite database for each learning test."""
        self._temp_dir = tempfile.TemporaryDirectory()
        self._previous_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = self._temp_dir.name
        self._database_service = DatabaseService(DatabaseConfig(filename=f"learning_{uuid4().hex}.sqlite3"))
        self._database_service.initialize()
        self._prediction_repository = PredictionRepository(self._database_service)
        self._learning_repository = LearningRepository(self._database_service)
        self._service = LearningReadinessService(
            prediction_repository=self._prediction_repository,
            learning_repository=self._learning_repository,
            trade_manager_service=_TradeManagerStub(),  # type: ignore[arg-type]
            config=LearningConfig(
                statistical_review_enabled=True,
                review_window_days=30,
                minimum_closed_trades_for_review=4,
                minimum_pattern_losses=2,
                max_failure_patterns=3,
                automatic_parameter_adjustment_enabled=False,
            ),
            logger=logging.getLogger("sentinel_ai.tests.learning_readiness"),
        )

    def tearDown(self) -> None:
        """Restore environment and clean temporary files."""
        if self._previous_appdata is None:
            os.environ.pop("APPDATA", None)
        else:
            os.environ["APPDATA"] = self._previous_appdata
        if self._database_service.database_path.exists():
            self._database_service.database_path.unlink()
        self._temp_dir.cleanup()

    def test_learning_review_collects_data_until_minimum_sample_size(self) -> None:
        """Learning should collect data and avoid parameter changes below sample threshold."""
        self._create_closed_prediction("WIN", confidence=82.0)
        self._create_closed_prediction("LOSS", confidence=83.0)
        snapshot = self._service.review()
        self.assertEqual(snapshot.status, "COLLECTING_DATA")
        self.assertEqual(snapshot.action, "NO_PARAMETER_CHANGE")
        self.assertEqual(snapshot.sample_size, 2)
        latest_review = self._learning_repository.latest_review()
        self.assertIsNotNone(latest_review)
        self.assertEqual(latest_review["action"], "NO_PARAMETER_CHANGE")

    def test_learning_review_identifies_recurring_failure_pattern(self) -> None:
        """Repeated losses in the same evidence bucket should become a review pattern, not an automatic change."""
        self._create_closed_prediction("LOSS", confidence=82.0)
        self._create_closed_prediction("LOSS", confidence=84.0)
        self._create_closed_prediction("LOSS", confidence=85.0)
        self._create_closed_prediction("WIN", confidence=86.0)
        snapshot = self._service.review()
        self.assertEqual(snapshot.status, "PATTERN_REVIEW_READY")
        self.assertEqual(snapshot.action, "NO_PARAMETER_CHANGE")
        self.assertTrue(snapshot.ready_for_parameter_review)
        self.assertIsNotNone(snapshot.top_failure_pattern)
        self.assertIn("BUY XAUUSDm M5", snapshot.top_failure_pattern.description)

    def _create_closed_prediction(self, outcome: str, *, confidence: float) -> str:
        """Create and close one deterministic BUY prediction."""
        record = PredictionRecord(
            symbol="XAUUSDm",
            timeframe="M5",
            direction=PredictionDirection.BUY,
            confidence=confidence,
            reason="validation learning row",
            engine_version="2.8.0-test",
            entry_price=2000.0,
            stop_loss=1995.0,
            take_profit=2010.0,
            risk_reward=2.0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        uid = self._prediction_repository.create(record)
        self._prediction_repository.close_prediction(
            uid,
            PredictionOutcome(outcome),
            tp_hit=outcome == "WIN",
            sl_hit=outcome == "LOSS",
        )
        return uid


if __name__ == "__main__":
    unittest.main()
