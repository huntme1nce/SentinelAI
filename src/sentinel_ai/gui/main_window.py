"""
MODULE: GUI-004
FILE: GUI-004-001
Module Name: Main Window
Version: 2.17.0
Purpose: Provides the Sentinel AI main shell layout without embedding trading, symbol-management, market-structure, analysis, Auto Trade diagnostics, trade-lifecycle, result-settlement, or trade-risk decision logic.
Dependencies: PySide6.QtCore, PySide6.QtWidgets, sentinel_ai.config.config_schema, sentinel_ai.gui.widgets, sentinel_ai.models
Change History:
- 2.17.0: Added display-only Profit Lock preview routing for future SL protection stages.
- 2.15.0: Routed display-only TP progress, SL risk, and route-state values into active-trade panels.
- 2.14.0: Added display-only active-trade risk alert routing for TP approach and SL danger visibility.
- 2.13.0: Added display-only active-trade pressure routing for open Sentinel trades.
- 2.12.0: Routed current price, TP/SL distance, and nearest-target progress into Active Trade panel state.
- 2.11.0: Routed verified closed Sentinel trade results to a dedicated Trade Result panel state.
- 2.10.0: Preserved active-trade routing for the summary-card panel refinement.
- 2.9.0: Routed open-position display to active-trade panel mode for clearer GUI state separation.
- 2.8.0: Preserved GUI shell while statistics panel now displays learning-readiness fields.
- 2.6.0: Routed Auto Trade diagnostics to the statistics dashboard.
- 2.5.0: Added explicit Auto Trade locked-state UI guard for manual-mode stabilization.
- 2.4.0: Enabled guarded Auto Trade control and added programmatic auto-trade state updates.
- 2.3.0: Preserved Ledger Tools toolbar routing for pending history repair.
- 2.2.0: Preserved statistics routing while main dashboard hides backend-only diagnostics.
- 2.1.0: Added Ledger Tools toolbar action for maintenance, export, archive, and reset workflows.
- 2.0.1: Preserved backlog/stale routing while pending-close count is limited to current settlement trades.
- 2.0.0: Routed final stabilization fields to dashboard.
- 1.9.0.2: Preserved resolver dashboard routing for app helper binding hotfix.
- 1.9.0.1: Preserved resolver dashboard routing for MT5 resolver binding hotfix.
- 1.9.0: Routed close resolver and audit diagnostics to statistics dashboard.
- 1.8.4.1: Preserved lifecycle dashboard routing for startup binding hotfix.
- 1.8.4: Routed lifecycle diagnostics to the statistics dashboard.
- 1.8.3: Routed pending close ledger counter to the dashboard.
- 1.8.2: Preserved trade result verification routing for active-ticket close guard.
- 1.8.1: Routed open/closed ledger counters and result status to the dashboard.
- 1.8.0: Displayed persistent Sentinel ledger totals in dashboard statistics.
- 1.7.5: Preserved dashboard routing while statistics use persistent Sentinel trade ledger.
- 1.7.4: Preserved dashboard routing while persistent Sentinel-owned recovery is added.
- 1.7.3: Preserved dashboard routing while statistics are restricted to Sentinel-owned trades.
- 1.7.2: Displayed last close type and history match mode from MT5 history fallback tracking.
- 1.7.1.3: Preserved active position display while fixing live candle-cycle countdown synchronization.
- 1.7.1.2: Preserved active position display while fixing countdown candle-open anchoring.
- 1.7.1.1: Preserved active position display while fixing chart countdown timer.
- 1.7.1: Preserved active position display while chart runtime adds candle countdown timer.
- 1.7.0: Displayed net P/L, last closed result, and lifecycle close status.
- 1.6.2: Displayed active-position missing SL/TP warnings and protection status.
- 1.6.1.2: Displayed missing active-position TP/SL as Not Set instead of 0.00.
- 1.6.1.1: Initialized active-position lock before first market refresh to fix startup AttributeError.
- 1.6.1: Prioritized active position display and locked chart markings to active trade levels.
- 0.1.0: Added approved main GUI layout with toolbar, chart, prediction panel, statistics panel, and status bar.
- 0.3.0: Added GUI-only market feed status update method for validated snapshots.
- 0.4.0: Routed validated snapshots to the embedded chart panel without changing layout.
- 0.5.0: Added GUI-only methods for live market snapshot and runtime status updates.
- 0.5.1: Preserved layout while live refresh cadence and chart navigation behavior were patched.
- 0.6.0: Added GUI-only symbol selection controls and symbol status methods.
- 0.7.0: Added GUI-only market structure status rendering and chart marker routing.
- 0.8.0: Added GUI-only support/resistance status rendering and chart zone routing.
- 0.9.0: Added GUI-only liquidity status rendering and chart overlay routing.
- 0.9.1: Preserved GUI layout while displaying cleaner bounded-overlay analysis summaries.
- 0.9.2: Added GUI-only imbalance overlay routing for FVG and order block boxes.
- 0.9.3.1: Passed structure context to S/R range boxes and shortened live prediction reason text.
- 0.9.3.2: Tightened live reason text further for active-overlay chart mode.
- 0.9.3.3: Replaced verbose live reason chain with concise active-state wording.
- 0.9.3.8: Preserved compact live reason behavior for single-canvas repaint artifact patch.
- 1.0.0: Added GUI-only momentum status rendering for Sprint 10 without changing layout.
- 1.1.1: Preserved GUI-only confidence display for live refresh pipeline patch.
- 1.2.3: Preserved GUI-only setup display for neutral-momentum setup patch.
- 1.3.1: Preserved TP/SL GUI display for smart TP target selection patch.
- 1.3.3: Preserved rejected-plan display for extended TP target discovery patch.
- 1.6.0: Added active position monitoring display and manual-trade lock while a position is open.
- 1.5.1: Preserved manual order UI for adaptive filling-mode fallback patch.
- 1.5.0: Preserved manual order gate for Sprint 15 user-confirmed MT5 execution.
- 1.4.1: Preserved manual review gate enablement for polished review-modal patch.
- 1.4.0: Added trade plan overlay routing and manual review gate enablement for ready states.
- 1.3.2: Added rejected TP/SL display labeling for invalid risk/reward plans.
- 1.3.0: Added GUI-only TP/SL and risk/reward readiness display.
- 1.2.2: Preserved GUI-only setup display for pullback-aware setup patch.
- 1.2.1: Preserved GUI-only setup display for entry reason patch.
- 1.2.0: Added GUI-only entry setup display for BUY_SETUP / SELL_SETUP / WAIT.
- 1.1.0: Added GUI-only confidence status rendering and probability label update for Sprint 11.
- 0.9.3.7: Preserved compact live reason behavior for canvas buffer artifact patch.
- 0.9.3.6: Preserved compact live reason behavior for chart status and flicker patch.
- 0.9.3.5: Preserved compact live reason behavior for true-consolidation chart patch.
- 0.9.3.4: Forced compact dashboard reasons to prevent technical chains from reappearing.
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
from sentinel_ai.models.confidence import ConfidenceSnapshot
from sentinel_ai.models.entry_validation import EntryValidationSnapshot
from sentinel_ai.models.imbalance import ImbalanceSnapshot
from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.momentum import MomentumSnapshot
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot


class MainWindow(QMainWindow):
    manual_trade_requested = Signal()
    auto_trade_toggled = Signal(bool)
    settings_requested = Signal()
    ledger_maintenance_requested = Signal()
    timeframe_changed = Signal(str)
    symbol_changed = Signal(str)

    def __init__(self, config: SentinelConfig) -> None:
        super().__init__()
        self._config = config
        self._chart_panel = ChartPanel()
        self._prediction_panel = PredictionPanel()
        self._statistics_panel = StatisticsPanel()
        self._auto_trade_enabled = False
        self._auto_trade_locked = bool(config.trading.auto_trade_locked)
        self._has_active_position_lock = False
        self._last_emitted_symbol = config.trading.symbol
        self.setWindowTitle(config.application.name)
        self.resize(config.ui.default_width, config.ui.default_height)
        self._build_toolbar()
        self._build_main_layout()
        self._build_status_bar()

    def _build_toolbar(self) -> None:
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

        self._auto_trade_button = QPushButton("Auto Trade: LOCKED" if self._auto_trade_locked else "Auto Trade: OFF")
        self._auto_trade_button.setCheckable(not self._auto_trade_locked)
        self._auto_trade_button.setEnabled(False)
        if self._auto_trade_locked:
            self._auto_trade_button.setToolTip("Auto Trade is locked until enough manual-mode lifecycle results are verified.")
        else:
            self._auto_trade_button.toggled.connect(self._handle_auto_trade_toggled)
        toolbar.addWidget(self._auto_trade_button)

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.settings_requested.emit)
        toolbar.addWidget(settings_button)

        ledger_button = QPushButton("Ledger Tools")
        ledger_button.clicked.connect(self.ledger_maintenance_requested.emit)
        toolbar.addWidget(ledger_button)

    def _build_main_layout(self) -> None:
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
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Sentinel AI foundation initialized.")

    def _emit_symbol_change_request(self) -> None:
        requested_symbol = self._symbol_combo.currentText().strip()
        if not requested_symbol or requested_symbol == self._last_emitted_symbol:
            return
        self._last_emitted_symbol = requested_symbol
        self.symbol_changed.emit(requested_symbol)

    def _handle_auto_trade_toggled(self, enabled: bool) -> None:
        self._auto_trade_enabled = enabled
        self._auto_trade_button.setText("Auto Trade: ON" if enabled else "Auto Trade: OFF")
        self.auto_trade_toggled.emit(enabled)

    def set_symbol_options(self, symbols: tuple[str, ...], active_symbol: str) -> None:
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
        self._statistics_panel.update_statistics(statistics, learning_status)

    def update_auto_trade_diagnostics(self, status: str, reason: str) -> None:
        """Display Auto Trade readiness diagnostics without owning execution logic."""
        self._statistics_panel.update_auto_trade_diagnostics(status, reason)

    def set_service_status(self, message: str) -> None:
        self.statusBar().showMessage(message)
        self._chart_panel.set_chart_status(message)

    def update_runtime_status(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def update_market_feed_status(self, snapshot: MarketDataSnapshot) -> None:
        self.statusBar().showMessage(f"Loaded {snapshot.candle_count} candles for {snapshot.symbol} {snapshot.timeframe}.")
        self._chart_panel.set_market_snapshot(snapshot)

    def update_live_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        latest = snapshot.latest_candle
        if latest is None:
            self.statusBar().showMessage(f"Live update received for {snapshot.symbol} {snapshot.timeframe}: no candles.")
        else:
            self.statusBar().showMessage(f"Live update: {snapshot.symbol} {snapshot.timeframe} close {latest.close:.2f}.")
        self._chart_panel.set_market_snapshot(snapshot)

    def update_market_structure_status(self, structure_snapshot: MarketStructureSnapshot) -> None:
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
        self._chart_panel.set_market_structure_snapshot(
            structure_snapshot,
            self._config.market_structure.max_chart_markers,
            self._config.market_structure.max_bos_markers,
        )

    def update_support_resistance_status(
        self,
        support_resistance_snapshot: SupportResistanceSnapshot,
        structure_summary: str,
        structure_snapshot: MarketStructureSnapshot | None = None,
    ) -> None:
        reason = self._build_live_reason(structure_summary, "WAIT")
        self._prediction_panel.update_prediction(
            direction="WAIT",
            confidence="Pending",
            timeframe=support_resistance_snapshot.timeframe,
            reason=reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )
        self._chart_panel.set_support_resistance_snapshot(
            support_resistance_snapshot,
            self._config.support_resistance.max_chart_zones,
            structure_snapshot,
        )

    def update_liquidity_status(self, liquidity_snapshot: LiquiditySnapshot, base_reason: str) -> None:
        reason = self._build_live_reason(base_reason, "Liquidity active")
        self._prediction_panel.update_prediction(
            direction="WAIT",
            confidence="Pending",
            timeframe=liquidity_snapshot.timeframe,
            reason=reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )
        self._chart_panel.set_liquidity_snapshot(
            liquidity_snapshot,
            self._config.liquidity.max_chart_pools,
            self._config.liquidity.max_chart_sweeps,
        )

    def update_imbalance_status(self, imbalance_snapshot: ImbalanceSnapshot, base_reason: str) -> None:
        reason = self._build_imbalance_reason(imbalance_snapshot, base_reason)
        self._prediction_panel.update_prediction(
            direction="WAIT",
            confidence="Pending",
            timeframe=imbalance_snapshot.timeframe,
            reason=reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )
        self._chart_panel.set_imbalance_snapshot(
            imbalance_snapshot,
            self._config.imbalance.max_chart_fvg_zones,
            self._config.imbalance.max_chart_order_blocks,
        )

    @staticmethod
    def _build_live_reason(source_reason: str, active_state: str) -> str:
        """Return a short live-dashboard reason while detailed context remains on the chart."""
        bias = MainWindow._extract_bias(source_reason)
        if active_state == "WAIT":
            return f"{bias} | WAIT"
        return f"{bias} | {active_state} | WAIT"

    @staticmethod
    def _build_imbalance_reason(imbalance_snapshot: ImbalanceSnapshot, base_reason: str) -> str:
        """Return concise FVG/OB state without restoring the full technical reason chain."""
        has_active_fvg = any(not zone.filled for zone in imbalance_snapshot.fair_value_gaps)
        has_active_order_block = any(not zone.invalidated and not zone.mitigated for zone in imbalance_snapshot.order_blocks)
        if has_active_fvg or has_active_order_block:
            return MainWindow._build_live_reason(base_reason, "FVG/OB active")
        return MainWindow._build_live_reason(base_reason, "WAIT")

    @staticmethod
    def _extract_bias(reason: str) -> str:
        """Extract the structure bias token from a longer technical reason."""
        clean_reason = " ".join(str(reason).split()).strip()
        if not clean_reason:
            return "WAIT"
        first_segment = clean_reason.split("|", 1)[0].split(";", 1)[0].strip()
        return first_segment if first_segment else "WAIT"

    def update_momentum_status(self, momentum_snapshot: MomentumSnapshot, base_reason: str) -> None:
        """Display read-only momentum context without changing trade controls or chart layout."""
        reason = self._build_momentum_reason(momentum_snapshot, base_reason)
        self._prediction_panel.update_prediction(
            direction="WAIT",
            confidence="Pending",
            timeframe=momentum_snapshot.timeframe,
            reason=reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )

    @staticmethod
    def _build_momentum_reason(momentum_snapshot: MomentumSnapshot, base_reason: str) -> str:
        """Return concise momentum state without restoring the full technical reason chain."""
        bias = MainWindow._extract_bias(base_reason)
        if momentum_snapshot.bias in {"BULLISH", "LEAN_BULLISH"}:
            return f"{bias} | Momentum bullish | WAIT"
        if momentum_snapshot.bias in {"BEARISH", "LEAN_BEARISH"}:
            return f"{bias} | Momentum bearish | WAIT"
        if momentum_snapshot.bias == "INSUFFICIENT_DATA":
            return f"{bias} | Momentum pending | WAIT"
        return f"{bias} | Momentum neutral | WAIT"

    def update_confidence_status(self, confidence_snapshot: ConfidenceSnapshot) -> None:
        """Display read-only confidence context without enabling trade controls."""
        self._probability_label.setText(f"Probability: {confidence_snapshot.score_percentage:.2f}%")
        self._prediction_panel.update_prediction(
            direction=confidence_snapshot.direction,
            confidence=f"{confidence_snapshot.score_percentage:.2f}%",
            timeframe=confidence_snapshot.timeframe,
            reason=confidence_snapshot.reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )

    def update_entry_validation_status(self, entry_snapshot: EntryValidationSnapshot) -> None:
        """Display setup-only entry validation without enabling trade controls."""
        self._prediction_panel.update_prediction(
            direction=entry_snapshot.direction,
            confidence=f"{entry_snapshot.confidence_percentage:.2f}%",
            timeframe=entry_snapshot.timeframe,
            reason=entry_snapshot.reason,
            take_profit="-",
            stop_loss="-",
            risk_reward="-",
        )

    def update_risk_reward_status(self, risk_reward_snapshot: RiskRewardSnapshot) -> None:
        """Display TP/SL and risk/reward validation without enabling auto execution."""
        if self._has_active_position_lock:
            self.set_manual_trade_review_enabled(False)
            return
        plan = risk_reward_snapshot.plan
        is_ready = risk_reward_snapshot.direction in {"BUY_READY", "SELL_READY"} and plan is not None and plan.valid
        if risk_reward_snapshot.direction == "WAIT" and plan is not None and not plan.valid:
            take_profit = "Rejected"
            stop_loss = "Rejected"
            risk_reward = f"{plan.risk_reward_ratio:.2f} rejected" if plan.risk_reward_ratio > 0 else "Rejected"
        else:
            take_profit = "-" if plan is None or plan.take_profit == plan.entry_price else f"{plan.take_profit:.2f}"
            stop_loss = "-" if plan is None else f"{plan.stop_loss:.2f}"
            risk_reward = "-" if plan is None or plan.risk_reward_ratio <= 0 else f"{plan.risk_reward_ratio:.2f}"
        self._prediction_panel.update_prediction(
            direction=risk_reward_snapshot.direction,
            confidence=f"{risk_reward_snapshot.confidence_percentage:.2f}%",
            timeframe=risk_reward_snapshot.timeframe,
            reason=risk_reward_snapshot.reason,
            take_profit=take_profit,
            stop_loss=stop_loss,
            risk_reward=risk_reward,
        )
        self._chart_panel.set_trade_plan_snapshot(risk_reward_snapshot)
        self.set_manual_trade_review_enabled(is_ready and not self._has_active_position_lock)


    def update_position_monitor_status(
        self,
        position_snapshot: PositionMonitorSnapshot,
        daily_statistics_snapshot: DailyTradeStatisticsSnapshot | None = None,
        learning_statistics: dict[str, object] | None = None,
    ) -> None:
        """Display active position monitoring and lock manual trade while a position is open."""
        self._has_active_position_lock = bool(position_snapshot.has_open_position)
        if position_snapshot.has_open_position:
            active_position = (
                f"{position_snapshot.direction} {position_snapshot.volume:.2f} "
                f"@ {position_snapshot.open_price:.2f}"
                if position_snapshot.open_price is not None
                else f"{position_snapshot.direction} {position_snapshot.volume:.2f}"
            )
            open_pl = f"{position_snapshot.profit:.2f}"
            ticket = str(position_snapshot.ticket or "-")
            protection_status = position_snapshot.protection_status
            learning_status = position_snapshot.message
            self.set_manual_trade_review_enabled(False)
            self.statusBar().showMessage(position_snapshot.message)
            active_trade_progress = self._build_active_trade_progress(position_snapshot)
            trade_pressure = active_trade_progress["trade_pressure"]
            risk_alert = active_trade_progress["risk_alert"]
            take_profit_progress = active_trade_progress["take_profit_progress"]
            stop_loss_risk = active_trade_progress["stop_loss_risk"]
            route_state = active_trade_progress["route_state"]
            trade_health = active_trade_progress["trade_health"]
            profit_lock_state = active_trade_progress["profit_lock_state"]
            next_lock_trigger = active_trade_progress["next_lock_trigger"]
            suggested_lock_sl = active_trade_progress["suggested_lock_sl"]
            suggested_lock_progress = active_trade_progress["suggested_lock_progress"]
            self._prediction_panel.update_active_trade(
                direction=f"{position_snapshot.direction} POSITION",
                status="Position Open",
                timeframe=self._config.trading.default_timeframe,
                reason=position_snapshot.protection_status + " | " + position_snapshot.message,
                take_profit="Not Set" if position_snapshot.take_profit is None else f"{position_snapshot.take_profit:.2f}",
                stop_loss="Not Set" if position_snapshot.stop_loss is None else f"{position_snapshot.stop_loss:.2f}",
                open_profit_loss=f"Open P/L {position_snapshot.profit:.2f}",
                current_price=active_trade_progress["current_price"],
                distance_to_take_profit=active_trade_progress["distance_to_take_profit"],
                distance_to_stop_loss=active_trade_progress["distance_to_stop_loss"],
                closer_target=active_trade_progress["closer_target"],
                trade_pressure=active_trade_progress["trade_pressure"],
                risk_alert=active_trade_progress["risk_alert"],
                take_profit_progress=active_trade_progress["take_profit_progress"],
                stop_loss_risk=active_trade_progress["stop_loss_risk"],
                route_state=active_trade_progress["route_state"],
                trade_health=active_trade_progress["trade_health"],
                profit_lock_state=active_trade_progress["profit_lock_state"],
                next_lock_trigger=active_trade_progress["next_lock_trigger"],
                suggested_lock_sl=active_trade_progress["suggested_lock_sl"],
                suggested_lock_progress=active_trade_progress["suggested_lock_progress"],
            )
            self._chart_panel.set_active_position_snapshot(position_snapshot)
        else:
            active_position = "None"
            open_pl = "0.00"
            ticket = "-"
            protection_status = "No active position"
            trade_pressure = "None"
            risk_alert = "None"
            take_profit_progress = "-"
            stop_loss_risk = "-"
            route_state = "NO_TRADE"
            trade_health = "NO_TRADE"
            profit_lock_state = "NO_TRADE"
            next_lock_trigger = "-"
            suggested_lock_sl = "-"
            suggested_lock_progress = "-"
            learning_status = position_snapshot.message
            self._chart_panel.set_active_position_snapshot(position_snapshot)

        if daily_statistics_snapshot is not None:
            last_result = "-"
            last_profit = "-"
            if daily_statistics_snapshot.last_closed_result != "NONE":
                last_profit = (
                    f"{daily_statistics_snapshot.last_closed_profit:.2f}"
                    if daily_statistics_snapshot.last_closed_profit is not None
                    else "-"
                )
                last_result = f"{daily_statistics_snapshot.last_closed_result} {last_profit}"
            statistics = {
                "win_rate": daily_statistics_snapshot.win_rate,
                "loss_rate": daily_statistics_snapshot.loss_rate,
                "average_confidence": 0.0,
                "todays_trades": daily_statistics_snapshot.total_closed_trades,
                "net_profit": daily_statistics_snapshot.net_profit,
                "ledger_total_trades": daily_statistics_snapshot.ledger_total_trades,
                "ledger_open_trades": daily_statistics_snapshot.ledger_open_trades,
                "ledger_pending_close_trades": daily_statistics_snapshot.ledger_pending_close_trades,
                "ledger_closed_trades": daily_statistics_snapshot.ledger_closed_trades,
                "ledger_total_records": daily_statistics_snapshot.ledger_total_records,
                "ledger_win_rate": daily_statistics_snapshot.ledger_win_rate,
                "ledger_net_profit": daily_statistics_snapshot.ledger_net_profit,
                "result_status": daily_statistics_snapshot.result_status or daily_statistics_snapshot.message,
                "lifecycle_stage": daily_statistics_snapshot.lifecycle_stage or "-",
                "tracked_sentinel_ticket": daily_statistics_snapshot.tracked_sentinel_ticket or "-",
                "pending_close_age_seconds": daily_statistics_snapshot.pending_close_age_seconds,
                "close_resolver_status": daily_statistics_snapshot.close_resolver_status or "-",
                "audit_warning": daily_statistics_snapshot.audit_warning or "-",
                "pending_backlog_trades": daily_statistics_snapshot.pending_backlog_trades,
                "stale_pending_trades": daily_statistics_snapshot.stale_pending_trades,
                "ledger_health": daily_statistics_snapshot.ledger_health or "-",
                "build_stage": daily_statistics_snapshot.build_stage or "-",
                "completion_status": daily_statistics_snapshot.completion_status or "-",
                "last_result": last_result,
                "last_close_type": daily_statistics_snapshot.last_close_type or "-",
                "history_match": daily_statistics_snapshot.history_match_mode or "-",
                "last_closed_ticket": daily_statistics_snapshot.last_closed_ticket or "-",
            }
            if learning_statistics:
                statistics.update(learning_statistics)
            self._statistics_panel.update_statistics(statistics, daily_statistics_snapshot.message)
            if not position_snapshot.has_open_position:
                learning_status = daily_statistics_snapshot.message
                if daily_statistics_snapshot.last_closed_result != "NONE":
                    closed_at = (
                        daily_statistics_snapshot.last_closed_at.strftime("%Y-%m-%d %H:%M")
                        if daily_statistics_snapshot.last_closed_at is not None
                        else "-"
                    )
                    close_type = daily_statistics_snapshot.last_close_type or "Close verified"
                    result_reason = daily_statistics_snapshot.result_status or daily_statistics_snapshot.message
                    self._prediction_panel.update_trade_result(
                        result=daily_statistics_snapshot.last_closed_result,
                        close_type=close_type,
                        timeframe=self._config.trading.default_timeframe,
                        reason=result_reason,
                        profit_loss=f"P/L {last_profit}",
                        ticket=str(daily_statistics_snapshot.last_closed_ticket or "-"),
                        closed_at=closed_at,
                    )

        self._statistics_panel.update_position_monitor(
            active_position=active_position,
            open_profit_loss=open_pl,
            ticket=ticket,
            protection_status=protection_status,
            learning_status=learning_status,
            trade_pressure=trade_pressure,
            risk_alert=risk_alert,
            take_profit_progress=take_profit_progress,
            stop_loss_risk=stop_loss_risk,
            route_state=route_state,
            trade_health=trade_health,
            profit_lock_state=profit_lock_state,
            next_lock_trigger=next_lock_trigger,
            suggested_lock_sl=suggested_lock_sl,
            suggested_lock_progress=suggested_lock_progress,
        )

    @staticmethod
    def _build_active_trade_progress(position_snapshot: PositionMonitorSnapshot) -> dict[str, str]:
        """Build display-only active-trade progress values from an open position snapshot."""
        current_price = position_snapshot.current_price
        if current_price is None:
            return {
                "current_price": "-",
                "distance_to_take_profit": "-",
                "distance_to_stop_loss": "-",
                "closer_target": "UNKNOWN",
                "trade_pressure": "UNKNOWN",
                "risk_alert": "UNKNOWN_RISK",
                "take_profit_progress": "-",
                "stop_loss_risk": "-",
                "route_state": "UNKNOWN_ROUTE",
                "trade_health": "UNKNOWN_HEALTH",
                "profit_lock_state": "UNKNOWN_LOCK",
                "next_lock_trigger": "-",
                "suggested_lock_sl": "-",
                "suggested_lock_progress": "-",
            }

        distance_to_take_profit = MainWindow._format_price_distance(current_price, position_snapshot.take_profit)
        distance_to_stop_loss = MainWindow._format_price_distance(current_price, position_snapshot.stop_loss)
        closer_target = MainWindow._resolve_closer_trade_target(
            current_price=current_price,
            take_profit=position_snapshot.take_profit,
            stop_loss=position_snapshot.stop_loss,
        )
        trade_pressure = MainWindow._resolve_trade_pressure(closer_target)
        risk_alert = MainWindow._resolve_trade_risk_alert(
            current_price=current_price,
            take_profit=position_snapshot.take_profit,
            stop_loss=position_snapshot.stop_loss,
            closer_target=closer_target,
        )
        progress_ratio = MainWindow._build_active_trade_progress_ratio(position_snapshot)
        trade_health = MainWindow._resolve_trade_health(
            route_state=progress_ratio["route_state"],
            risk_alert=risk_alert,
            trade_pressure=trade_pressure,
            take_profit_progress=progress_ratio["take_profit_progress"],
            stop_loss_risk=progress_ratio["stop_loss_risk"],
        )
        profit_lock_preview = MainWindow._build_profit_lock_preview(position_snapshot, progress_ratio["take_profit_progress"])
        return {
            "current_price": f"{current_price:.2f}",
            "distance_to_take_profit": distance_to_take_profit,
            "distance_to_stop_loss": distance_to_stop_loss,
            "closer_target": closer_target,
            "trade_pressure": trade_pressure,
            "risk_alert": risk_alert,
            "take_profit_progress": progress_ratio["take_profit_progress"],
            "stop_loss_risk": progress_ratio["stop_loss_risk"],
            "route_state": progress_ratio["route_state"],
            "trade_health": trade_health,
            "profit_lock_state": profit_lock_preview["profit_lock_state"],
            "next_lock_trigger": profit_lock_preview["next_lock_trigger"],
            "suggested_lock_sl": profit_lock_preview["suggested_lock_sl"],
            "suggested_lock_progress": profit_lock_preview["suggested_lock_progress"],
        }

    @staticmethod
    def _format_price_distance(current_price: float | None, target_price: float | None) -> str:
        """Return an absolute price-distance label for display-only trade progress."""
        if current_price is None or target_price is None:
            return "Not Set"
        return f"{abs(target_price - current_price):.2f}"

    @staticmethod
    def _resolve_closer_trade_target(
        current_price: float | None,
        take_profit: float | None,
        stop_loss: float | None,
    ) -> str:
        """Return whether the current price is closer to TP, SL, both, or unknown."""
        if current_price is None or (take_profit is None and stop_loss is None):
            return "UNKNOWN"
        if take_profit is None:
            return "SL"
        if stop_loss is None:
            return "TP"
        distance_to_take_profit = abs(take_profit - current_price)
        distance_to_stop_loss = abs(stop_loss - current_price)
        if abs(distance_to_take_profit - distance_to_stop_loss) < 1e-9:
            return "EQUAL"
        return "TP" if distance_to_take_profit < distance_to_stop_loss else "SL"

    @staticmethod
    def _resolve_trade_pressure(closer_target: str) -> str:
        """Return a display-only pressure state derived from the nearest open-trade target."""
        normalized_target = str(closer_target).upper().strip()
        if normalized_target == "TP":
            return "TP_PRESSURE"
        if normalized_target == "SL":
            return "SL_PRESSURE"
        if normalized_target == "EQUAL":
            return "NEUTRAL_PRESSURE"
        return "UNKNOWN_PRESSURE"

    @staticmethod
    def _resolve_trade_risk_alert(
        current_price: float | None,
        take_profit: float | None,
        stop_loss: float | None,
        closer_target: str,
    ) -> str:
        """Return a display-only risk proximity alert without changing trade management."""
        if current_price is None or take_profit is None or stop_loss is None:
            return "UNKNOWN_RISK"
        distance_to_take_profit = abs(take_profit - current_price)
        distance_to_stop_loss = abs(stop_loss - current_price)
        total_distance = distance_to_take_profit + distance_to_stop_loss
        if total_distance <= 0:
            return "UNKNOWN_RISK"
        proximity_ratio = min(distance_to_take_profit, distance_to_stop_loss) / total_distance
        normalized_target = str(closer_target).upper().strip()
        if normalized_target == "SL" and proximity_ratio <= 0.25:
            return "SL_DANGER_ZONE"
        if normalized_target == "TP" and proximity_ratio <= 0.25:
            return "TP_APPROACH_ZONE"
        if normalized_target == "EQUAL":
            return "BALANCED_ZONE"
        return "NEUTRAL_ZONE"

    @staticmethod
    def _build_active_trade_progress_ratio(position_snapshot: PositionMonitorSnapshot) -> dict[str, str]:
        """Build display-only TP progress, SL risk, and route-state labels for an open position."""
        take_profit_progress, stop_loss_risk, route_state = MainWindow._resolve_trade_progress_ratio(
            direction=position_snapshot.direction,
            open_price=position_snapshot.open_price,
            current_price=position_snapshot.current_price,
            take_profit=position_snapshot.take_profit,
            stop_loss=position_snapshot.stop_loss,
        )
        return {
            "take_profit_progress": take_profit_progress,
            "stop_loss_risk": stop_loss_risk,
            "route_state": route_state,
        }

    @staticmethod
    def _resolve_trade_progress_ratio(
        direction: str,
        open_price: float | None,
        current_price: float | None,
        take_profit: float | None,
        stop_loss: float | None,
    ) -> tuple[str, str, str]:
        """Resolve display-only progress percentages without changing trade management."""
        if open_price is None or current_price is None or take_profit is None or stop_loss is None:
            return "-", "-", "UNKNOWN_ROUTE"

        normalized_direction = str(direction).upper().strip()
        if normalized_direction == "BUY":
            profit_move = current_price - open_price
            loss_move = open_price - current_price
            target_distance = take_profit - open_price
            stop_distance = open_price - stop_loss
        elif normalized_direction == "SELL":
            profit_move = open_price - current_price
            loss_move = current_price - open_price
            target_distance = open_price - take_profit
            stop_distance = stop_loss - open_price
        else:
            return "-", "-", "UNKNOWN_ROUTE"

        take_profit_progress_value = MainWindow._clamped_percentage(profit_move, target_distance)
        stop_loss_risk_value = MainWindow._clamped_percentage(loss_move, stop_distance)

        if profit_move > 0:
            route_state = "PROFIT_PROGRESS"
        elif loss_move > 0:
            route_state = "DRAWDOWN_RISK"
        else:
            route_state = "ENTRY_ZONE"

        return (
            f"{take_profit_progress_value:.2f}%",
            f"{stop_loss_risk_value:.2f}%",
            route_state,
        )

    @staticmethod
    def _clamped_percentage(value: float, total: float) -> float:
        """Return a 0 to 100 display percentage for an open-trade route segment."""
        if total <= 0 or value <= 0:
            return 0.0
        return max(0.0, min(100.0, (value / total) * 100.0))


    @staticmethod
    def _resolve_trade_health(
        route_state: str,
        risk_alert: str,
        trade_pressure: str,
        take_profit_progress: str,
        stop_loss_risk: str,
    ) -> str:
        """Return a display-only health interpretation for the open Sentinel trade."""
        normalized_route = str(route_state).upper().strip()
        normalized_risk_alert = str(risk_alert).upper().strip()
        normalized_pressure = str(trade_pressure).upper().strip()
        take_profit_percent = MainWindow._parse_percentage_label(take_profit_progress)
        stop_loss_percent = MainWindow._parse_percentage_label(stop_loss_risk)

        if normalized_risk_alert == "SL_DANGER_ZONE" or stop_loss_percent >= 75.0:
            return "HIGH_RISK_NEAR_SL"
        if normalized_risk_alert == "TP_APPROACH_ZONE" or take_profit_percent >= 75.0:
            return "STRONG_PROGRESS_NEAR_TP"
        if normalized_route == "PROFIT_PROGRESS" and normalized_pressure == "TP_PRESSURE":
            return "HEALTHY_PROGRESS"
        if normalized_route == "DRAWDOWN_RISK" and normalized_pressure == "SL_PRESSURE":
            return "WATCH_DRAWDOWN"
        if normalized_route == "ENTRY_ZONE":
            return "ENTRY_ZONE_MONITOR"
        if normalized_risk_alert in {"BALANCED_ZONE", "NEUTRAL_ZONE"}:
            return "STABLE_MONITOR"
        return "UNKNOWN_HEALTH"

    @staticmethod
    def _parse_percentage_label(value: str) -> float:
        """Parse a percentage label used only for display-state interpretation."""
        try:
            return float(str(value).replace("%", "").strip())
        except (TypeError, ValueError):
            return 0.0


    @staticmethod
    def _build_profit_lock_preview(position_snapshot: PositionMonitorSnapshot, take_profit_progress: str) -> dict[str, str]:
        """Build display-only future Profit Lock Manager preview labels without modifying SL."""
        if (
            position_snapshot.open_price is None
            or position_snapshot.take_profit is None
            or position_snapshot.stop_loss is None
            or position_snapshot.current_price is None
        ):
            return {
                "profit_lock_state": "NOT_READY",
                "next_lock_trigger": "Needs TP/SL",
                "suggested_lock_sl": "-",
                "suggested_lock_progress": "-",
            }

        progress_percent = MainWindow._parse_percentage_label(take_profit_progress)
        normalized_direction = str(position_snapshot.direction).upper().strip()
        if normalized_direction not in {"BUY", "SELL"}:
            return {
                "profit_lock_state": "UNKNOWN_LOCK",
                "next_lock_trigger": "-",
                "suggested_lock_sl": "-",
                "suggested_lock_progress": "-",
            }

        stage_one_trigger = 50.0
        stage_one_lock = 25.0
        stage_two_trigger = 75.0
        stage_two_lock = 50.0

        if progress_percent >= stage_two_trigger:
            state = "STAGE_2_LOCK_READY"
            trigger_label = "75% reached"
            lock_percent = stage_two_lock
        elif progress_percent >= stage_one_trigger:
            state = "STAGE_1_LOCK_READY"
            trigger_label = "50% reached"
            lock_percent = stage_one_lock
        else:
            state = "WATCHING_50_TRIGGER"
            trigger_label = f"50% trigger ({max(0.0, stage_one_trigger - progress_percent):.2f}% away)"
            lock_percent = stage_one_lock

        suggested_lock_sl = MainWindow._resolve_profit_lock_price(
            direction=normalized_direction,
            open_price=position_snapshot.open_price,
            take_profit=position_snapshot.take_profit,
            lock_percent=lock_percent,
        )
        if not MainWindow._is_profit_lock_forward_only(
            direction=normalized_direction,
            current_stop_loss=position_snapshot.stop_loss,
            suggested_lock_sl=suggested_lock_sl,
            open_price=position_snapshot.open_price,
        ):
            return {
                "profit_lock_state": "ALREADY_PROTECTED_OR_INVALID",
                "next_lock_trigger": trigger_label,
                "suggested_lock_sl": f"{suggested_lock_sl:.2f}",
                "suggested_lock_progress": f"{lock_percent:.0f}% lock preview",
            }

        return {
            "profit_lock_state": state,
            "next_lock_trigger": trigger_label,
            "suggested_lock_sl": f"{suggested_lock_sl:.2f}",
            "suggested_lock_progress": f"{lock_percent:.0f}% lock preview",
        }

    @staticmethod
    def _resolve_profit_lock_price(direction: str, open_price: float, take_profit: float, lock_percent: float) -> float:
        """Return the display-only future SL level that would lock a percentage of the TP path."""
        progress_ratio = max(0.0, min(100.0, lock_percent)) / 100.0
        if direction == "BUY":
            return open_price + ((take_profit - open_price) * progress_ratio)
        return open_price - ((open_price - take_profit) * progress_ratio)

    @staticmethod
    def _is_profit_lock_forward_only(
        direction: str,
        current_stop_loss: float | None,
        suggested_lock_sl: float,
        open_price: float,
    ) -> bool:
        """Return True only when the previewed SL would reduce risk and lock profit."""
        if current_stop_loss is None:
            return False
        if direction == "BUY":
            return suggested_lock_sl > open_price and suggested_lock_sl > current_stop_loss
        if direction == "SELL":
            return suggested_lock_sl < open_price and suggested_lock_sl < current_stop_loss
        return False

    def set_manual_trade_review_enabled(self, enabled: bool) -> None:
        """Enable Manual Trade only when a validated ready plan exists."""
        self._manual_trade_button.setEnabled(enabled)

    def set_trading_controls_enabled(self, enabled: bool) -> None:
        """Enable trading controls while respecting manual-mode stabilization locks."""
        self._manual_trade_button.setEnabled(False if not enabled else self._manual_trade_button.isEnabled())
        if self._auto_trade_locked:
            self._auto_trade_button.setEnabled(False)
            self._auto_trade_button.setText("Auto Trade: LOCKED")
            return
        self._auto_trade_button.setEnabled(bool(enabled))

    def set_auto_trade_state(self, enabled: bool, *, emit_signal: bool = False) -> None:
        """Update the Auto Trade button safely from application logic."""
        if self._auto_trade_locked:
            self._auto_trade_enabled = False
            self._auto_trade_button.setChecked(False)
            self._auto_trade_button.setText("Auto Trade: LOCKED")
            return
        previous_state = self._auto_trade_button.blockSignals(not emit_signal)
        try:
            self._auto_trade_enabled = bool(enabled)
            self._auto_trade_button.setChecked(bool(enabled))
            self._auto_trade_button.setText("Auto Trade: ON" if enabled else "Auto Trade: OFF")
        finally:
            self._auto_trade_button.blockSignals(previous_state)

