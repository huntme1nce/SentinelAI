"""
MODULE: GUI-002
FILE: GUI-002-001
Module Name: Welcome Window
Version: 0.1.0
Purpose: Displays the required Sentinel AI startup verse and manual entry gate.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 0.1.0: Added manual welcome gate with Proverbs 13:11 and consistency message.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WelcomeWindow(QDialog):
    """Display the non-automatic Sentinel AI welcome window."""

    entered = Signal()

    def __init__(self) -> None:
        """Initialize the welcome window UI."""
        super().__init__()
        self.setWindowTitle("Sentinel AI")
        self.setModal(True)
        self.setMinimumSize(620, 420)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the required startup content and manual entry button."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(22)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Sentinel AI")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        verse = QLabel(
            "Proverbs 13:11\n\n"
            "\"Wealth gained hastily will dwindle,\n"
            "but whoever gathers little by little increases it.\""
        )
        verse.setObjectName("VerseLabel")
        verse.setAlignment(Qt.AlignCenter)
        verse.setWordWrap(True)
        layout.addWidget(verse)

        message = QLabel(
            "Don't be obsessed with fast money.\n"
            "Be obsessed with consistency."
        )
        message.setObjectName("MutedLabel")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)

        enter_button = QPushButton("Enter Sentinel AI")
        enter_button.setObjectName("PrimaryButton")
        enter_button.clicked.connect(self._enter_application)
        layout.addWidget(enter_button, alignment=Qt.AlignCenter)

    def _enter_application(self) -> None:
        """Emit the entered signal and close the welcome window."""
        self.entered.emit()
        self.accept()
