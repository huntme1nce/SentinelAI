"""
MODULE: APP-001
FILE: APP-001-001
Module Name: Qt Application Bootstrapper
Version: 0.5.0
Purpose: Starts Sentinel AI with configured services, theme, welcome gate, MT5 status, market feed, chart rendering, refresh loop, and main window.
Dependencies: sys, PySide6.QtWidgets, sentinel_ai.gui, sentinel_ai.market_data, sentinel_ai.models, sentinel_ai.services
Change History:
- 0.1.0: Added production startup flow with mandatory manual welcome window.
- 0.2.0: Added MT5 connection initialization and safe market status reporting without trading execution.
- 0.3.0: Added validated market data feed loading without prediction or trade execution logic.
- 0.4.0: Preserved startup flow while chart panel renders live validated candles.
- 0.5.0: Added service-driven live market refresh without adding prediction or trade execution logic.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from sentinel_ai.gui.main_window import MainWindow
from sentinel_ai.gui.theme import ThemeService
from sentinel_ai.gui.welcome_window import WelcomeWindow
from sentinel_ai.market_data.candle_validator import CandleDataValidationError
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.mt5.exceptions import Mt5ServiceError
from sentinel_ai.services.app_context import ApplicationContextFactory


class SentinelApplication:
    """Coordinate Qt startup without embedding domain trading logic."""

    def __init__(self) -> None:
        """Initialize the Qt application and composed services."""
        self._qt_application = QApplication(sys.argv)
        self._context = ApplicationContextFactory().build()
        ThemeService().apply(self._qt_application)
        self._main_window = MainWindow(self._context.config)
        self._active_timeframe = self._context.config.trading.default_timeframe
        self._connect_main_window_signals()
        self._connect_market_refresh_signals()
        self._initialize_mt5_connection()
        self._refresh_dashboard_statistics()

    def run(self) -> int:
        """Run the welcome gate and start the Qt event loop."""
        if self._context.config.ui.welcome_required:
            welcome = WelcomeWindow()
            result = welcome.exec()
            if result != QDialog.DialogCode.Accepted:
                self._context.logger.info("Application startup cancelled at welcome window.")
                self._shutdown_services()
                return 0

        self._main_window.show()
        self._start_market_refresh_if_ready(self._active_timeframe)
        self._context.logger.info("Sentinel AI main window displayed.")
        exit_code = self._qt_application.exec()
        self._shutdown_services()
        return exit_code

    def _connect_main_window_signals(self) -> None:
        """Connect GUI request signals to safe application-level handlers."""
        self._main_window.settings_requested.connect(self._show_settings_information)
        self._main_window.timeframe_changed.connect(self._handle_timeframe_changed)

    def _connect_market_refresh_signals(self) -> None:
        """Connect market refresh service events to application-level GUI updates."""
        self._context.market_refresh_service.snapshot_refreshed.connect(self._handle_market_snapshot_refreshed)
        self._context.market_refresh_service.refresh_failed.connect(self._handle_market_refresh_failed)
        self._context.market_refresh_service.refresh_status_changed.connect(self._handle_market_refresh_status_changed)

    def _initialize_mt5_connection(self) -> None:
        """Initialize MT5 read-only connectivity when enabled by configuration."""
        if not self._context.config.mt5.startup_connect:
            self._main_window.set_service_status("MT5 startup connection is disabled in configuration.")
            return

        status = self._context.mt5_service.connect()
        if not status.connected:
            self._main_window.set_service_status(status.message)
            return

        symbol_status = self._context.mt5_service.validate_symbol(self._context.config.trading.symbol)
        message = f"{status.message} Symbol {symbol_status.symbol}: {symbol_status.message}"
        self._main_window.set_service_status(message)
        self._main_window.set_trading_controls_enabled(False)
        if self._context.config.market_data.startup_load:
            self._refresh_market_feed(self._active_timeframe)

    def _refresh_dashboard_statistics(self) -> None:
        """Refresh dashboard statistics from the prediction repository."""
        statistics = self._context.prediction_repository.summary_statistics()
        self._main_window.update_statistics_panel(statistics, "Statistical review pending sufficient closed trades")

    def _refresh_market_feed(self, timeframe: str) -> MarketDataSnapshot | None:
        """Load a validated market data snapshot for the selected timeframe."""
        try:
            snapshot = self._context.market_data_feed_service.load_snapshot(
                symbol=self._context.config.trading.symbol,
                timeframe=timeframe,
                bar_count=self._context.config.market_data.default_feed_bar_count,
            )
            self._main_window.update_market_feed_status(snapshot)
            return snapshot
        except (Mt5ServiceError, CandleDataValidationError, ValueError) as error:
            self._context.logger.warning("Market feed refresh failed: %s", error)
            self._main_window.set_service_status(f"Market feed unavailable for {timeframe}: {error}")
            return None

    def _start_market_refresh_if_ready(self, timeframe: str) -> None:
        """Start the configured market refresh service when the MT5 feed is connected."""
        if not self._context.config.market_data.auto_refresh_enabled:
            self._context.market_refresh_service.stop()
            self._main_window.update_runtime_status("Live market refresh is disabled in configuration.")
            return

        status = self._context.mt5_service.connection_status()
        if not status.connected:
            self._context.market_refresh_service.stop()
            self._main_window.update_runtime_status(f"Live market refresh not started. {status.message}")
            return

        interval_seconds = self._context.config.market_data.refresh_interval_for(timeframe)
        self._context.market_refresh_service.start(
            symbol=self._context.config.trading.symbol,
            timeframe=timeframe,
            bar_count=self._context.config.market_data.default_feed_bar_count,
            interval_seconds=interval_seconds,
        )

    def _show_settings_information(self) -> None:
        """Display the active configuration and data paths without changing settings."""
        status = self._context.mt5_service.connection_status()
        latest_snapshot = self._context.market_data_feed_service.latest_snapshot()
        if latest_snapshot is None:
            feed_status = "No validated market feed snapshot loaded."
        else:
            feed_status = (
                f"{latest_snapshot.symbol} {latest_snapshot.timeframe}: "
                f"{latest_snapshot.candle_count} validated candles loaded."
            )
        refresh_status = "Running" if self._context.market_refresh_service.is_running else "Stopped"
        QMessageBox.information(
            self._main_window,
            "Sentinel AI Settings",
            "Configuration and database are initialized.\n\n"
            f"Database:\n{self._context.database_service.database_path}\n\n"
            f"MT5 Status:\n{status.message}\n\n"
            f"Market Feed:\n{feed_status}\n\n"
            f"Live Refresh:\n{refresh_status}",
        )

    def _handle_timeframe_changed(self, timeframe: str) -> None:
        """Record the selected timeframe and refresh validated market-data availability."""
        self._active_timeframe = timeframe
        self._context.logger.info("Timeframe selected: %s", timeframe)
        status = self._context.mt5_service.connection_status()
        if not status.connected:
            self._context.market_refresh_service.stop()
            self._main_window.set_service_status(f"Selected timeframe: {timeframe}. {status.message}")
            return
        if self._refresh_market_feed(timeframe) is not None:
            self._start_market_refresh_if_ready(timeframe)

    def _handle_market_snapshot_refreshed(self, snapshot: object) -> None:
        """Update the chart from a validated market refresh event."""
        if not isinstance(snapshot, MarketDataSnapshot):
            self._context.logger.warning("Ignored unexpected market refresh payload: %r", type(snapshot))
            return
        if snapshot.timeframe != self._active_timeframe:
            self._context.logger.info(
                "Ignored stale refresh snapshot for %s while active timeframe is %s.",
                snapshot.timeframe,
                self._active_timeframe,
            )
            return
        self._main_window.update_live_market_snapshot(snapshot)

    def _handle_market_refresh_failed(self, message: str) -> None:
        """Display a non-destructive refresh failure status."""
        self._main_window.update_runtime_status(message)

    def _handle_market_refresh_status_changed(self, message: str) -> None:
        """Display non-destructive live refresh status updates."""
        self._main_window.update_runtime_status(message)

    def _shutdown_services(self) -> None:
        """Stop timed services and disconnect external market data resources."""
        self._context.market_refresh_service.stop()
        self._context.mt5_service.disconnect()


def run_application() -> int:
    """Create and execute the Sentinel AI application."""
    application = SentinelApplication()
    return application.run()
