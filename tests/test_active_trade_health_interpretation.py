"""
MODULE: TEST-013
FILE: TEST-013-001
Module Name: Active Trade Health Interpretation Tests
Version: 2.16.0
Purpose: Verifies source-level active-trade health interpretation visibility without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.16.0: Added tests for display-only active-trade health interpretation.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradeHealthInterpretationTests(unittest.TestCase):
    """Validate display-only active-trade health interpretation from source files."""

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

    def test_active_trade_summary_includes_health_interpretation(self) -> None:
        """The active-trade summary card should show a display-only health line."""
        self.assertIn("trade_health", self._prediction_panel_source)
        self.assertIn("Trade Health:", self._prediction_panel_source)

    def test_main_window_resolves_trade_health_without_execution_changes(self) -> None:
        """The main window should derive health labels from display-state inputs only."""
        self.assertIn("def _resolve_trade_health", self._main_window_source)
        self.assertIn("def _parse_percentage_label", self._main_window_source)
        self.assertIn("HEALTHY_PROGRESS", self._main_window_source)
        self.assertIn("HIGH_RISK_NEAR_SL", self._main_window_source)
        self.assertIn("STRONG_PROGRESS_NEAR_TP", self._main_window_source)
        self.assertIn("WATCH_DRAWDOWN", self._main_window_source)

    def test_statistics_panel_exposes_trade_health_row(self) -> None:
        """The statistics panel should expose Trade Health for quick monitoring."""
        self.assertIn('"Trade Health"', self._statistics_panel_source)
        self.assertIn('self._fields["Trade Health"].setText', self._statistics_panel_source)


if __name__ == "__main__":
    unittest.main()
