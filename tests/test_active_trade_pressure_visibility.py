"""
MODULE: TEST-010
FILE: TEST-010-001
Module Name: Active Trade Pressure Visibility Tests
Version: 2.13.0
Purpose: Verifies source-level active-trade pressure visibility without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.13.0: Added tests for Trade Pressure summary and statistics routing.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradePressureVisibilityTests(unittest.TestCase):
    """Validate display-only trade-pressure implementation from source files."""

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

    def test_active_trade_summary_includes_trade_pressure(self) -> None:
        """The active-trade summary card should show the current display-only pressure state."""
        self.assertIn("trade_pressure", self._prediction_panel_source)
        self.assertIn("Trade Pressure", self._prediction_panel_source)
        self.assertIn("Trade Pressure:", self._prediction_panel_source)

    def test_main_window_resolves_trade_pressure(self) -> None:
        """The main window should derive pressure from the nearest target without changing trading logic."""
        self.assertIn("def _resolve_trade_pressure", self._main_window_source)
        self.assertIn("TP_PRESSURE", self._main_window_source)
        self.assertIn("SL_PRESSURE", self._main_window_source)
        self.assertIn("NEUTRAL_PRESSURE", self._main_window_source)
        self.assertIn("UNKNOWN_PRESSURE", self._main_window_source)

    def test_statistics_panel_exposes_trade_pressure_row(self) -> None:
        """The statistics panel should expose trade pressure for quick monitoring."""
        self.assertIn('"Trade Pressure"', self._statistics_panel_source)
        self.assertIn('self._fields["Trade Pressure"].setText', self._statistics_panel_source)
        self.assertIn("trade_pressure", self._statistics_panel_source)


if __name__ == "__main__":
    unittest.main()
