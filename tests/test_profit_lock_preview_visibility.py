"""
MODULE: TEST-014
FILE: TEST-014-001
Module Name: Profit Lock Preview Visibility Tests
Version: 2.17.0
Purpose: Verifies display-only Profit Lock preview visibility without requiring MT5 or live SL modification.
Dependencies: pathlib, unittest
Change History:
- 2.17.0: Added tests for future Profit Lock Manager preview fields and execution-disabled config.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


class ProfitLockPreviewVisibilityTests(unittest.TestCase):
    """Validate display-only Profit Lock readiness preview source changes."""

    def setUp(self) -> None:
        """Load source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")
        self._statistics_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "statistics_panel.py"
        ).read_text(encoding="utf-8")
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )
        self._config_schema_source = (project_root / "src" / "sentinel_ai" / "config" / "config_schema.py").read_text(
            encoding="utf-8"
        )
        self._default_config = json.loads(
            (project_root / "src" / "sentinel_ai" / "resources" / "config" / "default_config.json").read_text(
                encoding="utf-8"
            )
        )

    def test_active_trade_summary_includes_profit_lock_preview(self) -> None:
        """The active-trade summary should include display-only Profit Lock preview fields."""
        self.assertIn("Profit Lock:", self._prediction_panel_source)
        self.assertIn("profit_lock_state", self._prediction_panel_source)
        self.assertIn("suggested_lock_sl", self._prediction_panel_source)
        self.assertIn("suggested_lock_progress", self._prediction_panel_source)

    def test_statistics_panel_exposes_profit_lock_preview_rows(self) -> None:
        """The statistics panel should expose future lock-preview fields."""
        self.assertIn('"Profit Lock"', self._statistics_panel_source)
        self.assertIn('"Next Lock Trigger"', self._statistics_panel_source)
        self.assertIn('"Suggested Lock SL"', self._statistics_panel_source)
        self.assertIn('"Suggested Lock"', self._statistics_panel_source)

    def test_main_window_preview_is_display_only_and_forward_only(self) -> None:
        """Main-window preview helpers must not perform SL modifications or widen risk."""
        self.assertIn("def _build_profit_lock_preview", self._main_window_source)
        self.assertIn("def _resolve_profit_lock_price", self._main_window_source)
        self.assertIn("def _is_profit_lock_forward_only", self._main_window_source)
        self.assertIn("STAGE_1_LOCK_READY", self._main_window_source)
        self.assertIn("STAGE_2_LOCK_READY", self._main_window_source)
        self.assertIn("WATCHING_50_TRIGGER", self._main_window_source)
        self.assertNotIn("order_send", self._main_window_source)
        self.assertNotIn("TRADE_ACTION_SLTP", self._main_window_source)

    def test_profit_lock_config_is_present_but_execution_disabled(self) -> None:
        """The default config should document future Profit Lock settings while execution remains disabled."""
        profit_lock = self._default_config["profit_lock"]
        self.assertTrue(profit_lock["enabled"])
        self.assertFalse(profit_lock["execution_enabled"])
        self.assertTrue(profit_lock["apply_to_manual_trades"])
        self.assertTrue(profit_lock["apply_to_auto_trades"])
        self.assertIn("class ProfitLockConfig", self._config_schema_source)
        self.assertIn("execution_enabled false", self._config_schema_source)


if __name__ == "__main__":
    unittest.main()
