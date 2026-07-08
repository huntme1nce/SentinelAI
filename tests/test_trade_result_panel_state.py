"""
MODULE: TEST-008
FILE: TEST-008-001
Module Name: Trade Result Panel State Tests
Version: 2.11.0
Purpose: Verifies source-level closed-trade result panel presentation without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.11.0: Added tests for verified closed-trade result panel routing.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class TradeResultPanelStateTests(unittest.TestCase):
    """Validate bottom-left verified trade-result display implementation from source files."""

    def setUp(self) -> None:
        """Load GUI source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )

    def test_prediction_panel_supports_trade_result_mode(self) -> None:
        """The panel should explicitly support a verified Trade Result state."""
        self.assertIn('"Trade Result"', self._prediction_panel_source)
        self.assertIn("def update_trade_result", self._prediction_panel_source)
        self.assertIn("def _build_trade_result_summary", self._prediction_panel_source)

    def test_trade_result_summary_includes_result_close_profit_and_ticket(self) -> None:
        """The result summary should expose the result, close type, P/L, ticket, and close time."""
        self.assertIn("result", self._prediction_panel_source)
        self.assertIn("close_type", self._prediction_panel_source)
        self.assertIn("profit_loss", self._prediction_panel_source)
        self.assertIn("ticket", self._prediction_panel_source)
        self.assertIn("closed_at", self._prediction_panel_source)

    def test_main_window_routes_closed_verified_trade_to_result_panel(self) -> None:
        """Closed verified trade data should be routed to the Trade Result panel mode."""
        self.assertIn("update_trade_result", self._main_window_source)
        self.assertIn("last_closed_result", self._main_window_source)
        self.assertIn("last_closed_ticket", self._main_window_source)
        self.assertIn("last_closed_at", self._main_window_source)


if __name__ == "__main__":
    unittest.main()
