"""
MODULE: TEST-006
FILE: TEST-006-001
Module Name: Prediction Panel State Tests
Version: 2.9.0
Purpose: Verifies source-level GUI clarity separation between current prediction and active trade panel modes without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.9.0: Added tests for active-trade panel title switching without changing trading logic.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class PredictionPanelStateTests(unittest.TestCase):
    """Validate bottom-left panel state-label implementation from source files."""

    def setUp(self) -> None:
        """Load GUI source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )

    def test_prediction_panel_supports_two_explicit_titles(self) -> None:
        """The panel source should explicitly support prediction and active-trade titles."""
        self.assertIn('"Current Prediction"', self._prediction_panel_source)
        self.assertIn('"Active Trade"', self._prediction_panel_source)
        self.assertIn("def update_active_trade", self._prediction_panel_source)

    def test_prediction_updates_restore_current_prediction_title(self) -> None:
        """Normal prediction updates should set the title back to Current Prediction."""
        update_prediction_start = self._prediction_panel_source.index("def update_prediction")
        update_active_trade_start = self._prediction_panel_source.index("def update_active_trade")
        update_prediction_body = self._prediction_panel_source[update_prediction_start:update_active_trade_start]
        self.assertIn('self._set_title("Current Prediction")', update_prediction_body)

    def test_main_window_routes_open_positions_to_active_trade_mode(self) -> None:
        """Open-position monitoring should use active-trade display mode instead of prediction wording."""
        self.assertIn("update_active_trade", self._main_window_source)
        self.assertIn('direction=f"{position_snapshot.direction} POSITION"', self._main_window_source)
        self.assertNotIn('direction=f"ACTIVE_{position_snapshot.direction}_POSITION"', self._main_window_source)


if __name__ == "__main__":
    unittest.main()
