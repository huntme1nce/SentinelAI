"""
MODULE: TEST-011
FILE: TEST-011-001
Module Name: Active Trade Risk Alert Visibility Tests
Version: 2.14.0
Purpose: Verifies source-level active-trade risk alert visibility without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.14.0: Added tests for display-only TP approach and SL danger risk alert visibility.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradeRiskAlertVisibilityTests(unittest.TestCase):
    """Validate display-only active-trade risk alert implementation from source files."""

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

    def test_active_trade_summary_includes_risk_alert(self) -> None:
        """The active-trade summary card should show the current display-only risk alert state."""
        self.assertIn("risk_alert", self._prediction_panel_source)
        self.assertIn("Risk Alert", self._prediction_panel_source)
        self.assertIn("Risk Alert:", self._prediction_panel_source)

    def test_main_window_resolves_risk_alert(self) -> None:
        """The main window should derive risk alert state without changing trading logic."""
        self.assertIn("def _resolve_trade_risk_alert", self._main_window_source)
        self.assertIn("SL_DANGER_ZONE", self._main_window_source)
        self.assertIn("TP_APPROACH_ZONE", self._main_window_source)
        self.assertIn("NEUTRAL_ZONE", self._main_window_source)
        self.assertIn("UNKNOWN_RISK", self._main_window_source)
        self.assertIn("proximity_ratio", self._main_window_source)

    def test_statistics_panel_exposes_risk_alert_row(self) -> None:
        """The statistics panel should expose risk alert for quick monitoring."""
        self.assertIn('"Risk Alert"', self._statistics_panel_source)
        self.assertIn('self._fields["Risk Alert"].setText', self._statistics_panel_source)
        self.assertIn("risk_alert", self._statistics_panel_source)


if __name__ == "__main__":
    unittest.main()
