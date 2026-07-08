"""
MODULE: TEST-012
FILE: TEST-012-001
Module Name: Active Trade Progress Ratio Visibility Tests
Version: 2.15.0
Purpose: Verifies source-level active-trade TP progress, SL risk, and route-state visibility without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.15.0: Added tests for display-only open-trade progress-ratio visibility.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradeProgressRatioVisibilityTests(unittest.TestCase):
    """Validate display-only active-trade progress-ratio implementation from source files."""

    def setUp(self) -> None:
        """Load GUI source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )
        self._statistics_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "statistics_panel.py"
        ).read_text(encoding="utf-8")

    def test_active_trade_summary_includes_progress_ratio_fields(self) -> None:
        """The active-trade summary card should show display-only progress ratios."""
        self.assertIn("take_profit_progress", self._prediction_panel_source)
        self.assertIn("stop_loss_risk", self._prediction_panel_source)
        self.assertIn("route_state", self._prediction_panel_source)
        self.assertIn("TP Progress:", self._prediction_panel_source)
        self.assertIn("SL Risk:", self._prediction_panel_source)
        self.assertIn("Route:", self._prediction_panel_source)

    def test_main_window_resolves_progress_ratios(self) -> None:
        """The main window should derive progress ratios without changing trading logic."""
        self.assertIn("def _build_active_trade_progress_ratio", self._main_window_source)
        self.assertIn("def _resolve_trade_progress_ratio", self._main_window_source)
        self.assertIn("def _clamped_percentage", self._main_window_source)
        self.assertIn("PROFIT_PROGRESS", self._main_window_source)
        self.assertIn("DRAWDOWN_RISK", self._main_window_source)
        self.assertIn("ENTRY_ZONE", self._main_window_source)

    def test_statistics_panel_exposes_progress_ratio_rows(self) -> None:
        """The statistics panel should expose progress ratio fields for quick monitoring."""
        self.assertIn('"TP Progress"', self._statistics_panel_source)
        self.assertIn('"SL Risk"', self._statistics_panel_source)
        self.assertIn('"Route State"', self._statistics_panel_source)
        self.assertIn('self._fields["TP Progress"].setText', self._statistics_panel_source)
        self.assertIn('self._fields["SL Risk"].setText', self._statistics_panel_source)
        self.assertIn('self._fields["Route State"].setText', self._statistics_panel_source)


if __name__ == "__main__":
    unittest.main()
