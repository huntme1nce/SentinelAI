"""
MODULE: APP-001
FILE: APP-001-001
Module Name: Qt Application Bootstrapper
Version: 2.7.0
Purpose: Starts Sentinel AI with configured services, theme, welcome gate, market analysis, manual trading coordination, locked Auto Trade diagnostics, and delegated Trade Manager lifecycle orchestration.
Dependencies: sys, PySide6.QtWidgets, sentinel_ai.gui, sentinel_ai.market_data, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.7.0: Delegated Sentinel-owned trade lifecycle, ledger statistics, and maintenance execution to TradeManagerService for Stage 8 completion.
- 2.6.0: Added Auto Trade diagnostics so blocked execution states are visible without unlocking Auto Trade.
- 2.5.0: Locked Auto Trade for manual-mode stabilization and wired deduplicated prediction persistence.
- 2.4.0: Added guarded auto-trade execution engine with default OFF safety controls and one-trade-at-a-time protection.
- 2.3.0: Added pending history repair tool and final manual-mode completion workflow.
- 2.2.0: Improved close-result settlement and simplified main dashboard by moving diagnostics to ledger tools/backend.
- 2.1.0: Added ledger maintenance workflows: archive stale pending, export ledger, and reset test ledger with active-trade guard.
- 2.0.1: Separated current pending-close trades from stale pending backlog so old records no longer appear as active pending trades.
- 2.0.0: Added final stabilization pass with current trade priority, ledger health, stale pending backlog, and stage completion dashboard.
- 1.9.0.2: Bound close resolver and audit helper methods inside SentinelApplication.
- 1.9.0.1: Preserved close resolver routing for MT5 resolver binding hotfix.
- 1.9.0: Added robust pending-close resolver, audit status, and broader lifecycle stabilization.
- 1.8.4.1: Fixed lifecycle result-status helper binding on startup.
- 1.8.4: Added lifecycle diagnostics for active, pending, and closed Sentinel trade states.
- 1.8.3: Added pending-close settlement state for MT5 close-history delay handling.
- 1.8.2: Added active-ticket close guard to prevent open Sentinel positions from being marked closed.
- 1.8.1: Added result verification status and open/closed ledger counters for clearer trade lifecycle dashboard.
- 1.8.0: Added ledger-closed result persistence and ledger-based Sentinel performance statistics.
- 1.7.5: Added persistent Sentinel trade ledger and active recovery for all app-created trade statistics.
- 1.7.4: Added persistent Sentinel-owned trade journal and recovery for app trades created before ticket persistence.
- 1.7.3: Added Sentinel-owned trade tracking so accuracy statistics only count app-created trades.
- 1.7.2: Added close type and history match mode to position lifecycle status messages.
- 1.7.1.3: Preserved lifecycle tracking while fixing live candle-cycle countdown synchronization.
- 1.7.1.2: Preserved lifecycle tracking while fixing countdown to broker candle-open anchoring.
- 1.7.1.1: Preserved lifecycle tracking while fixing candle countdown timer repaint behavior.
- 1.7.1: Preserved lifecycle tracking while adding chart candle countdown timer and active-header priority.
- 1.7.0: Added open-to-closed position lifecycle detection and close-result status messages.
- 1.6.2: Preserved active-position priority pipeline while adding missing SL/TP warnings.
- 1.6.1.2: Preserved active-position priority pipeline for missing TP chart-scale hotfix.
- 1.6.1.1: Preserved active-position chart lock while fixing startup lock initialization.
- 1.6.1: Preserved position monitoring pipeline while active-position display takes priority over new ready plans.
- 0.1.0: Added production startup flow with mandatory manual welcome window.
- 0.2.0: Added MT5 connection initialization and safe market status reporting without trading execution.
- 0.3.0: Added validated market data feed loading without prediction or trade execution logic.
- 0.4.0: Preserved startup flow while chart panel renders live validated candles.
- 0.5.0: Added service-driven live market refresh without adding prediction or trade execution logic.
- 0.5.1: Preserved service wiring for one-second refresh and chart navigation patch.
- 0.6.0: Added broker/account-specific symbol resolution, selection, persistence, and chart reload flow.
- 0.7.0: Added read-only market structure analysis updates from validated snapshots.
- 0.8.0: Added read-only support/resistance analysis updates from market structure snapshots.
- 0.9.0: Added read-only liquidity analysis updates and persistent BOS visibility wiring.
- 0.9.1: Preserved service wiring while chart overlays changed to bounded segments.
- 0.9.2: Added read-only imbalance analysis updates for FVG and order block boxes and surfaced BOS/COC labels.
- 0.9.3.1: Passed structure snapshots into S/R overlays for fallback active range boxing.
- 0.9.3.2: Preserved service wiring for right-scroll and flicker-reduction chart runtime patch.
- 0.9.3.3: Preserved service wiring for consolidation-only S/R box and unchanged-overlay flicker patch.
- 0.9.3.8: Preserved service wiring for single-canvas repaint artifact patch.
- 1.0.0: Added read-only momentum analysis update after structure, S/R, liquidity, and imbalance context.
- 1.1.0: Added read-only confidence scoring update after momentum context.
- 1.1.1: Ensured live refresh pipeline also calls Confidence Engine after Momentum Engine.
- 1.2.3: Preserved setup-only entry validation wiring for neutral-momentum setup patch.
- 1.3.3: Preserved risk reward pipeline wiring for extended TP target discovery patch.
- 1.4.0: Added manual review gate and confirmation modal for BUY_READY / SELL_READY plans without execution.
- 1.4.1: Added polished manual review modal with Cancel/Confirm Review buttons and reviewed-plan snapshots.
- 1.5.1: Preserved manual order placement flow for adaptive filling-mode fallback patch.
- 1.6.0: Added position monitoring, manual-trade lock, and same-day trade statistics refresh.
- 1.5.0: Added user-confirmed manual MT5 order placement foundation.
- 1.3.2: Preserved risk reward pipeline wiring for rejected-plan display and directional TP guard patch.
- 1.3.1: Preserved risk reward pipeline wiring for smart TP target selection patch.
- 1.3.0: Added TP/SL and risk/reward validation update after Entry Validation Engine.
- 1.2.2: Preserved setup-only entry validation wiring for pullback-aware setup patch.
- 1.2.1: Preserved setup-only entry validation wiring for reason patch.
- 1.2.0: Added setup-only Entry Validation Engine update after Confidence Engine.
- 0.9.3.7: Preserved service wiring for physical-pixel buffer swap flicker patch.
- 0.9.3.6: Preserved service wiring for chart status accuracy and flicker reduction patch.
- 0.9.3.5: Preserved service wiring for true-consolidation S/R filter and double-buffer rendering patch.
- 0.9.3.4: Preserved service wiring for close-based S/R invalidation and compact reason patch.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from sentinel_ai.gui.main_window import MainWindow
from sentinel_ai.gui.theme import ThemeService
from sentinel_ai.gui.welcome_window import WelcomeWindow
from sentinel_ai.market_data.candle_validator import CandleDataValidationError
from sentinel_ai.models.confidence import ConfidenceSnapshot
from sentinel_ai.models.entry_validation import EntryValidationSnapshot
from sentinel_ai.models.imbalance import ImbalanceSnapshot
from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.momentum import MomentumSnapshot
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot
from sentinel_ai.models.trade_execution import ManualTradeOrderRequest, ManualTradeOrderResult
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.models.sentinel_trade import SentinelOwnedTrade
from sentinel_ai.models.symbol import SymbolResolutionResult
from sentinel_ai.services.auto_trade_diagnostics_service import AutoTradeDiagnostic, AutoTradeDiagnosticsService
from sentinel_ai.mt5.exceptions import Mt5ServiceError
from sentinel_ai.services.app_context import ApplicationContextFactory


class SentinelApplication:
    """Coordinate Qt startup without embedding domain trading logic."""

    def __init__(self) -> None:
        self._qt_application = QApplication(sys.argv)
        self._context = ApplicationContextFactory().build()
        ThemeService().apply(self._qt_application)
        self._main_window = MainWindow(self._context.config)
        self._latest_risk_reward_snapshot: RiskRewardSnapshot | None = None
        self._reviewed_trade_plan_snapshots: list[dict[str, object]] = []
        self._manual_order_results: list[ManualTradeOrderResult] = []
        self._latest_position_snapshot: PositionMonitorSnapshot | None = None
        self._latest_daily_trade_statistics: DailyTradeStatisticsSnapshot | None = None
        self._trade_manager = self._context.trade_manager_service
        self._tracked_active_position_ticket: int | None = self._trade_manager.tracked_active_position_ticket
        self._last_reported_closed_trade_key: str | None = None
        self._sentinel_owned_trade: SentinelOwnedTrade | None = self._trade_manager.sentinel_owned_trade
        self._sentinel_trade_ledger: list[SentinelOwnedTrade] = list(self._trade_manager.ledger_records)
        self._pending_stale_seconds = 300
        self._pending_extended_scan_seconds = 180
        self._auto_trade_enabled = False
        self._last_auto_trade_plan_key: str | None = None
        self._latest_auto_trade_diagnostic: AutoTradeDiagnostic | None = None
        self._active_timeframe = self._context.config.trading.default_timeframe
        self._active_symbol = self._context.config.trading.symbol.strip()
        self._trade_manager.activate_symbol_context(self._active_symbol)
        self._sync_trade_manager_legacy_state()
        self._connect_main_window_signals()
        self._connect_market_refresh_signals()
        self._initialize_mt5_connection()
        self._refresh_dashboard_statistics()
        self._update_auto_trade_diagnostics()

    def _sync_trade_manager_legacy_state(self) -> None:
        """Mirror TradeManagerService state for legacy compatibility wrappers only."""
        self._sentinel_owned_trade = self._trade_manager.sentinel_owned_trade
        self._sentinel_trade_ledger = list(self._trade_manager.ledger_records)
        self._tracked_active_position_ticket = self._trade_manager.tracked_active_position_ticket

    def run(self) -> int:
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
        self._main_window.manual_trade_requested.connect(self._handle_manual_trade_review_requested)
        self._main_window.auto_trade_toggled.connect(self._handle_auto_trade_toggled)
        self._main_window.settings_requested.connect(self._show_settings_information)
        self._main_window.ledger_maintenance_requested.connect(self._show_ledger_maintenance_tools)
        self._main_window.timeframe_changed.connect(self._handle_timeframe_changed)
        self._main_window.symbol_changed.connect(self._handle_symbol_changed)

    def _connect_market_refresh_signals(self) -> None:
        self._context.market_refresh_service.snapshot_refreshed.connect(self._handle_market_snapshot_refreshed)
        self._context.market_refresh_service.refresh_failed.connect(self._handle_market_refresh_failed)
        self._context.market_refresh_service.refresh_status_changed.connect(self._handle_market_refresh_status_changed)

    def _initialize_mt5_connection(self) -> None:
        if not self._context.config.mt5.startup_connect:
            self._main_window.set_service_status("MT5 startup connection is disabled in configuration.")
            return

        status = self._context.mt5_service.connect()
        if not status.connected:
            self._main_window.set_service_status(status.message)
            return

        symbol_catalog_loaded = self._load_symbol_catalog_options()
        symbol_resolution = self._resolve_startup_symbol()
        if not symbol_resolution.resolved or symbol_resolution.active_symbol is None:
            self._main_window.set_service_status(f"{status.message} {self._format_symbol_resolution_message(symbol_resolution)}")
            self._main_window.set_trading_controls_enabled(False)
            return

        self._active_symbol = symbol_resolution.active_symbol
        self._trade_manager.activate_symbol_context(self._active_symbol)
        self._sync_trade_manager_legacy_state()
        self._main_window.update_active_symbol(self._active_symbol)
        catalog_status = "Symbol catalog loaded." if symbol_catalog_loaded else "Symbol catalog unavailable."
        self._main_window.set_service_status(f"{status.message} {catalog_status} {symbol_resolution.message}")
        self._main_window.set_trading_controls_enabled(True)
        if self._context.config.market_data.startup_load:
            self._refresh_market_feed(self._active_timeframe)

    def _load_symbol_catalog_options(self) -> bool:
        try:
            catalog = self._context.symbol_service.load_available_symbols()
        except (Mt5ServiceError, ValueError) as error:
            self._context.logger.warning("Symbol catalog load failed: %s", error)
            self._main_window.update_runtime_status(f"Symbol catalog unavailable: {error}")
            return False

        toolbar_limit = self._context.config.symbol_management.toolbar_max_symbols
        symbol_names = tuple(item.symbol for item in catalog[:toolbar_limit])
        self._main_window.set_symbol_options(symbol_names, self._active_symbol)
        self._main_window.update_runtime_status(f"Loaded {len(catalog)} available symbols from active MT5 account.")
        return True

    def _resolve_startup_symbol(self) -> SymbolResolutionResult:
        return self._context.symbol_service.resolve_startup_symbol(
            configured_symbol=self._active_symbol,
            preferred_aliases=self._context.config.symbol_management.preferred_aliases,
            auto_resolve_enabled=self._context.config.symbol_management.auto_resolve_enabled,
        )

    def _refresh_dashboard_statistics(self) -> None:
        statistics = self._context.prediction_repository.summary_statistics()
        self._main_window.update_statistics_panel(statistics, "Statistical review pending sufficient closed trades")

    def _update_auto_trade_diagnostics(self, diagnostic: AutoTradeDiagnostic | None = None) -> AutoTradeDiagnostic:
        """Evaluate and display the current Auto Trade readiness state."""
        if diagnostic is None:
            diagnostic = self._context.auto_trade_diagnostics_service.evaluate(
                auto_trade_enabled=self._auto_trade_enabled,
                trading_config=self._context.config.trading,
                manual_config=self._context.config.manual_trading,
                snapshot=self._latest_risk_reward_snapshot,
                position_snapshot=self._latest_position_snapshot,
                last_plan_key=self._last_auto_trade_plan_key,
            )
        self._latest_auto_trade_diagnostic = diagnostic
        self._main_window.update_auto_trade_diagnostics(diagnostic.status, diagnostic.reason)
        return diagnostic

    def _refresh_market_feed(self, timeframe: str) -> MarketDataSnapshot | None:
        try:
            snapshot = self._context.market_data_feed_service.load_snapshot(
                symbol=self._active_symbol,
                timeframe=timeframe,
                bar_count=self._context.config.market_data.default_feed_bar_count,
            )
            self._main_window.update_market_feed_status(snapshot)
            structure_snapshot = self._update_market_structure(snapshot)
            if structure_snapshot is not None:
                support_resistance_snapshot = self._update_support_resistance(snapshot, structure_snapshot)
                liquidity_snapshot = self._update_liquidity(snapshot, structure_snapshot, support_resistance_snapshot)
                imbalance_snapshot = self._update_imbalance(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot)
                momentum_snapshot = self._update_momentum(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot)
                confidence_snapshot = self._update_confidence(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot, momentum_snapshot)
                entry_snapshot = self._update_entry_validation(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot, momentum_snapshot, confidence_snapshot)
                self._update_risk_reward(snapshot, entry_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot)
            self._update_position_monitoring()
            return snapshot
        except (Mt5ServiceError, CandleDataValidationError, ValueError) as error:
            self._context.logger.warning("Market feed refresh failed: %s", error)
            self._main_window.set_service_status(f"Market feed unavailable for {self._active_symbol} {timeframe}: {error}")
            return None

    def _start_market_refresh_if_ready(self, timeframe: str) -> None:
        if not self._active_symbol:
            self._context.market_refresh_service.stop()
            self._main_window.update_runtime_status("Live market refresh not started. No active symbol selected.")
            return
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
            symbol=self._active_symbol,
            timeframe=timeframe,
            bar_count=self._context.config.market_data.default_feed_bar_count,
            interval_seconds=interval_seconds,
        )

    def _show_settings_information(self) -> None:
        status = self._context.mt5_service.connection_status()
        latest_snapshot = self._context.market_data_feed_service.latest_snapshot()
        if latest_snapshot is None:
            feed_status = "No validated market feed snapshot loaded."
        else:
            feed_status = f"{latest_snapshot.symbol} {latest_snapshot.timeframe}: {latest_snapshot.candle_count} validated candles loaded."
        refresh_status = "Running" if self._context.market_refresh_service.is_running else "Stopped"
        QMessageBox.information(
            self._main_window,
            "Sentinel AI Settings",
            "Configuration and database are initialized.\n\n"
            f"Database:\n{self._context.database_service.database_path}\n\n"
            f"MT5 Status:\n{status.message}\n\n"
            f"Active Symbol:\n{self._active_symbol}\n\n"
            f"Available Symbols Loaded:\n{self._context.symbol_service.available_symbol_count}\n\n"
            f"Market Feed:\n{feed_status}\n\n"
            f"Live Refresh:\n{refresh_status}",
        )

    def _handle_timeframe_changed(self, timeframe: str) -> None:
        self._active_timeframe = timeframe
        self._context.logger.info("Timeframe selected: %s", timeframe)
        status = self._context.mt5_service.connection_status()
        if not status.connected:
            self._context.market_refresh_service.stop()
            self._main_window.set_service_status(f"Selected timeframe: {timeframe}. {status.message}")
            return
        if self._refresh_market_feed(timeframe) is not None:
            self._start_market_refresh_if_ready(timeframe)

    def _handle_symbol_changed(self, requested_symbol: str) -> None:
        clean_symbol = str(requested_symbol).strip()
        if not clean_symbol or clean_symbol == self._active_symbol:
            return
        self._context.market_refresh_service.stop()
        try:
            resolution = self._context.symbol_service.activate_symbol(clean_symbol)
        except (Mt5ServiceError, ValueError) as error:
            self._context.logger.warning("Symbol activation failed: %s", error)
            self._main_window.set_service_status(f"Symbol activation failed for {clean_symbol}: {error}")
            return

        if not resolution.resolved or resolution.active_symbol is None:
            self._main_window.set_service_status(self._format_symbol_resolution_message(resolution))
            return

        self._active_symbol = resolution.active_symbol
        self._trade_manager.activate_symbol_context(self._active_symbol)
        self._sync_trade_manager_legacy_state()
        self._main_window.update_active_symbol(self._active_symbol)
        self._main_window.set_service_status(resolution.message)
        if self._refresh_market_feed(self._active_timeframe) is not None:
            self._start_market_refresh_if_ready(self._active_timeframe)

    def _handle_market_snapshot_refreshed(self, snapshot: object) -> None:
        if not isinstance(snapshot, MarketDataSnapshot):
            self._context.logger.warning("Ignored unexpected market refresh payload: %r", type(snapshot))
            return
        if snapshot.symbol != self._active_symbol:
            self._context.logger.info("Ignored stale refresh snapshot for %s while active symbol is %s.", snapshot.symbol, self._active_symbol)
            return
        if snapshot.timeframe != self._active_timeframe:
            self._context.logger.info("Ignored stale refresh snapshot for %s while active timeframe is %s.", snapshot.timeframe, self._active_timeframe)
            return
        self._main_window.update_live_market_snapshot(snapshot)
        structure_snapshot = self._update_market_structure(snapshot)
        if structure_snapshot is not None:
            support_resistance_snapshot = self._update_support_resistance(snapshot, structure_snapshot)
            liquidity_snapshot = self._update_liquidity(snapshot, structure_snapshot, support_resistance_snapshot)
            imbalance_snapshot = self._update_imbalance(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot)
            momentum_snapshot = self._update_momentum(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot)
            confidence_snapshot = self._update_confidence(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot, momentum_snapshot)
            entry_snapshot = self._update_entry_validation(snapshot, structure_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot, momentum_snapshot, confidence_snapshot)
            self._update_risk_reward(snapshot, entry_snapshot, support_resistance_snapshot, liquidity_snapshot, imbalance_snapshot)
        self._update_position_monitoring()
        self._evaluate_auto_trade_after_analysis()

    def _update_market_structure(self, snapshot: MarketDataSnapshot) -> MarketStructureSnapshot | None:
        try:
            structure_snapshot = self._context.market_structure_engine.analyze(snapshot)
        except ValueError as error:
            self._context.logger.warning("Market structure analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Market structure unavailable: {error}")
            return None
        self._main_window.update_market_structure_status(structure_snapshot)
        return structure_snapshot

    def _update_support_resistance(self, snapshot: MarketDataSnapshot, structure_snapshot: MarketStructureSnapshot) -> SupportResistanceSnapshot | None:
        try:
            support_resistance_snapshot = self._context.support_resistance_engine.analyze(snapshot, structure_snapshot)
        except ValueError as error:
            self._context.logger.warning("Support/resistance analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Support/resistance unavailable: {error}")
            return None
        self._main_window.update_support_resistance_status(
            support_resistance_snapshot,
            structure_snapshot.summary,
            structure_snapshot,
        )
        return support_resistance_snapshot

    def _update_liquidity(
        self,
        snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
    ) -> LiquiditySnapshot | None:
        try:
            liquidity_snapshot = self._context.liquidity_engine.analyze(snapshot, structure_snapshot)
        except ValueError as error:
            self._context.logger.warning("Liquidity analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Liquidity unavailable: {error}")
            return None
        base_reason = structure_snapshot.summary
        if support_resistance_snapshot is not None:
            base_reason = f"{base_reason} | {support_resistance_snapshot.summary}"
        self._main_window.update_liquidity_status(liquidity_snapshot, base_reason)
        return liquidity_snapshot

    def _update_imbalance(
        self,
        snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
    ) -> ImbalanceSnapshot | None:
        try:
            imbalance_snapshot = self._context.imbalance_engine.analyze(snapshot, structure_snapshot)
        except ValueError as error:
            self._context.logger.warning("Imbalance analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Imbalance unavailable: {error}")
            return None
        base_reason = structure_snapshot.summary
        if support_resistance_snapshot is not None:
            base_reason = f"{base_reason} | {support_resistance_snapshot.summary}"
        if liquidity_snapshot is not None:
            base_reason = f"{base_reason} | {liquidity_snapshot.summary}"
        self._main_window.update_imbalance_status(imbalance_snapshot, base_reason)
        return imbalance_snapshot

    def _update_momentum(
        self,
        snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> MomentumSnapshot | None:
        try:
            momentum_snapshot = self._context.momentum_engine.analyze(snapshot)
        except ValueError as error:
            self._context.logger.warning("Momentum analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Momentum unavailable: {error}")
            return None
        base_reason = structure_snapshot.summary
        if support_resistance_snapshot is not None:
            base_reason = f"{base_reason} | {support_resistance_snapshot.summary}"
        if liquidity_snapshot is not None:
            base_reason = f"{base_reason} | {liquidity_snapshot.summary}"
        if imbalance_snapshot is not None:
            base_reason = f"{base_reason} | {imbalance_snapshot.summary}"
        self._main_window.update_momentum_status(momentum_snapshot, base_reason)
        return momentum_snapshot

    def _update_confidence(
        self,
        snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
        momentum_snapshot: MomentumSnapshot | None,
    ) -> ConfidenceSnapshot | None:
        try:
            confidence_snapshot = self._context.confidence_engine.analyze(
                market_snapshot=snapshot,
                structure_snapshot=structure_snapshot,
                support_resistance_snapshot=support_resistance_snapshot,
                liquidity_snapshot=liquidity_snapshot,
                imbalance_snapshot=imbalance_snapshot,
                momentum_snapshot=momentum_snapshot,
            )
        except ValueError as error:
            self._context.logger.warning("Confidence analysis failed: %s", error)
            self._main_window.update_runtime_status(f"Confidence unavailable: {error}")
            return None
        self._main_window.update_confidence_status(confidence_snapshot)
        return confidence_snapshot

    def _update_entry_validation(
        self,
        snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
        momentum_snapshot: MomentumSnapshot | None,
        confidence_snapshot: ConfidenceSnapshot | None,
    ) -> EntryValidationSnapshot | None:
        try:
            entry_snapshot = self._context.entry_validation_engine.analyze(
                market_snapshot=snapshot,
                structure_snapshot=structure_snapshot,
                support_resistance_snapshot=support_resistance_snapshot,
                liquidity_snapshot=liquidity_snapshot,
                imbalance_snapshot=imbalance_snapshot,
                momentum_snapshot=momentum_snapshot,
                confidence_snapshot=confidence_snapshot,
            )
        except ValueError as error:
            self._context.logger.warning("Entry validation failed: %s", error)
            self._main_window.update_runtime_status(f"Entry validation unavailable: {error}")
            return None
        self._main_window.update_entry_validation_status(entry_snapshot)
        return entry_snapshot

    def _update_risk_reward(
        self,
        snapshot: MarketDataSnapshot,
        entry_snapshot: EntryValidationSnapshot | None,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> RiskRewardSnapshot | None:
        try:
            risk_reward_snapshot = self._context.risk_reward_engine.analyze(
                market_snapshot=snapshot,
                entry_snapshot=entry_snapshot,
                support_resistance_snapshot=support_resistance_snapshot,
                liquidity_snapshot=liquidity_snapshot,
                imbalance_snapshot=imbalance_snapshot,
            )
        except ValueError as error:
            self._context.logger.warning("Risk/reward validation failed: %s", error)
            self._main_window.update_runtime_status(f"Risk/reward unavailable: {error}")
            return None
        self._latest_risk_reward_snapshot = risk_reward_snapshot
        self._main_window.update_risk_reward_status(risk_reward_snapshot)
        self._context.prediction_lifecycle_service.record_from_risk_reward_snapshot(risk_reward_snapshot)
        self._update_auto_trade_diagnostics()
        return risk_reward_snapshot

    def _update_position_monitoring(self) -> None:
        """Refresh MT5 open-position monitoring through the TradeManagerService."""
        status = self._context.mt5_service.connection_status()
        if not status.connected:
            return
        try:
            manual_config = self._context.config.manual_trading
            position_snapshot = self._context.mt5_service.monitor_symbol_position(
                symbol=self._active_symbol,
                magic_number=manual_config.magic_number,
            )
            self._trade_manager.sync_sentinel_owned_position_ticket(
                position_snapshot,
                active_timeframe=self._active_timeframe,
            )
            daily_statistics = self._trade_manager.sentinel_owned_daily_statistics(
                position_snapshot=position_snapshot,
                active_symbol=self._active_symbol,
            )
            lifecycle_event = self._trade_manager.track_position_lifecycle(position_snapshot, daily_statistics)
            self._sync_trade_manager_legacy_state()
        except (Mt5ServiceError, ValueError) as error:
            self._context.logger.warning("Position monitoring unavailable: %s", error)
            self._main_window.update_runtime_status(f"Position monitoring unavailable: {error}")
            return

        if lifecycle_event.message:
            self._main_window.update_runtime_status(lifecycle_event.message)
        daily_statistics = self._trade_manager.statistics_with_ledger_totals(daily_statistics)
        self._latest_position_snapshot = position_snapshot
        self._latest_daily_trade_statistics = daily_statistics
        self._main_window.update_position_monitor_status(position_snapshot, daily_statistics)
        self._update_auto_trade_diagnostics()


    def _register_sentinel_owned_trade(
        self,
        snapshot: RiskRewardSnapshot,
        result: ManualTradeOrderResult,
        *,
        source: str = "SENTINEL_APP_MANUAL",
    ) -> None:
        """Delegate Sentinel-created trade registration to TradeManagerService."""
        self._trade_manager.register_sentinel_owned_trade(snapshot, result, source=source)
        self._sync_trade_manager_legacy_state()



    @staticmethod











    @staticmethod

    @staticmethod



    @staticmethod


    @staticmethod

    @staticmethod





    @staticmethod

    @staticmethod












    @staticmethod

    @staticmethod

    def _show_ledger_maintenance_tools(self) -> None:
        """Show guarded ledger maintenance actions for stale records and exports."""
        open_count, current_pending_count, stale_count, closed_count, total_count = self._ledger_maintenance_counts()
        message_box = QMessageBox(self._main_window)
        message_box.setWindowTitle("Ledger Maintenance")
        message_box.setText("Sentinel ledger maintenance tools")
        message_box.setInformativeText(
            "\n".join(
                (
                    f"Open Sentinel Trades: {open_count}",
                    f"Current Pending Close Trades: {current_pending_count}",
                    f"Stale Pending Backlog Trades: {stale_count}",
                    f"Closed Ledger Trades: {closed_count}",
                    f"Total Ledger Records: {total_count}",
                    "",
                    "Repair pending history attempts to convert unresolved pending records into verified closed trades.",
                    "Archive stale records removes old unresolved test records from the live dashboard.",
                    "Export ledger creates JSON and CSV files for review.",
                    "Reset test ledger is blocked while an active trade is open.",
                )
            )
        )
        repair_button = message_box.addButton("Repair Pending History", QMessageBox.ButtonRole.ActionRole)
        archive_button = message_box.addButton("Archive Stale Pending", QMessageBox.ButtonRole.ActionRole)
        export_button = message_box.addButton("Export Ledger", QMessageBox.ButtonRole.ActionRole)
        reset_button = message_box.addButton("Reset Test Ledger", QMessageBox.ButtonRole.DestructiveRole)
        close_button = message_box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        message_box.setDefaultButton(close_button)
        message_box.exec()

        clicked = message_box.clickedButton()
        if clicked == repair_button:
            self._repair_pending_history_records()
        elif clicked == archive_button:
            self._archive_stale_pending_records()
        elif clicked == export_button:
            self._export_sentinel_ledger()
        elif clicked == reset_button:
            self._reset_test_ledger_guarded()

    def _ledger_maintenance_counts(self) -> tuple[int, int, int, int, int]:
        """Return TradeManagerService ledger maintenance counts."""
        counts = self._trade_manager.ledger_maintenance_counts()
        self._sync_trade_manager_legacy_state()
        return counts.open_count, counts.current_pending_count, counts.stale_count, counts.closed_count, counts.total_count

    def _repair_pending_history_records(self) -> None:
        """Attempt to repair unresolved pending ledger records through TradeManagerService."""
        result = self._trade_manager.repair_pending_history_records()
        self._sync_trade_manager_legacy_state()
        self._update_position_monitoring()
        QMessageBox.information(self._main_window, "Ledger Maintenance", result.message)




    @staticmethod

    def _archive_stale_pending_records(self) -> None:
        """Archive stale pending records through TradeManagerService."""
        result = self._trade_manager.archive_stale_pending_records()
        self._sync_trade_manager_legacy_state()
        self._update_position_monitoring()
        if result.success:
            QMessageBox.information(self._main_window, "Ledger Maintenance", result.message)
        else:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", result.message)

    def _export_sentinel_ledger(self) -> None:
        """Export the Sentinel ledger through TradeManagerService."""
        result = self._trade_manager.export_sentinel_ledger()
        if result.success:
            QMessageBox.information(self._main_window, "Ledger Maintenance", result.message)
        else:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", result.message)

    def _reset_test_ledger_guarded(self) -> None:
        """Reset test ledger through TradeManagerService after GUI confirmation."""
        open_count, current_pending_count, stale_count, closed_count, total_count = self._ledger_maintenance_counts()
        if open_count > 0:
            QMessageBox.warning(
                self._main_window,
                "Ledger Maintenance",
                "Reset blocked because an active Sentinel trade is open. Close or wait for the active trade first.",
            )
            return
        confirm = QMessageBox.question(
            self._main_window,
            "Reset Test Ledger",
            (
                f"This will archive and clear {total_count} ledger record(s).\n\n"
                "This should only be used for demo/test cleanup. Continue?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        result = self._trade_manager.reset_test_ledger_guarded()
        self._sync_trade_manager_legacy_state()
        self._update_position_monitoring()
        if result.success:
            QMessageBox.information(self._main_window, "Ledger Maintenance", result.message)
        else:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", result.message)

    @staticmethod

    def _handle_auto_trade_toggled(self, enabled: bool) -> None:
        """Enable or disable guarded auto-trade execution after explicit user confirmation."""
        if self._context.config.trading.auto_trade_locked:
            self._auto_trade_enabled = False
            self._main_window.set_auto_trade_state(False)
            diagnostic = self._update_auto_trade_diagnostics()
            self._main_window.update_runtime_status(diagnostic.reason)
            return
        if enabled:
            diagnostic = self._update_auto_trade_diagnostics()
            if diagnostic.status == "BLOCKED" and self._latest_position_snapshot is not None and self._latest_position_snapshot.has_open_position:
                self._auto_trade_enabled = False
                self._main_window.set_auto_trade_state(False)
                QMessageBox.warning(
                    self._main_window,
                    "Auto Trade Blocked",
                    diagnostic.reason,
                )
                return
            confirmation = QMessageBox.question(
                self._main_window,
                "Enable Auto Trade",
                (
                    "Auto Trade will place MT5 market orders automatically only when a BUY_READY or SELL_READY "
                    "plan passes the configured confidence and risk/reward checks. The dashboard will show "
                    "the exact reason whenever execution is waiting or blocked.\n\n"
                    "Default safety remains one trade at a time. Continue?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirmation != QMessageBox.StandardButton.Yes:
                self._auto_trade_enabled = False
                self._main_window.set_auto_trade_state(False)
                self._update_auto_trade_diagnostics()
                return
            self._auto_trade_enabled = True
            self._last_auto_trade_plan_key = None
            diagnostic = self._update_auto_trade_diagnostics()
            self._main_window.update_runtime_status(f"Auto Trade enabled. {diagnostic.reason}")
        else:
            self._auto_trade_enabled = False
            diagnostic = self._update_auto_trade_diagnostics()
            self._main_window.update_runtime_status(diagnostic.reason)

    def _evaluate_auto_trade_after_analysis(self) -> None:
        """Place an automatic trade only when diagnostics confirm all guardrails pass."""
        diagnostic = self._update_auto_trade_diagnostics()
        if diagnostic.status == "LOCKED":
            self._auto_trade_enabled = False
            self._last_auto_trade_plan_key = None
            return
        if diagnostic.status != "ARMED":
            self._context.logger.debug("Auto Trade not submitted: %s | %s", diagnostic.status, diagnostic.reason)
            return

        snapshot = self._latest_risk_reward_snapshot
        if snapshot is None or snapshot.plan is None:
            return

        result = self._place_manual_mt5_order(snapshot)
        self._manual_order_results.append(result)
        self._last_auto_trade_plan_key = diagnostic.plan_key
        result_diagnostic = self._context.auto_trade_diagnostics_service.from_order_result(result)
        self._update_auto_trade_diagnostics(result_diagnostic)
        self._context.logger.info("Auto trade result: %s", result)
        self._main_window.update_runtime_status(result.message)
        if result.accepted:
            self._register_sentinel_owned_trade(snapshot, result, source="SENTINEL_APP_AUTO")
            self._update_position_monitoring()
            QMessageBox.information(
                self._main_window,
                "Auto Trade Placed",
                (
                    f"{result.direction} auto trade placed.\n\n"
                    f"Symbol: {result.symbol}\n"
                    f"Volume: {result.volume:.2f}\n"
                    f"Order: {result.order_ticket or '-'}\n"
                    f"Deal: {result.deal_ticket or '-'}\n"
                    f"Filled Price: {result.filled_price if result.filled_price is not None else '-'}"
                ),
            )
        else:
            self._auto_trade_enabled = False
            self._main_window.set_auto_trade_state(False)
            QMessageBox.warning(
                self._main_window,
                "Auto Trade Stopped",
                f"Auto Trade was disabled because order placement failed.\n\n{result.message}",
            )

    def _auto_trade_plan_passes_guardrails(self, snapshot: RiskRewardSnapshot) -> bool:
        """Return True when diagnostics mark the current plan as ARMED."""
        diagnostic = self._context.auto_trade_diagnostics_service.evaluate(
            auto_trade_enabled=self._auto_trade_enabled,
            trading_config=self._context.config.trading,
            manual_config=self._context.config.manual_trading,
            snapshot=snapshot,
            position_snapshot=self._latest_position_snapshot,
            last_plan_key=self._last_auto_trade_plan_key,
        )
        return diagnostic.status == "ARMED"

    @staticmethod
    def _auto_trade_plan_key(snapshot: RiskRewardSnapshot) -> str:
        """Return a stable key so the same ready plan is not submitted repeatedly."""
        return AutoTradeDiagnosticsService.plan_key(snapshot)


    def _handle_manual_trade_review_requested(self) -> None:
        """Show a final confirmation gate before placing a user-confirmed manual MT5 order."""
        snapshot = self._latest_risk_reward_snapshot
        if snapshot is None or snapshot.plan is None or not snapshot.plan.valid or snapshot.direction not in {"BUY_READY", "SELL_READY"}:
            QMessageBox.information(
                self._main_window,
                "Manual Trade Review",
                "No BUY_READY or SELL_READY plan is available for manual review.",
            )
            return

        plan = snapshot.plan
        direction = "BUY" if snapshot.direction == "BUY_READY" else "SELL"
        review_snapshot = self._build_trade_plan_review_snapshot(snapshot)
        message_box = QMessageBox(self._main_window)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Manual Trade Review")
        message_box.setText(f"{direction} plan is ready for manual review.")
        message_box.setInformativeText(
            "\n".join(
                (
                    f"Symbol: {snapshot.symbol}",
                    f"Direction: {direction}",
                    f"Timeframe: {snapshot.timeframe}",
                    f"Entry: {plan.entry_price:.2f}",
                    f"SL: {plan.stop_loss:.2f}",
                    f"TP: {plan.take_profit:.2f}",
                    f"RR: {plan.risk_reward_ratio:.2f}",
                    f"Confidence: {snapshot.confidence_percentage:.2f}%",
                    "",
                    "Click Place Manual Order only if you want Sentinel AI to send this market order to MT5.",
                )
            )
        )
        message_box.setDetailedText(
            "\n".join(
                (
                    f"Reason: {snapshot.reason}",
                    f"Stop logic: {plan.stop_reason}",
                    f"Target logic: {plan.target_reason}",
                    "Execution status: Sprint 15 sends a manual MT5 market order only after this confirmation.",
                )
            )
        )
        cancel_button = message_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        confirm_button = message_box.addButton("Place Manual Order", QMessageBox.ButtonRole.AcceptRole)
        message_box.setDefaultButton(cancel_button)
        message_box.exec()

        if message_box.clickedButton() == confirm_button:
            self._reviewed_trade_plan_snapshots.append(review_snapshot)
            result = self._place_manual_mt5_order(snapshot)
            self._manual_order_results.append(result)
            self._context.logger.info("Manual order result: %s", result)
            self._main_window.update_runtime_status(result.message)
            if result.accepted:
                self._register_sentinel_owned_trade(snapshot, result, source="SENTINEL_APP_MANUAL")
                self._update_position_monitoring()
                QMessageBox.information(
                    self._main_window,
                    "Manual Order Placed",
                    (
                        f"{result.direction} manual order placed.\n\n"
                        f"Symbol: {result.symbol}\n"
                        f"Volume: {result.volume:.2f}\n"
                        f"Order: {result.order_ticket or '-'}\n"
                        f"Deal: {result.deal_ticket or '-'}\n"
                        f"Filled Price: {result.filled_price if result.filled_price is not None else '-'}"
                    ),
                )
            else:
                QMessageBox.warning(
                    self._main_window,
                    "Manual Order Not Placed",
                    result.message,
                )

    def _place_manual_mt5_order(self, snapshot: RiskRewardSnapshot) -> ManualTradeOrderResult:
        """Place the latest user-confirmed ready plan as one manual MT5 market order."""
        if snapshot.plan is None:
            return ManualTradeOrderResult(
                accepted=False,
                symbol=snapshot.symbol,
                direction=snapshot.direction,
                volume=0.0,
                requested_price=None,
                filled_price=None,
                stop_loss=0.0,
                take_profit=0.0,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                comment="",
                message="Manual order blocked: no risk/reward plan is available.",
                sent_at=datetime.now(timezone.utc),
            )
        if not self._context.config.manual_trading.enabled:
            plan = snapshot.plan
            return ManualTradeOrderResult(
                accepted=False,
                symbol=snapshot.symbol,
                direction=snapshot.direction,
                volume=0.0,
                requested_price=None,
                filled_price=None,
                stop_loss=plan.stop_loss,
                take_profit=plan.take_profit,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                comment="",
                message="Manual order blocked: manual_trading.enabled is false.",
                sent_at=datetime.now(timezone.utc),
            )

        plan = snapshot.plan
        manual_config = self._context.config.manual_trading
        direction = "BUY" if snapshot.direction == "BUY_READY" else "SELL"
        volume = min(float(manual_config.default_volume), float(manual_config.max_volume))
        request = ManualTradeOrderRequest(
            symbol=snapshot.symbol,
            direction=direction,
            volume=volume,
            stop_loss=plan.stop_loss,
            take_profit=plan.take_profit,
            deviation_points=manual_config.deviation_points,
            magic_number=manual_config.magic_number,
            comment=manual_config.order_comment,
            order_filling=manual_config.order_filling,
        )
        return self._context.mt5_service.place_manual_market_order(
            request=request,
            one_position_per_symbol=manual_config.one_position_per_symbol,
        )

    @staticmethod
    def _build_trade_plan_review_snapshot(snapshot: RiskRewardSnapshot) -> dict[str, object]:
        """Build a manual-order review snapshot for memory/logging before execution."""
        if snapshot.plan is None:
            return {}
        plan = snapshot.plan
        return {
            "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
            "symbol": snapshot.symbol,
            "timeframe": snapshot.timeframe,
            "direction": snapshot.direction,
            "confidence_percentage": round(float(snapshot.confidence_percentage), 2),
            "entry_price": round(float(plan.entry_price), 5),
            "stop_loss": round(float(plan.stop_loss), 5),
            "take_profit": round(float(plan.take_profit), 5),
            "risk_points": round(float(plan.risk_points), 5),
            "reward_points": round(float(plan.reward_points), 5),
            "risk_reward_ratio": round(float(plan.risk_reward_ratio), 2),
            "reason": snapshot.reason,
            "stop_reason": plan.stop_reason,
            "target_reason": plan.target_reason,
            "execution_status": "manual_order_requested_after_confirmation",
        }

    def _handle_market_refresh_failed(self, message: str) -> None:
        self._main_window.update_runtime_status(message)

    def _handle_market_refresh_status_changed(self, message: str) -> None:
        self._main_window.update_runtime_status(message)

    @staticmethod
    def _format_symbol_resolution_message(resolution: SymbolResolutionResult) -> str:
        if not resolution.candidates:
            return resolution.message
        candidate_text = ", ".join(resolution.candidate_symbols[:5])
        return f"{resolution.message} Suggestions: {candidate_text}"

    def _shutdown_services(self) -> None:
        self._context.market_refresh_service.stop()
        self._context.mt5_service.disconnect()


def run_application() -> int:
    application = SentinelApplication()
    return application.run()
