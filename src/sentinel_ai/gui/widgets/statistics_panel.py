"""
MODULE: GUI-003
FILE: GUI-003-003
Module Name: Statistics Panel
Version: 0.1.0
Purpose: Displays persistent prediction statistics in the bottom-right dashboard area.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 0.1.0: Added statistics dashboard panel fed by repository output.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class StatisticsPanel(QFrame):
    """Display stored prediction statistics without performing database queries."""

    def __init__(self) -> None:
        """Initialize the statistics panel."""
        super().__init__()
        self.setObjectName("Panel")
        self._fields: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the statistics panel layout."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        title = QLabel("Statistics")
        title.setStyleSheet("font-weight: 700; font-size: 12pt;")
        outer_layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        labels = ["Win Rate", "Loss Rate", "Average Confidence", "Today's Trades", "Learning Status"]
        for row, label_text in enumerate(labels):
            label = QLabel(f"{label_text}:")
            label.setObjectName("MutedLabel")
            value = QLabel("-")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._fields[label_text] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
        outer_layout.addLayout(grid)

    def update_statistics(self, statistics: dict[str, Any], learning_status: str) -> None:
        """Update visible statistics from persistent aggregate values."""
        self._fields["Win Rate"].setText(f"{statistics.get('win_rate', 0):.2f}%")
        self._fields["Loss Rate"].setText(f"{statistics.get('loss_rate', 0):.2f}%")
        self._fields["Average Confidence"].setText(f"{statistics.get('average_confidence', 0):.2f}%")
        self._fields["Today's Trades"].setText(str(statistics.get("todays_trades", 0)))
        self._fields["Learning Status"].setText(learning_status)
