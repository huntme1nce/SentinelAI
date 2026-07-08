"""
MODULE: TEST-015
FILE: TEST-015-001
Module Name: Chart-First Dashboard Layout Tests
Version: 2.20.0
Purpose: Verifies the GUI source uses a left statistics sidebar and chart-first workspace without requiring a desktop runtime.
Dependencies: pathlib, unittest
Change History:
- 2.20.0: Preserved chart-first tests while sidebar grouping improves readability.
- 2.19.0: Preserved chart-first tests while compact workspace validation moved to a dedicated test.
- 2.18.0: Added source-level tests for statistics sidebar, protected chart area, and trade panel below the chart.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class ChartFirstDashboardLayoutTests(unittest.TestCase):
    """Validate chart-first dashboard layout source changes."""

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

    def test_statistics_are_moved_to_scrollable_left_sidebar(self) -> None:
        """Main window should place Statistics in a scrollable fixed-width sidebar."""
        self.assertIn("QScrollArea", self._main_window_source)
        self.assertIn('statistics_sidebar.setObjectName("StatisticsSidebar")', self._main_window_source)
        self.assertIn("statistics_sidebar.setWidget(self._statistics_panel)", self._main_window_source)
        self.assertIn("statistics_sidebar.setMaximumWidth", self._main_window_source)
        self.assertIn("outer_layout.addWidget(statistics_sidebar, stretch=0)", self._main_window_source)

    def test_chart_and_trade_panel_share_center_workspace(self) -> None:
        """Chart should live in the center workspace with Active Trade panel below it."""
        self.assertIn('chart_workspace.setObjectName("ChartWorkspace")', self._main_window_source)
        chart_add_index = self._main_window_source.index("chart_layout.addWidget(self._chart_panel, stretch=12)")
        trade_add_index = self._main_window_source.index("chart_layout.addWidget(self._prediction_panel, stretch=0)")
        self.assertLess(chart_add_index, trade_add_index)
        self.assertIn("outer_layout.addWidget(chart_workspace, stretch=1)", self._main_window_source)

    def test_statistics_rows_wrap_inside_sidebar(self) -> None:
        """Long values should wrap instead of forcing the chart workspace to shrink further."""
        self.assertIn("value.setWordWrap(True)", self._statistics_panel_source)
        self.assertIn("self.setMinimumWidth(315)", self._statistics_panel_source)
        self.assertIn("QSizePolicy.Maximum", self._statistics_panel_source)

    def test_prediction_panel_is_documented_as_below_chart(self) -> None:
        """Prediction panel metadata should reflect below-chart placement."""
        self.assertIn("below the chart", self._prediction_panel_source)


if __name__ == "__main__":
    unittest.main()
