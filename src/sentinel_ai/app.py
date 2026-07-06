"""
MODULE: APP-001
FILE: APP-001-001
Module Name: Qt Application Bootstrapper
Version: 0.1.0
Purpose: Starts Sentinel AI with configured services, theme, welcome gate, and main window.
Dependencies: sys, PySide6.QtWidgets, sentinel_ai.gui, sentinel_ai.services
Change History:
- 0.1.0: Added production startup flow with mandatory manual welcome window.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from sentinel_ai.gui.main_window import MainWindow
from sentinel_ai.gui.theme import ThemeService
from sentinel_ai.gui.welcome_window import WelcomeWindow
from sentinel_ai.services.app_context import ApplicationContextFactory


class SentinelApplication:
    """Coordinate Qt startup without embedding domain trading logic."""

    def __init__(self) -> None:
        """Initialize the Qt application and composed services."""
        self._qt_application = QApplication(sys.argv)
        self._context = ApplicationContextFactory().build()
        ThemeService().apply(self._qt_application)
        self._main_window = MainWindow(self._context.config)
        self._connect_main_window_signals()
        self._refresh_dashboard_statistics()

    def run(self) -> int:
        """Run the welcome gate and start the Qt event loop."""
        if self._context.config.ui.welcome_required:
            welcome = WelcomeWindow()
            result = welcome.exec()
            if result != QDialog.DialogCode.Accepted:
                self._context.logger.info("Application startup cancelled at welcome window.")
                return 0

        self._main_window.show()
        self._context.logger.info("Sentinel AI main window displayed.")
        return self._qt_application.exec()

    def _connect_main_window_signals(self) -> None:
        """Connect GUI request signals to safe application-level handlers."""
        self._main_window.settings_requested.connect(self._show_settings_information)
        self._main_window.timeframe_changed.connect(self._handle_timeframe_changed)

    def _refresh_dashboard_statistics(self) -> None:
        """Refresh dashboard statistics from the prediction repository."""
        statistics = self._context.prediction_repository.summary_statistics()
        self._main_window.update_statistics_panel(statistics, "Statistical review pending sufficient closed trades")
        self._main_window.set_service_status("Sentinel AI foundation initialized. Trading service not connected.")

    def _show_settings_information(self) -> None:
        """Display the active configuration and data paths without changing settings."""
        QMessageBox.information(
            self._main_window,
            "Sentinel AI Settings",
            "Configuration and database are initialized.\n\n"
            f"Database:\n{self._context.database_service.database_path}",
        )

    def _handle_timeframe_changed(self, timeframe: str) -> None:
        """Record the selected timeframe without triggering analysis inside the GUI."""
        self._context.logger.info("Timeframe selected: %s", timeframe)
        self._main_window.set_service_status(f"Selected timeframe: {timeframe}")


def run_application() -> int:
    """Create and execute the Sentinel AI application."""
    application = SentinelApplication()
    return application.run()
