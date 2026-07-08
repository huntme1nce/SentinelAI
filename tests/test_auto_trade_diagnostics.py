"""
MODULE: TEST-003
FILE: TEST-003-001
Module Name: Auto Trade Diagnostics Tests
Version: 2.6.0
Purpose: Verifies explicit Auto Trade readiness states and blocker reasons without sending MT5 orders.
Dependencies: datetime, unittest, sentinel_ai.config, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.6.0: Added diagnostics tests for locked, blocked, armed, duplicate, and order-result states.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import ManualTradingConfig, TradingConfig
from sentinel_ai.models.risk_reward import RiskRewardPlan, RiskRewardSnapshot
from sentinel_ai.models.trade_execution import ManualTradeOrderResult
from sentinel_ai.services.auto_trade_diagnostics_service import AutoTradeDiagnosticsService


class AutoTradeDiagnosticsServiceTests(unittest.TestCase):
    """Validate Auto Trade diagnostics without requiring MT5 or Qt."""

    def setUp(self) -> None:
        """Create a diagnostics service for each test."""
        self._service = AutoTradeDiagnosticsService()
        self._manual_config = ManualTradingConfig.from_dict(
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

    def test_locked_config_reports_locked_before_other_gates(self) -> None:
        """A locked build should clearly state that Auto Trade is locked."""
        diagnostic = self._service.evaluate(
            auto_trade_enabled=True,
            trading_config=self._trading_config(auto_trade_locked=True),
            manual_config=self._manual_config,
            snapshot=self._ready_buy_snapshot(),
            position_snapshot=None,
            last_plan_key=None,
        )
        self.assertEqual(diagnostic.status, "LOCKED")
        self.assertIn("locked", diagnostic.reason.lower())
        self.assertFalse(diagnostic.actionable)

    def test_enabled_but_low_confidence_reports_blocked_reason(self) -> None:
        """A ready plan below minimum confidence should not fail silently."""
        diagnostic = self._service.evaluate(
            auto_trade_enabled=True,
            trading_config=self._trading_config(auto_trade_locked=False),
            manual_config=self._manual_config,
            snapshot=self._ready_buy_snapshot(confidence=65.0),
            position_snapshot=None,
            last_plan_key=None,
        )
        self.assertEqual(diagnostic.status, "BLOCKED")
        self.assertIn("Confidence 65.00%", diagnostic.reason)
        self.assertIn("75.00%", diagnostic.reason)

    def test_valid_new_ready_plan_reports_armed(self) -> None:
        """A valid new ready plan should reach ARMED, not remain silently waiting."""
        diagnostic = self._service.evaluate(
            auto_trade_enabled=True,
            trading_config=self._trading_config(auto_trade_locked=False),
            manual_config=self._manual_config,
            snapshot=self._ready_buy_snapshot(),
            position_snapshot=None,
            last_plan_key=None,
        )
        self.assertEqual(diagnostic.status, "ARMED")
        self.assertTrue(diagnostic.actionable)
        self.assertTrue(diagnostic.plan_key)

    def test_duplicate_plan_reports_blocked(self) -> None:
        """The same ready plan should expose duplicate blocking instead of doing nothing."""
        snapshot = self._ready_buy_snapshot()
        plan_key = AutoTradeDiagnosticsService.plan_key(snapshot)
        diagnostic = self._service.evaluate(
            auto_trade_enabled=True,
            trading_config=self._trading_config(auto_trade_locked=False),
            manual_config=self._manual_config,
            snapshot=snapshot,
            position_snapshot=None,
            last_plan_key=plan_key,
        )
        self.assertEqual(diagnostic.status, "BLOCKED")
        self.assertIn("Duplicate", diagnostic.reason)

    def test_order_result_diagnostic_reports_failed_submission(self) -> None:
        """Failed MT5 submissions should be visible as ORDER_FAILED."""
        result = ManualTradeOrderResult(
            accepted=False,
            symbol="XAUUSDm",
            direction="BUY",
            volume=0.01,
            requested_price=None,
            filled_price=None,
            stop_loss=1995.0,
            take_profit=2010.0,
            retcode=10030,
            order_ticket=None,
            deal_ticket=None,
            comment="validation only",
            message="Unsupported filling mode",
            sent_at=datetime.now(timezone.utc),
        )
        diagnostic = self._service.from_order_result(result)
        self.assertEqual(diagnostic.status, "ORDER_FAILED")
        self.assertIn("Unsupported filling mode", diagnostic.reason)

    @staticmethod
    def _trading_config(*, auto_trade_locked: bool) -> TradingConfig:
        """Build deterministic trading configuration for diagnostics tests."""
        return TradingConfig.from_dict(
            {
                "symbol": "GOLDm#",
                "default_timeframe": "M5",
                "auto_trade_enabled": False,
                "one_trade_at_a_time": True,
                "minimum_confidence": 75.0,
                "default_risk_reward": 2.0,
                "auto_trade_locked": auto_trade_locked,
            }
        )

    @staticmethod
    def _ready_buy_snapshot(*, confidence: float = 82.5, rr: float = 2.0) -> RiskRewardSnapshot:
        """Build one deterministic BUY_READY risk/reward snapshot."""
        return RiskRewardSnapshot(
            symbol="XAUUSDm",
            timeframe="M5",
            direction="BUY_READY",
            confidence_percentage=confidence,
            plan=RiskRewardPlan(
                setup_direction="BUY_SETUP",
                entry_price=2000.0,
                stop_loss=1995.0,
                take_profit=2010.0,
                risk_points=5.0,
                reward_points=10.0,
                risk_reward_ratio=rr,
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
