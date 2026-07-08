"""
MODULE: TEST-007
FILE: TEST-007-001
Module Name: Active Trade Panel Summary Tests
Version: 2.10.0
Purpose: Verifies source-level active-trade summary-card presentation without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.10.0: Added tests for active-trade summary-card refinement.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ActiveTradePanelSummaryTests(unittest.TestCase):
    """Validate active-trade summary-card implementation from source files."""

    def setUp(self) -> None:
        """Load prediction panel source for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")

    def test_prediction_panel_has_summary_label(self) -> None:
        """The panel should expose a dedicated summary-card label above the field grid."""
        self.assertIn("self._summary_label", self._prediction_panel_source)
        self.assertIn("ActiveTradeSummary", self._prediction_panel_source)
        self.assertIn("current_summary", self._prediction_panel_source)

    def test_active_trade_summary_includes_core_trade_fields(self) -> None:
        """The active-trade summary should include direction, status, P/L, TP, and SL."""
        self.assertIn("def _build_active_trade_summary", self._prediction_panel_source)
        self.assertIn("direction", self._prediction_panel_source)
        self.assertIn("status", self._prediction_panel_source)
        self.assertIn("open_profit_loss", self._prediction_panel_source)
        self.assertIn("take_profit", self._prediction_panel_source)
        self.assertIn("stop_loss", self._prediction_panel_source)

    def test_layout_is_top_aligned_to_reduce_empty_space(self) -> None:
        """The panel layout should be top-aligned so active-trade details do not sit at the bottom."""
        self.assertIn("outer_layout.setAlignment(Qt.AlignTop)", self._prediction_panel_source)
        self.assertIn("outer_layout.addStretch(1)", self._prediction_panel_source)


if __name__ == "__main__":
    unittest.main()
