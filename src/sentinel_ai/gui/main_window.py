"""
MODULE: GUI-004
FILE: GUI-004-001
Module Name: Main Window
Version: 0.3.0
Purpose: Provides the Sentinel AI main shell layout without embedding trading logic.
Dependencies: PySide6.QtCore, PySide6.QtWidgets, sentinel_ai.config.config_schema, sentinel_ai.gui.widgets, sentinel_ai.models.market
Change History:
- 0.1.0: Added approved main GUI layout with toolbar, chart, prediction panel, statistics panel, and status bar.
- 0.3.0: Added GUI-only market feed status update method for validated snapshots.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from sentinel_ai.config.config_schema import SentinelConfig
from sentinel_ai.gui.widgets.chart_panel import ChartPanel
from sentinel_ai.gui.widgets.prediction_panel import PredictionPanel
from sentinel_ai.gui.widgets.statistics_panel import StatisticsPanel
from sentinel_ai.models.market import MarketDataSnapshot


class MainWindow(QMainWindow):
    """Render the Sentinel AI main application window."""

    manual_trade_requested = Signal()
    auto_trade_toggled = Signal(bool)
    settings_requested = Signal()
    timeframe_changed = Signal(str)

    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the main window from validated application configuration."""
        super().__init__()
        self._config = config
        self._chart_panel = ChartPanel()
        self._prediction_panel = PredictionPanel()
        self._statistics_panel = StatisticsPanel()
        self._auto_trade_enabled = False
        self.setWindowTitle(config.application.name)
        self.resize(config.ui.default_width, config.ui.default_height)
        self._build_toolbar()
        self._build_main_layout()
        self._build_status_bar()

    def _build_toolbar(self) -> None:
        """Build the top toolbar required by the blueprint."""
        toolbar = QToolBar("Top Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self._trend_label = QLabel("Trend: WAIT")
        self._probability_label = QLabel("Probability: 0.00%")
        toolbar.addWidget(self._trend_label)
        toolbar.addSeparator()
        toolbar.addWidget(self._probability_label)
        toolbar.addSeparator()

        timeframe_label = QLabel("Timeframe:")
        self._timeframe_combo = QComboBox()
        self._timeframe_combo.addItems(["M1", "M5", "M15", "M30", "H1", "H4", "D1"])
        self._timeframe_combo.setCurrentText(self._config.trading.default_timeframe)
        self._timeframe_combo.currentTextChanged.connect(self.timeframe_changed.emit)
        toolbar.addWidget(timeframe_label)
        toolbar.addWidget(self._timeframe_combo)
        toolbar.addSeparator()

        self._manual_trade_button = QPushButton("Manual Trade")
        self._manual_trade_button.setEnabled(False)
        self._manual_trade_button.clicked.connect(self.manual_trade_requested.emit)
        toolbar.addWidget(self._manual_trade_button)

        self._auto_trade_button = QPushButton("Auto Trade: OFF")
        self._auto_trade_button.setCheckable(True)
        self._auto_trade_button.setEnabled(False)
        self._auto_trade_button.toggled.connect(self._handle_auto_trade_toggled)
        toolbar.addWidget(self._auto_trade_button)

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.settings_requested.emit)
        toolbar.addWidget(settings_button)

    def _build_main_layout(self) -> None:
        """Build the central chart and bottom dashboard layout."""
        central = QWidget()
        outer_layout = QVBoxLayout(central)
        outer_layout.setContentsMargins(14, 14, 14, 14)
        outer_layout.setSpacing(14)

        self._chart_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer_layout.addWidget(self._chart_panel, stretch=8)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(14)
        bottom_layout.addWidget(self._prediction_panel, stretch=1)
        bottom_layout.addWidget(self._statistics_panel, stretch=1)
        outer_layout.addLayout(bottom_layout, stretch=2)

        self.setCentralWidget(central)

    def _build_status_bar(self) -> None:
        """Build the bottom status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Sentinel AI foundation initialized.")

    def _handle_auto_trade_toggled(self, enabled: bool) -> None:
        """Emit an auto-trade toggle request without executing trades in the GUI."""
        self._auto_trade_enabled = enabled
        self._auto_trade_button.setText("Auto Trade: ON" if enabled else "Auto Trade: OFF")
        self.auto_trade_toggled.emit(enabled)

    def update_statistics_panel(self, statistics: dict[str, object], learning_status: str) -> None:
        """Update the statistics dashboard using values supplied by application services."""
        self._statistics_panel.update_statistics(statistics, learning_status)

    def set_service_status(self, message: str) -> None:
        """Show a service-originated message in the status bar and chart status area."""
        self.statusBar().showMessage(message)
        self._chart_panel.set_chart_status(message)

    def update_market_feed_status(self, snapshot: MarketDataSnapshot) -> None:
        """Display validated market feed status without calculating trading signals."""
        self.statusBar().showMessage(
            f"Loaded {snapshot.candle_count} candles for {snapshot.symbol} {snapshot.timeframe}."
        )
        self._chart_panel.set_market_snapshot(snapshot)

    def set_trading_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable trading controls based on trading service availability."""
        self._manual_trade_button.setEnabled(enabled)
        self._auto_trade_button.setEnabled(enabled)
