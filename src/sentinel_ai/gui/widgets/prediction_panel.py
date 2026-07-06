"""
MODULE: GUI-003
FILE: GUI-003-002
Module Name: Prediction Panel
Version: 0.1.0
Purpose: Displays the current prediction fields in the bottom-left dashboard area.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 0.1.0: Added current prediction dashboard panel.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class PredictionPanel(QFrame):
    """Display current prediction details without calculating trading decisions."""

    def __init__(self) -> None:
        """Initialize the current prediction panel."""
        super().__init__()
        self.setObjectName("Panel")
        self._fields: dict[str, QLabel] = {}
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        """Build the prediction panel layout."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        title = QLabel("Current Prediction")
        title.setStyleSheet("font-weight: 700; font-size: 12pt;")
        outer_layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        labels = ["Direction", "Confidence", "Timeframe", "Reason", "TP", "SL", "Risk Reward"]
        for row, label_text in enumerate(labels):
            label = QLabel(f"{label_text}:")
            label.setObjectName("MutedLabel")
            value = QLabel("-")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._fields[label_text] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
        outer_layout.addLayout(grid)

    def clear(self) -> None:
        """Reset the panel to a neutral display state."""
        for value_label in self._fields.values():
            value_label.setText("-")

    def update_prediction(
        self,
        direction: str,
        confidence: str,
        timeframe: str,
        reason: str,
        take_profit: str,
        stop_loss: str,
        risk_reward: str,
    ) -> None:
        """Update visible prediction fields from already computed prediction values."""
        self._fields["Direction"].setText(direction)
        self._fields["Confidence"].setText(confidence)
        self._fields["Timeframe"].setText(timeframe)
        self._fields["Reason"].setText(reason)
        self._fields["TP"].setText(take_profit)
        self._fields["SL"].setText(stop_loss)
        self._fields["Risk Reward"].setText(risk_reward)
