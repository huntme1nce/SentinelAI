"""
MODULE: GUI-003
FILE: GUI-003-001
Module Name: Chart Panel
Version: 0.1.0
Purpose: Provides the central chart container for future embedded TradingView Lightweight Charts integration.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 0.1.0: Added chart panel shell with strict GUI-only responsibility.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ChartPanel(QFrame):
    """Render the central chart area without embedding trading logic."""

    def __init__(self) -> None:
        """Initialize the chart panel UI."""
        super().__init__()
        self.setObjectName("ChartPanel")
        self.setMinimumHeight(520)
        self._status_label = QLabel("Chart Area")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the chart panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.addWidget(self._status_label)

    def set_chart_status(self, message: str) -> None:
        """Set a chart status message supplied by a non-GUI service."""
        self._status_label.setText(message)
