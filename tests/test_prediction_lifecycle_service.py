"""
MODULE: TEST-002
FILE: TEST-002-001
Module Name: Prediction Lifecycle Service Tests
Version: 2.5.0
Purpose: Verifies deduplicated prediction persistence and trade-result closure behavior.
Dependencies: datetime, logging, os, tempfile, unittest, sentinel_ai.database, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.5.0: Added prediction lifecycle persistence tests.
"""

from __future__ import annotations

import logging
import os
import tempfile
import unittest
from uuid import uuid4
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import DatabaseConfig
from sentinel_ai.database.database_service import DatabaseService
from sentinel_ai.database.repositories.prediction_repository import PredictionRepository
from sentinel_ai.models.risk_reward import RiskRewardPlan, RiskRewardSnapshot
from sentinel_ai.services.prediction_lifecycle_service import PredictionLifecycleService


class PredictionLifecycleServiceTests(unittest.TestCase):
    """Validate prediction persistence lifecycle behavior."""

    def setUp(self) -> None:
        """Create an isolated SQLite database for each test."""
        self._temp_dir = tempfile.TemporaryDirectory()
        self._previous_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = self._temp_dir.name
        self._database_filename = f"sentinel_test_{uuid4().hex}.sqlite3"
        self._database_service = DatabaseService(DatabaseConfig(filename=self._database_filename))
        if self._database_service.database_path.exists():
            self._database_service.database_path.unlink()
        self._database_service.initialize()
        self._repository = PredictionRepository(self._database_service)
        self._service = PredictionLifecycleService(
            repository=self._repository,
            engine_version="2.5.0-test",
            logger=logging.getLogger("sentinel_ai.tests.prediction_lifecycle"),
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

    def test_repeated_snapshot_is_deduplicated(self) -> None:
        """The same one-second refresh snapshot should not create duplicate rows."""
        snapshot = self._ready_buy_snapshot()
        first_uid = self._service.record_from_risk_reward_snapshot(snapshot)
        second_uid = self._service.record_from_risk_reward_snapshot(snapshot)
        self.assertEqual(first_uid, second_uid)
        with self._database_service.connection() as connection:
            count = connection.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        self.assertEqual(count, 1)

    def test_trade_result_closes_linked_prediction(self) -> None:
        """A verified ledger result should close the linked prediction record."""
        prediction_uid = self._service.record_from_risk_reward_snapshot(self._ready_buy_snapshot())
        self._service.mark_trade_active(prediction_uid)
        self._service.close_from_ledger_result(prediction_uid, "WIN", "TP HIT")
        with self._database_service.connection() as connection:
            row = connection.execute(
                "SELECT status, outcome, tp_hit, sl_hit FROM predictions WHERE prediction_uid = ?",
                (prediction_uid,),
            ).fetchone()
        self.assertEqual(row["status"], "CLOSED")
        self.assertEqual(row["outcome"], "WIN")
        self.assertEqual(row["tp_hit"], 1)
        self.assertEqual(row["sl_hit"], 0)

    @staticmethod
    def _ready_buy_snapshot() -> RiskRewardSnapshot:
        """Build one deterministic BUY_READY risk/reward snapshot."""
        return RiskRewardSnapshot(
            symbol="XAUUSDm",
            timeframe="M5",
            direction="BUY_READY",
            confidence_percentage=82.5,
            plan=RiskRewardPlan(
                setup_direction="BUY_SETUP",
                entry_price=2000.0,
                stop_loss=1995.0,
                take_profit=2010.0,
                risk_points=5.0,
                reward_points=10.0,
                risk_reward_ratio=2.0,
                stop_reason="validation stop",
                target_reason="validation target",
                valid=True,
                rejection_reason="",
            ),
            generated_at=datetime.now(timezone.utc),
            summary="BUY_READY validation snapshot",
            reason="Structure, liquidity, momentum, and RR are aligned.",
        )


if __name__ == "__main__":
    unittest.main()
