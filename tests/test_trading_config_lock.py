"""
MODULE: TEST-001
FILE: TEST-001-001
Module Name: Trading Configuration Lock Tests
Version: 2.5.0
Purpose: Verifies Auto Trade lock defaults for the manual-mode stabilization baseline.
Dependencies: unittest, sentinel_ai.config.config_schema
Change History:
- 2.5.0: Added explicit Auto Trade lock configuration tests.
"""

from __future__ import annotations

import unittest

from sentinel_ai.config.config_schema import TradingConfig


class TradingConfigLockTests(unittest.TestCase):
    """Validate conservative Auto Trade lock behavior."""

    def test_auto_trade_lock_defaults_true_when_missing(self) -> None:
        """Legacy configs should remain locked unless explicitly unlocked later."""
        config = TradingConfig.from_dict(
            {
                "symbol": "GOLDm#",
                "default_timeframe": "M5",
                "auto_trade_enabled": False,
                "one_trade_at_a_time": True,
                "minimum_confidence": 75.0,
                "default_risk_reward": 2.0,
            }
        )
        self.assertTrue(config.auto_trade_locked)

    def test_auto_trade_lock_reads_packaged_value(self) -> None:
        """Packaged configs can explicitly declare the Auto Trade lock."""
        config = TradingConfig.from_dict(
            {
                "symbol": "GOLDm#",
                "default_timeframe": "M5",
                "auto_trade_enabled": False,
                "one_trade_at_a_time": True,
                "minimum_confidence": 75.0,
                "default_risk_reward": 2.0,
                "auto_trade_locked": True,
            }
        )
        self.assertTrue(config.auto_trade_locked)


if __name__ == "__main__":
    unittest.main()
