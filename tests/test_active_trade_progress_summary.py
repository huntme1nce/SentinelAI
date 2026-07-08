"""
MODULE: TEST-009
FILE: TEST-009-001
Module Name: Active Trade Progress Summary Tests
Version: 2.12.0
Purpose: Verifies source-level active-trade progress visibility without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.12.0: Added tests for current price, TP/SL distance, and nearest-target display.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradeProgressSummaryTests(unittest.TestCase):
    """Validate active-trade progress display implementation from source files."""

    def setUp(self) -> None:
        """Load GUI source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )

    def test_active_trade_summary_includes_progress_fields(self) -> None:
        """The active-trade summary should expose current price and TP/SL distance context."""
        self.assertIn("current_price", self._prediction_panel_source)
        self.assertIn("distance_to_take_profit", self._prediction_panel_source)
        self.assertIn("distance_to_stop_loss", self._prediction_panel_source)
        self.assertIn("closer_target", self._prediction_panel_source)
        self.assertIn("Distance to TP", self._prediction_panel_source)
        self.assertIn("Distance to SL", self._prediction_panel_source)
        self.assertIn("Closer:", self._prediction_panel_source)

    def test_main_window_builds_active_trade_progress_values(self) -> None:
        """The main window should compute display-only progress values from the position snapshot."""
        self.assertIn("def _build_active_trade_progress", self._main_window_source)
        self.assertIn("def _format_price_distance", self._main_window_source)
        self.assertIn("def _resolve_closer_trade_target", self._main_window_source)
        self.assertIn("position_snapshot.current_price", self._main_window_source)

    def test_update_active_trade_receives_progress_values(self) -> None:
        """The active-trade panel route should pass progress fields into the panel."""
        self.assertIn('active_trade_progress["current_price"]', self._main_window_source)
        self.assertIn('active_trade_progress["distance_to_take_profit"]', self._main_window_source)
        self.assertIn('active_trade_progress["distance_to_stop_loss"]', self._main_window_source)
        self.assertIn('active_trade_progress["closer_target"]', self._main_window_source)


if __name__ == "__main__":
    unittest.main()
