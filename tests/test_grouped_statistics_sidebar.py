"""
MODULE: TEST-017
FILE: TEST-017-001
Module Name: Grouped Statistics Sidebar Tests
Version: 2.20.0
Purpose: Verifies the long left statistics sidebar is grouped into readable sections without changing field update keys.
Dependencies: pathlib, unittest
Change History:
- 2.20.0: Added source-level tests for grouped statistics sidebar readability.
"""

from __future__ import annotations

import unittest
from pathlib import Path


class GroupedStatisticsSidebarTests(unittest.TestCase):
    """Validate grouped statistics-sidebar source changes without requiring a desktop runtime."""

    def setUp(self) -> None:
        """Load statistics panel source for deterministic validation."""
        project_root = Path(__file__).resolve().parents[1]
        self._statistics_panel_source = (
            project_root / "src" / "sentinel_ai" / "gui" / "widgets" / "statistics_panel.py"
        ).read_text(encoding="utf-8")

    def test_sidebar_contains_named_sections(self) -> None:
        """Statistics rows should be grouped by operational purpose."""
        for section_name in (
            "Performance",
            "Trade Lifecycle",
            "Trade Monitoring",
            "Profit Lock Preview",
            "Automation",
            "Learning",
        ):
            self.assertIn(section_name, self._statistics_panel_source)
        self.assertIn("section_groups", self._statistics_panel_source)
        self.assertIn("SidebarSectionHeader", self._statistics_panel_source)

    def test_grouping_preserves_all_update_field_names(self) -> None:
        """Grouping must not break existing update_statistics and update_position_monitor keys."""
        for field_name in (
            "Today's Trades",
            "Lifecycle Stage",
            "Result Status",
            "Trade Pressure",
            "Risk Alert",
            "TP Progress",
            "Trade Health",
            "Profit Lock",
            "Next Lock Trigger",
            "Suggested Lock SL",
            "Auto Trade Status",
            "Auto Trade Reason",
            "Learning Status",
            "Learning Action",
        ):
            self.assertIn(f'"{field_name}"', self._statistics_panel_source)
        self.assertIn("self._fields[label_text] = value", self._statistics_panel_source)

    def test_grouped_rows_keep_compact_spacing(self) -> None:
        """Grouped rows should remain compact in the left sidebar."""
        self.assertIn("outer_layout.setSpacing(8)", self._statistics_panel_source)
        self.assertIn("grid.setHorizontalSpacing(7)", self._statistics_panel_source)
        self.assertIn("grid.setVerticalSpacing(3)", self._statistics_panel_source)
        self.assertIn("value.setWordWrap(True)", self._statistics_panel_source)


if __name__ == "__main__":
    unittest.main()
