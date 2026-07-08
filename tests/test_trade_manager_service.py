"""
MODULE: TEST-004
FILE: TEST-004-001
Module Name: Trade Manager Service Tests
Version: 2.7.0
Purpose: Verifies Stage 8 TradeManagerService ownership of Sentinel trade registration, ledger totals, and close-result prediction linkage.
Dependencies: datetime, logging, os, tempfile, unittest, sentinel_ai.config, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.7.0: Added Trade Manager service tests for lifecycle extraction and ledger statistics integrity.
"""

from __future__ import annotations

import logging
import os
import tempfile
import unittest
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import ManualTradingConfig
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.models.risk_reward import RiskRewardPlan, RiskRewardSnapshot
from sentinel_ai.models.trade_execution import ManualTradeOrderResult
from sentinel_ai.services.trade_manager_service import TradeManagerService


class _PredictionLifecycleStub:
    """Capture prediction lifecycle calls without using SQLite."""

    def __init__(self) -> None:
        self.active_uid: str | None = None
        self.closed: list[tuple[str | None, str, str]] = []

    def record_from_risk_reward_snapshot(self, snapshot: RiskRewardSnapshot) -> str:
        """Return a deterministic prediction UID."""
        return f"prediction-{snapshot.symbol}-{snapshot.timeframe}"

    def mark_trade_active(self, prediction_uid: str | None) -> None:
        """Record active prediction status."""
        self.active_uid = prediction_uid

    def close_from_ledger_result(self, prediction_uid: str | None, close_result: str, close_type: str) -> None:
        """Record closed prediction status."""
        self.closed.append((prediction_uid, close_result, close_type))


class _TradeGatewayStub:
    """Provide deterministic position and statistics responses for TradeManagerService."""

    def __init__(self) -> None:
        self.statistics = DailyTradeStatisticsSnapshot(
            symbol="XAUUSDm",
            total_closed_trades=0,
            wins=0,
            losses=0,
            breakeven=0,
            win_rate=0.0,
            loss_rate=0.0,
            net_profit=0.0,
            generated_at=datetime.now(timezone.utc),
            message="No Sentinel app trade closed yet.",
            history_match_mode="SENTINEL_ONLY_NO_TICKET",
            sentinel_owned_only=True,
        )

    def daily_trade_statistics(self, **_: object) -> DailyTradeStatisticsSnapshot:
        """Return the configured deterministic statistics snapshot."""
        return self.statistics


class TradeManagerServiceTests(unittest.TestCase):
    """Validate service-owned Sentinel trade lifecycle behavior."""

    def setUp(self) -> None:
        """Create an isolated APPDATA folder for each ledger test."""
        self._temp_dir = tempfile.TemporaryDirectory()
        self._previous_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = self._temp_dir.name
        self._prediction_stub = _PredictionLifecycleStub()
        self._gateway = _TradeGatewayStub()
        self._service = TradeManagerService(
            mt5_service=self._gateway,  # type: ignore[arg-type]
            manual_config=self._manual_config(),
            prediction_lifecycle_service=self._prediction_stub,  # type: ignore[arg-type]
            logger=logging.getLogger("sentinel_ai.tests.trade_manager"),
            pending_stale_seconds=300,
        )

    def tearDown(self) -> None:
        """Restore APPDATA after each test."""
        if self._previous_appdata is None:
            os.environ.pop("APPDATA", None)
        else:
            os.environ["APPDATA"] = self._previous_appdata
        self._temp_dir.cleanup()

    def test_register_trade_persists_ledger_and_marks_prediction_active(self) -> None:
        """Accepted Sentinel trades should be persisted by TradeManagerService, not the GUI."""
        trade = self._service.register_sentinel_owned_trade(
            self._ready_buy_snapshot(),
            self._accepted_buy_result(),
            source="SENTINEL_APP_MANUAL",
        )
        self.assertIsNotNone(trade)
        self.assertEqual(self._prediction_stub.active_uid, "prediction-XAUUSDm-M5")
        self.assertEqual(len(self._service.ledger_records), 1)
        self.assertTrue(self._service.sentinel_trade_ledger_path().exists())

    def test_close_result_updates_ledger_totals_and_prediction(self) -> None:
        """A verified MT5 close result should close the Sentinel ledger and linked prediction."""
        self._service.register_sentinel_owned_trade(self._ready_buy_snapshot(), self._accepted_buy_result())
        closed_stats = DailyTradeStatisticsSnapshot(
            symbol="XAUUSDm",
            total_closed_trades=1,
            wins=1,
            losses=0,
            breakeven=0,
            win_rate=100.0,
            loss_rate=0.0,
            net_profit=15.0,
            generated_at=datetime.now(timezone.utc),
            message="validation close",
            last_closed_ticket=101,
            last_closed_profit=15.0,
            last_closed_result="WIN",
            last_closed_at=datetime.now(timezone.utc),
            last_close_type="TP HIT",
            history_match_mode="SENTINEL_TICKET_MATCH",
            sentinel_owned_only=True,
        )
        event = self._service.track_position_lifecycle(self._no_open_position(), closed_stats)
        self.assertIn("Sentinel app trade closed", event.message)
        totals = self._service.statistics_with_ledger_totals(closed_stats)
        self.assertEqual(totals.ledger_closed_trades, 1)
        self.assertEqual(totals.ledger_wins, 1)
        self.assertEqual(totals.completion_status, "STAGE_8_COMPLETE_AUTO_TRADE_LOCKED")
        self.assertEqual(self._prediction_stub.closed[-1], ("prediction-XAUUSDm-M5", "WIN", "TP HIT"))

    @staticmethod
    def _manual_config() -> ManualTradingConfig:
        """Return deterministic manual trading settings."""
        return ManualTradingConfig.from_dict(
            {
                "enabled": True,
                "default_volume": 0.01,
                "max_volume": 1.0,
                "deviation_points": 30,
                "magic_number": 151500,
                "order_comment": "SentinelAI manual",
                "order_filling": "AUTO",
                "one_position_per_symbol": True,
            }
        )

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

    @staticmethod
    def _accepted_buy_result() -> ManualTradeOrderResult:
        """Build one accepted MT5 order result."""
        return ManualTradeOrderResult(
            accepted=True,
            symbol="XAUUSDm",
            direction="BUY",
            volume=0.01,
            requested_price=2000.0,
            filled_price=2000.1,
            stop_loss=1995.0,
            take_profit=2010.0,
            retcode=10009,
            order_ticket=101,
            deal_ticket=202,
            comment="validation accepted",
            message="accepted",
            sent_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _no_open_position() -> PositionMonitorSnapshot:
        """Build a no-open-position snapshot."""
        return PositionMonitorSnapshot(
            symbol="XAUUSDm",
            has_open_position=False,
            ticket=None,
            direction="NONE",
            volume=0.0,
            open_price=None,
            current_price=None,
            stop_loss=None,
            take_profit=None,
            profit=0.0,
            swap=0.0,
            commission=0.0,
            magic_number=151500,
            comment="",
            opened_at=None,
            monitored_at=datetime.now(timezone.utc),
            message="No open position.",
        )


if __name__ == "__main__":
    unittest.main()
