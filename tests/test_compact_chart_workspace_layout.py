"""
MODULE: TEST-016
FILE: TEST-016-001
Module Name: Compact Chart Workspace Layout Tests
Version: 2.20.0
Purpose: Verifies the chart-first layout protects chart height with a compact fixed-height trade panel and narrower statistics sidebar.
Dependencies: pathlib, unittest
Change History:
- 2.20.0: Preserved compact workspace checks while sidebar rows are grouped.
- 2.19.0: Added source-level tests for compact below-chart trade panel and reduced sidebar width pressure.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class CompactChartWorkspaceLayoutTests(unittest.TestCase):
    """Validate chart-first compact layout source changes without requiring a desktop runtime."""

    def setUp(self) -> None:
        """Load GUI source files for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._main_window_source = (project_root / "src" / "sentinel_ai" / "gui" / "main_window.py").read_text(
            encoding="utf-8"
        )
        self._statistics_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "statistics_panel.py"
        ).read_text(encoding="utf-8")
        self._prediction_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "prediction_panel.py"
        ).read_text(encoding="utf-8")

    def test_trade_panel_is_fixed_height_below_chart(self) -> None:
        """Below-chart trade panel should be capped so the chart keeps vertical priority."""
        self.assertIn("self._prediction_panel.setMinimumHeight(175)", self._main_window_source)
        self.assertIn("self._prediction_panel.setMaximumHeight(265)", self._main_window_source)
        self.assertIn("self._prediction_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)", self._main_window_source)
        self.assertIn("chart_layout.addWidget(self._chart_panel, stretch=12)", self._main_window_source)
        self.assertIn("chart_layout.addWidget(self._prediction_panel, stretch=0)", self._main_window_source)

    def test_statistics_sidebar_is_narrower_to_protect_chart_width(self) -> None:
        """Statistics sidebar should be narrower than the first chart-first layout."""
        self.assertIn("statistics_sidebar.setMinimumWidth(330)", self._main_window_source)
        self.assertIn("statistics_sidebar.setMaximumWidth(430)", self._main_window_source)
        self.assertIn("self.setMinimumWidth(315)", self._statistics_panel_source)
        self.assertIn("grid.setHorizontalSpacing(7)", self._statistics_panel_source)
        self.assertIn("grid.setVerticalSpacing(3)", self._statistics_panel_source)

    def test_active_trade_summary_is_compact(self) -> None:
        """Summary card should be height-capped and use compact spacing."""
        self.assertIn("outer_layout.setContentsMargins(12, 10, 12, 10)", self._prediction_panel_source)
        self.assertIn("outer_layout.setSpacing(6)", self._prediction_panel_source)
        self.assertIn("self._summary_label.setMaximumHeight(135)", self._prediction_panel_source)
        self.assertIn("grid.setVerticalSpacing(4)", self._prediction_panel_source)


if __name__ == "__main__":
    unittest.main()
