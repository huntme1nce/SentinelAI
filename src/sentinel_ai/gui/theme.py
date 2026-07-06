"""
MODULE: GUI-001
FILE: GUI-001-001
Module Name: Theme Service
Version: 0.1.0
Purpose: Loads and builds the Sentinel AI Qt stylesheet from packaged theme resources.
Dependencies: json, pathlib, PySide6.QtWidgets, sentinel_ai.core.constants, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added dark neon Qt theme loader.
"""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtWidgets import QApplication

from sentinel_ai.core.constants import DEFAULT_THEME_RESOURCE
from sentinel_ai.utils.paths import resource_path


class ThemeService:
    """Apply packaged visual themes to the Qt application."""

    def __init__(self, theme_resource: str = DEFAULT_THEME_RESOURCE) -> None:
        """Initialize the theme service with a packaged theme resource path."""
        self._theme_resource = theme_resource

    def apply(self, application: QApplication) -> None:
        """Apply the configured Qt stylesheet to the QApplication instance."""
        theme = self._load_theme()
        application.setStyleSheet(self._build_stylesheet(theme))

    def _load_theme(self) -> dict[str, Any]:
        """Load a theme JSON file from packaged application resources."""
        path = resource_path(self._theme_resource)
        with path.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        if not isinstance(data, dict):
            raise ValueError(f"Theme file must contain a JSON object: {path}")
        return data

    @staticmethod
    def _build_stylesheet(theme: dict[str, Any]) -> str:
        """Build a Qt stylesheet from validated theme values."""
        background = str(theme["background"])
        surface = str(theme["surface"])
        elevated = str(theme["elevated"])
        text = str(theme["text"])
        muted_text = str(theme["muted_text"])
        accent = str(theme["accent"])
        border = str(theme["border"])
        danger = str(theme["danger"])

        return f"""
        QWidget {{
            background-color: {background};
            color: {text};
            font-family: Segoe UI;
            font-size: 10pt;
        }}
        QMainWindow, QDialog {{
            background-color: {background};
        }}
        QLabel#TitleLabel {{
            font-size: 24pt;
            font-weight: 700;
            color: {accent};
        }}
        QLabel#VerseLabel {{
            font-size: 13pt;
            line-height: 150%;
            color: {text};
        }}
        QLabel#MutedLabel {{
            color: {muted_text};
        }}
        QFrame#Panel {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 10px;
        }}
        QFrame#ChartPanel {{
            background-color: {elevated};
            border: 1px solid {border};
            border-radius: 12px;
        }}
        QPushButton {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 8px 14px;
            color: {text};
        }}
        QPushButton:hover {{
            border-color: {accent};
        }}
        QPushButton:pressed {{
            background-color: {elevated};
        }}
        QPushButton:disabled {{
            color: {muted_text};
            border-color: {border};
        }}
        QPushButton#PrimaryButton {{
            background-color: {accent};
            color: #081014;
            font-weight: 700;
        }}
        QPushButton#DangerButton {{
            border-color: {danger};
            color: {danger};
        }}
        QStatusBar {{
            background-color: {surface};
            color: {muted_text};
        }}
        QToolBar {{
            background-color: {surface};
            border-bottom: 1px solid {border};
            spacing: 8px;
        }}
        QComboBox {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 5px;
        }}
        """
