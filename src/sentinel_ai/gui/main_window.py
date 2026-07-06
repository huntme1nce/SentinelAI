"""
MODULE: GUI-004
FILE: GUI-004-001
Module Name: Main Window
Version: 0.7.0
Purpose: Provides the Sentinel AI main shell layout without embedding trading, symbol-management, market-structure, or analysis logic.
Dependencies: PySide6.QtCore, PySide6.QtWidgets, sentinel_ai.config.config_schema, sentinel_ai.gui.widgets, sentinel_ai.models.market, sentinel_ai.models.market_structure
Change History:
- 0.1.0: Added approved main GUI layout with toolbar, chart, prediction panel, statistics panel, and status bar.
- 0.3.0: Added GUI-only market feed status update method for validated snapshots.
- 0.4.0: Routed validated snapshots to the embedded chart panel without changing layout.
- 0.5.0: Added GUI-only methods for live market snapshot and runtime status updates.
- 0.5.1: Preserved layout while live refresh cadence and chart navigation behavior were patched.
- 0.6.0: Added GUI-only symbol selection controls and symbol status methods.
- 0.7.0: Added GUI-only market structure status rendering and chart marker routing.
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
from sentinel_ai.models.market_structure import MarketStructureSnapshot


class MainWindow(QMainWindow):
    """Render the Sentinel AI main application window."""

    manual_trade_requested = Signal()
    auto_trade_toggled = Signal(bool)
    settings_requested = Signal()
    timeframe_changed = Signal(str)
    symbol_changed = Signal(str)

    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the main window from validated application configuration."""
        super().__init__()
        self._config = config
        self._chart_panel = ChartPanel()
        self._prediction_panel = PredictionPanel()
        self._statistics_panel = StatisticsPanel()
        self._auto_trade_enabled = False
        self._last_emitted_symbol = config.trading.symbol
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

        symbol_label = QLabel("Symbol:")
        self._symbol_combo = QComboBox()
        self._symbol_combo.setEditable(True)
        self._symbol_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._symbol_combo.setMinimumWidth(155)
        self._symbol_combo.setMaxVisibleItems(20)
        self._symbol_combo.addItem(self._config.trading.symbol)
        self._symbol_combo.setCurrentText(self._config.trading.symbol)
        self._symbol_combo.activated.connect(lambda _index: self._emit_symbol_change_request())
        line_edit = self._symbol_combo.lineEdit()
        if line_edit is not None:
            line_edit.editingFinished.connect(self._emit_symbol_change_request)
        toolbar.addWidget(symbol_label)
        toolbar.addWidget(self._symbol_combo)
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


    def _emit_symbol_change_request(self) -> None:
        """Emit a user symbol-change request without validating symbols in the GUI."""
        requested_symbol = self._symbol_combo.currentText().strip()
        if not requested_symbol or requested_symbol == self._last_emitted_symbol:
            return
        self._last_emitted_symbol = requested_symbol
        self.symbol_changed.emit(requested_symbol)

    def _handle_auto_trade_toggled(self, enabled: bool) -> None:
        """Emit an auto-trade toggle request without executing trades in the GUI."""
        self._auto_trade_enabled = enabled
        self._auto_trade_button.setText("Auto Trade: ON" if enabled else "Auto Trade: OFF")
        self.auto_trade_toggled.emit(enabled)


    def set_symbol_options(self, symbols: tuple[str, ...], active_symbol: str) -> None:
        """Display broker symbols supplied by application services without validating them in the GUI."""
        previous_signal_state = self._symbol_combo.blockSignals(True)
        try:
            self._symbol_combo.clear()
            unique_symbols: list[str] = []
            for symbol in symbols:
                clean_symbol = str(symbol).strip()
                if clean_symbol and clean_symbol not in unique_symbols:
                    unique_symbols.append(clean_symbol)
            clean_active_symbol = str(active_symbol).strip()
            if clean_active_symbol and clean_active_symbol not in unique_symbols:
                unique_symbols.insert(0, clean_active_symbol)
            self._symbol_combo.addItems(unique_symbols)
            if clean_active_symbol:
                self._symbol_combo.setCurrentText(clean_active_symbol)
                self._last_emitted_symbol = clean_active_symbol
        finally:
            self._symbol_combo.blockSignals(previous_signal_state)

    def update_active_symbol(self, symbol: str) -> None:
        """Update the displayed active symbol after service-level validation."""
        clean_symbol = str(symbol).strip()
        if not clean_symbol:
            return
        previous_signal_state = self._symbol_combo.blockSignals(True)
        try:
            if self._symbol_combo.findText(clean_symbol) < 0:
                self._symbol_combo.insertItem(0, clean_symbol)
            self._symbol_combo.setCurrentText(clean_symbol)
            self._last_emitted_symbol = clean_symbol
        finally:
            self._symbol_combo.blockSignals(previous_signal_state)

    def update_statistics_panel(self, statistics: dict[str, object], learning_status: str) -> None:
        """Update the statistics dashboard using values supplied by application services."""
        self._statistics_panel.update_statistics(statistics, learning_status)

    def set_service_status(self, message: str) -> None:
        """Show a service-originated message in the status bar and chart status area."""
        self.statusBar().showMessage(message)
        self._chart_panel.set_chart_status(message)

    def update_runtime_status(self, message: str) -> None:
        """Show a runtime status message without replacing chart candle rendering."""
        self.statusBar().showMessage(message)

    def update_market_feed_status(self, snapshot: MarketDataSnapshot) -> None:
        """Display validated market feed status without calculating trading signals."""
        self.statusBar().showMessage(
            f"Loaded {snapshot.candle_count} candles for {snapshot.symbol} {snapshot.timeframe}."
        )
        self._chart_panel.set_market_snapshot(snapshot)

    def update_live_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        """Display a live refreshed market snapshot without calculating trading signals."""
        latest = snapshot.latest_candle
        if latest is None:
            self.statusBar().showMessage(f"Live update received for {snapshot.symbol} {snapshot.timeframe}: no candles.")
        else:
            self.statusBar().showMessage(
                f"Live update: {snapshot.symbol} {snapshot.timeframe} close {latest.close:.2f}."
            )
        self._chart_panel.set_market_snapshot(snapshot)

    def update_market_structure_status(self, structure_snapshot: MarketStructureSnapshot) -> None:
        """Display market structure context supplied by analysis services without computing it in the GUI."""
        self._trend_label.setText(f"Trend: {structure_snapshot.bias}")
        self._probability_label.setText("Probability: 0.00%")
        self._prediction_panel.update_prediction(
            direction="WAIT",
            confidence="Pending",
            timeframe=structure_snapshot.timeframe,
            reason=structure_snapshot.summary,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )
        self._chart_panel.set_market_structure_snapshot(structure_snapshot, self._config.market_structure.max_chart_markers)

    def set_trading_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable trading controls based on trading service availability."""
        self._manual_trade_button.setEnabled(enabled)
        self._auto_trade_button.setEnabled(enabled)
