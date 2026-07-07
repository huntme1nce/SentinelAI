"""
MODULE: APP-001
FILE: APP-001-001
Module Name: Qt Application Bootstrapper
Version: 2.5.0
Purpose: Starts Sentinel AI with configured services, theme, welcome gate, MT5 status, symbol management, market feed, chart rendering, refresh loop, analysis pipeline, manual trading, locked auto-trade stabilization, and prediction persistence.
Dependencies: sys, PySide6.QtWidgets, sentinel_ai.gui, sentinel_ai.market_data, sentinel_ai.models, sentinel_ai.services
Change History:
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
import json
import os
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

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
        self._tracked_active_position_ticket: int | None = None
        self._last_reported_closed_trade_key: str | None = None
        self._sentinel_owned_trade: SentinelOwnedTrade | None = None
        self._sentinel_trade_ledger: list[SentinelOwnedTrade] = []
        self._pending_stale_seconds = 300
        self._pending_extended_scan_seconds = 180
        self._auto_trade_enabled = False
        self._last_auto_trade_plan_key: str | None = None
        self._active_timeframe = self._context.config.trading.default_timeframe
        self._active_symbol = self._context.config.trading.symbol.strip()
        self._sentinel_trade_ledger = self._load_sentinel_trade_ledger()
        legacy_trade = self._load_sentinel_owned_trade()
        if legacy_trade is not None:
            self._upsert_sentinel_trade(legacy_trade)
        self._sentinel_owned_trade = self._select_active_sentinel_trade()
        self._connect_main_window_signals()
        self._connect_market_refresh_signals()
        self._initialize_mt5_connection()
        self._refresh_dashboard_statistics()

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
        return risk_reward_snapshot

    def _update_position_monitoring(self) -> None:
        """Refresh MT5 open-position monitoring and Sentinel-owned trade statistics."""
        status = self._context.mt5_service.connection_status()
        if not status.connected:
            return
        try:
            manual_config = self._context.config.manual_trading
            position_snapshot = self._context.mt5_service.monitor_symbol_position(
                symbol=self._active_symbol,
                magic_number=manual_config.magic_number,
            )
            self._sync_sentinel_owned_position_ticket(position_snapshot)
            if not position_snapshot.has_open_position:
                self._tracked_active_position_ticket = None
            daily_statistics = self._sentinel_owned_daily_statistics(position_snapshot, manual_config.magic_number)
        except (Mt5ServiceError, ValueError) as error:
            self._context.logger.warning("Position monitoring unavailable: %s", error)
            self._main_window.update_runtime_status(f"Position monitoring unavailable: {error}")
            return

        self._track_position_lifecycle(position_snapshot, daily_statistics)
        daily_statistics = self._statistics_with_ledger_totals(daily_statistics)
        self._latest_position_snapshot = position_snapshot
        self._latest_daily_trade_statistics = daily_statistics
        self._main_window.update_position_monitor_status(position_snapshot, daily_statistics)

    def _track_position_lifecycle(
        self,
        position_snapshot: PositionMonitorSnapshot,
        daily_statistics: DailyTradeStatisticsSnapshot,
    ) -> None:
        """Detect Sentinel-owned open-to-closed transitions and surface the latest result."""
        if self._sentinel_owned_trade is None:
            self._tracked_active_position_ticket = None
            return

        owned_ticket = self._sentinel_owned_ticket()
        if position_snapshot.has_open_position and self._is_position_sentinel_owned(position_snapshot):
            self._tracked_active_position_ticket = position_snapshot.ticket or owned_ticket
            return

        if owned_ticket is None:
            return

        if daily_statistics.last_closed_result == "NONE":
            self._mark_sentinel_trade_pending_close()
            self._main_window.update_runtime_status("Sentinel-owned trade is pending close result. Waiting for MT5 history settlement.")
            return

        close_ticket = daily_statistics.last_closed_ticket or owned_ticket
        close_key = f"{daily_statistics.symbol}:{close_ticket}:{daily_statistics.last_closed_result}:{daily_statistics.last_closed_profit}"
        if self._last_reported_closed_trade_key == close_key:
            return

        profit_text = (
            f"{daily_statistics.last_closed_profit:.2f}"
            if daily_statistics.last_closed_profit is not None
            else "-"
        )
        close_reason = f" | {daily_statistics.last_close_reason}" if daily_statistics.last_close_reason else ""
        match_mode = f" | Match {daily_statistics.history_match_mode}" if daily_statistics.history_match_mode else ""
        message = (
            f"Sentinel app trade closed: {daily_statistics.last_closed_result} | "
            f"{daily_statistics.last_close_type or 'CLOSED'} | "
            f"P/L {profit_text} | Ticket {close_ticket}{close_reason}{match_mode}"
        )
        self._last_reported_closed_trade_key = close_key
        self._tracked_active_position_ticket = None
        self._close_sentinel_owned_trade(daily_statistics, close_ticket)
        self._context.logger.info(message)
        self._main_window.update_runtime_status(message)

    def _register_sentinel_owned_trade(
        self,
        snapshot: RiskRewardSnapshot,
        result: ManualTradeOrderResult,
        *,
        source: str = "SENTINEL_APP_MANUAL",
    ) -> None:
        """Persist the app-created trade identity for Sentinel-only accuracy tracking."""
        if snapshot.plan is None:
            return
        prediction_uid = self._context.prediction_lifecycle_service.record_from_risk_reward_snapshot(snapshot)
        self._context.prediction_lifecycle_service.mark_trade_active(prediction_uid)
        plan = snapshot.plan
        self._sentinel_owned_trade = SentinelOwnedTrade(
            symbol=result.symbol,
            direction=result.direction,
            order_ticket=result.order_ticket,
            deal_ticket=result.deal_ticket,
            position_ticket=result.order_ticket or result.deal_ticket,
            entry_price=result.filled_price or result.requested_price or plan.entry_price,
            stop_loss=result.stop_loss,
            take_profit=result.take_profit,
            risk_reward_ratio=plan.risk_reward_ratio,
            confidence_percentage=snapshot.confidence_percentage,
            timeframe=snapshot.timeframe,
            opened_at=result.sent_at,
            source=source,
            prediction_uid=prediction_uid,
        )
        self._tracked_active_position_ticket = self._sentinel_owned_trade.position_ticket
        self._last_reported_closed_trade_key = None
        self._upsert_sentinel_trade(self._sentinel_owned_trade)
        self._save_sentinel_owned_trade()
        self._context.logger.info("Registered Sentinel-owned trade: %s", self._sentinel_owned_trade)

    def _sync_sentinel_owned_position_ticket(self, position_snapshot: PositionMonitorSnapshot) -> None:
        """Update, recover, or reopen the Sentinel-owned active position ticket."""
        if not position_snapshot.has_open_position or position_snapshot.ticket is None:
            return
        manual_magic = int(self._context.config.manual_trading.magic_number)
        magic_matches = position_snapshot.magic_number is not None and int(position_snapshot.magic_number) == manual_magic

        reopened_trade = self._reopen_sentinel_trade_from_active_position(position_snapshot)
        if reopened_trade is not None:
            self._sentinel_owned_trade = reopened_trade
            self._tracked_active_position_ticket = position_snapshot.ticket
            self._save_sentinel_owned_trade()
            self._context.logger.info("Reopened Sentinel ledger trade because MT5 position is still active: %s", reopened_trade)
            return

        if self._sentinel_owned_trade is None and magic_matches:
            self._sentinel_owned_trade = SentinelOwnedTrade(
                symbol=position_snapshot.symbol,
                direction=position_snapshot.direction,
                order_ticket=None,
                deal_ticket=None,
                position_ticket=position_snapshot.ticket,
                entry_price=position_snapshot.open_price,
                stop_loss=position_snapshot.stop_loss or 0.0,
                take_profit=position_snapshot.take_profit or 0.0,
                risk_reward_ratio=0.0,
                confidence_percentage=0.0,
                timeframe=self._active_timeframe,
                opened_at=position_snapshot.opened_at or datetime.now(timezone.utc),
            )
            self._tracked_active_position_ticket = position_snapshot.ticket
            self._upsert_sentinel_trade(self._sentinel_owned_trade)
            self._save_sentinel_owned_trade()
            self._context.logger.info("Recovered active Sentinel-owned trade from MT5 position: %s", self._sentinel_owned_trade)
            return

        if self._sentinel_owned_trade is None:
            return
        if position_snapshot.symbol != self._sentinel_owned_trade.symbol:
            return
        current_ticket = self._sentinel_owned_trade.position_ticket
        candidate_tickets = {
            ticket
            for ticket in (
                current_ticket,
                self._sentinel_owned_trade.order_ticket,
                self._sentinel_owned_trade.deal_ticket,
                self._sentinel_owned_trade.close_ticket,
            )
            if ticket is not None
        }
        ticket_matches = position_snapshot.ticket in candidate_tickets
        if current_ticket is None or ticket_matches or magic_matches:
            if current_ticket != position_snapshot.ticket or self._sentinel_owned_trade.closed:
                self._sentinel_owned_trade = replace(
                    self._sentinel_owned_trade,
                    position_ticket=position_snapshot.ticket,
                    closed=False,
                    close_ticket=None,
                    close_profit=None,
                    close_result="NONE",
                    close_type="",
                    close_reason="",
                    closed_at=None,
                    history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
                    pending_close=False,
                    pending_close_since=None,
                )
                self._upsert_sentinel_trade(self._sentinel_owned_trade)
                self._save_sentinel_owned_trade()
            self._tracked_active_position_ticket = position_snapshot.ticket

    def _reopen_sentinel_trade_from_active_position(
        self,
        position_snapshot: PositionMonitorSnapshot,
    ) -> SentinelOwnedTrade | None:
        """Reopen any ledger record that matches a still-active MT5 position ticket."""
        if position_snapshot.ticket is None:
            return None
        updated_trade: SentinelOwnedTrade | None = None
        revised: list[SentinelOwnedTrade] = []
        for trade in self._sentinel_trade_ledger:
            if self._trade_matches_position_ticket(trade, position_snapshot.ticket):
                updated_trade = replace(
                    trade,
                    symbol=position_snapshot.symbol or trade.symbol,
                    direction=position_snapshot.direction or trade.direction,
                    position_ticket=position_snapshot.ticket,
                    entry_price=position_snapshot.open_price or trade.entry_price,
                    stop_loss=position_snapshot.stop_loss if position_snapshot.stop_loss is not None else trade.stop_loss,
                    take_profit=position_snapshot.take_profit if position_snapshot.take_profit is not None else trade.take_profit,
                    opened_at=position_snapshot.opened_at or trade.opened_at,
                    closed=False,
                    close_ticket=None,
                    close_profit=None,
                    close_result="NONE",
                    close_type="",
                    close_reason="",
                    closed_at=None,
                    history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
                    pending_close=False,
                    pending_close_since=None,
                )
                revised.append(updated_trade)
            else:
                revised.append(trade)
        if updated_trade is not None:
            self._sentinel_trade_ledger = revised
            return updated_trade
        return None

    @staticmethod
    def _trade_matches_position_ticket(trade: SentinelOwnedTrade, position_ticket: int | None) -> bool:
        """Return whether a ledger record refers to a still-open MT5 position ticket."""
        if position_ticket is None:
            return False
        return int(position_ticket) in {
            int(ticket)
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket, trade.close_ticket)
            if ticket is not None
        }

    def _sentinel_owned_ticket(self) -> int | None:
        """Return the most reliable Sentinel-owned trade ticket."""
        if self._sentinel_owned_trade is None:
            return None
        return (
            self._sentinel_owned_trade.position_ticket
            or self._sentinel_owned_trade.order_ticket
            or self._sentinel_owned_trade.deal_ticket
        )

    def _sentinel_owned_tickets(self) -> tuple[int, ...]:
        """Return all persisted Sentinel-owned ticket references for ledger statistics."""
        values: list[int] = []
        for trade in self._sentinel_trade_ledger:
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket):
                if ticket is not None:
                    values.append(int(ticket))
        return tuple(sorted({ticket for ticket in values if ticket > 0}))

    def _is_position_sentinel_owned(self, position_snapshot: PositionMonitorSnapshot) -> bool:
        """Return whether the active MT5 position belongs to Sentinel AI."""
        if self._sentinel_owned_trade is None or self._sentinel_owned_trade.closed:
            return False
        if not position_snapshot.has_open_position or position_snapshot.symbol != self._sentinel_owned_trade.symbol:
            return False
        owned_ticket = self._sentinel_owned_ticket()
        ticket_matches = owned_ticket is not None and position_snapshot.ticket == owned_ticket
        close_ticket_matches = (
            self._sentinel_owned_trade.close_ticket is not None
            and position_snapshot.ticket == self._sentinel_owned_trade.close_ticket
        )
        manual_magic = int(self._context.config.manual_trading.magic_number)
        magic_matches = position_snapshot.magic_number is not None and int(position_snapshot.magic_number) == manual_magic
        return ticket_matches or close_ticket_matches or magic_matches

    def _current_resolution_opened_at(self) -> datetime | None:
        """Return the active or pending Sentinel trade open time for close-history resolution."""
        if self._sentinel_owned_trade is not None:
            return self._sentinel_owned_trade.opened_at
        candidates = [
            trade
            for trade in self._sentinel_trade_ledger
            if trade.symbol == self._active_symbol and not trade.closed
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda trade: trade.opened_at)[-1].opened_at

    def _sentinel_owned_daily_statistics(
        self,
        position_snapshot: PositionMonitorSnapshot,
        magic_number: int,
    ) -> DailyTradeStatisticsSnapshot:
        """Return Sentinel-only statistics while guarding active tickets from false close results."""
        if position_snapshot.has_open_position and self._is_position_sentinel_owned(position_snapshot):
            return self._active_trade_guard_statistics(position_snapshot)

        sentinel_comment = self._context.config.manual_trading.order_comment
        owned_tickets = self._sentinel_owned_tickets()
        if owned_tickets:
            snapshot = self._context.mt5_service.daily_trade_statistics(
                symbol=self._active_symbol,
                magic_number=magic_number,
                owned_position_ticket=self._sentinel_owned_ticket(),
                owned_position_tickets=owned_tickets,
                sentinel_owned_only=True,
                sentinel_comment=sentinel_comment,
                owned_trade_opened_at=self._current_resolution_opened_at(),
                settlement_search_hours=168,
            )
        else:
            snapshot = self._context.mt5_service.daily_trade_statistics(
                symbol=self._active_symbol,
                magic_number=magic_number,
                owned_position_ticket=None,
                owned_position_tickets=None,
                sentinel_owned_only=True,
                sentinel_comment=sentinel_comment,
                owned_trade_opened_at=self._current_resolution_opened_at(),
                settlement_search_hours=168,
            )
        self._sync_ledger_with_statistics(snapshot)
        return self._statistics_with_ledger_totals(snapshot)

    def _active_trade_guard_statistics(self, position_snapshot: PositionMonitorSnapshot) -> DailyTradeStatisticsSnapshot:
        """Build a zero-closed-trade statistics snapshot for a still-open Sentinel ticket."""
        snapshot = DailyTradeStatisticsSnapshot(
            symbol=position_snapshot.symbol,
            total_closed_trades=0,
            wins=0,
            losses=0,
            breakeven=0,
            win_rate=0.0,
            loss_rate=0.0,
            net_profit=0.0,
            generated_at=datetime.now(timezone.utc),
            message="Sentinel active ticket guard: open position is not counted as closed.",
            last_closed_ticket=None,
            last_closed_profit=None,
            last_closed_result="NONE",
            last_closed_at=None,
            last_close_reason="",
            last_close_type="",
            history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
            sentinel_owned_only=True,
            result_status="1 Sentinel trade open. Waiting for close result.",
        )
        return self._statistics_with_ledger_totals(snapshot)

    def _close_sentinel_owned_trade(self, statistics: DailyTradeStatisticsSnapshot, close_ticket: int | None) -> None:
        """Persist the close result into the Sentinel trade ledger."""
        if self._sentinel_owned_trade is None:
            return
        self._sentinel_owned_trade = self._trade_with_close_result(
            trade=self._sentinel_owned_trade,
            statistics=statistics,
            close_ticket=close_ticket,
        )
        self._upsert_sentinel_trade(self._sentinel_owned_trade)
        self._save_sentinel_owned_trade()
        self._close_prediction_for_trade(self._sentinel_owned_trade)

    def _mark_sentinel_trade_pending_close(self) -> None:
        """Mark the active Sentinel trade as pending close while MT5 history settles."""
        if self._sentinel_owned_trade is None or self._sentinel_owned_trade.closed:
            return
        pending_since = self._sentinel_owned_trade.pending_close_since or datetime.now(timezone.utc)
        self._sentinel_owned_trade = replace(
            self._sentinel_owned_trade,
            pending_close=True,
            pending_close_since=pending_since,
            history_match_mode="SENTINEL_PENDING_CLOSE",
        )
        self._upsert_sentinel_trade(self._sentinel_owned_trade)
        self._save_sentinel_owned_trade()

    def _sync_ledger_with_statistics(self, statistics: DailyTradeStatisticsSnapshot) -> None:
        """Update persisted ledger records when MT5 reports a Sentinel-owned close."""
        if statistics.last_closed_result == "NONE" or statistics.last_closed_ticket is None:
            return
        if self._tracked_active_position_ticket is not None and int(statistics.last_closed_ticket) == int(self._tracked_active_position_ticket):
            self._context.logger.info(
                "Ignored false close result for still-active Sentinel ticket: %s",
                statistics.last_closed_ticket,
            )
            return
        updated = False
        revised: list[SentinelOwnedTrade] = []
        for trade in self._sentinel_trade_ledger:
            if self._trade_matches_close_ticket(trade, statistics.last_closed_ticket) or self._trade_can_accept_resolved_close(trade, statistics):
                revised.append(
                    self._trade_with_close_result(
                        trade=trade,
                        statistics=statistics,
                        close_ticket=statistics.last_closed_ticket,
                    )
                )
                updated = True
            else:
                revised.append(trade)
        if updated:
            self._sentinel_trade_ledger = revised
            for revised_trade in revised:
                if revised_trade.closed and revised_trade.close_result != "NONE":
                    self._close_prediction_for_trade(revised_trade)
            if self._sentinel_owned_trade is not None and (
                self._trade_matches_close_ticket(self._sentinel_owned_trade, statistics.last_closed_ticket)
                or self._trade_can_accept_resolved_close(self._sentinel_owned_trade, statistics)
            ):
                self._sentinel_owned_trade = self._trade_with_close_result(
                    trade=self._sentinel_owned_trade,
                    statistics=statistics,
                    close_ticket=statistics.last_closed_ticket,
                )
            self._save_sentinel_trade_ledger()

    def _close_prediction_for_trade(self, trade: SentinelOwnedTrade) -> None:
        """Close a linked prediction record when a Sentinel ledger result is verified."""
        self._context.prediction_lifecycle_service.close_from_ledger_result(
            prediction_uid=trade.prediction_uid,
            close_result=trade.close_result,
            close_type=trade.close_type,
        )

    @staticmethod
    def _trade_with_close_result(
        trade: SentinelOwnedTrade,
        statistics: DailyTradeStatisticsSnapshot,
        close_ticket: int | None,
    ) -> SentinelOwnedTrade:
        """Return a ledger trade updated with a closed-trade outcome."""
        return replace(
            trade,
            closed=True,
            close_ticket=close_ticket,
            close_profit=statistics.last_closed_profit,
            close_result=statistics.last_closed_result,
            close_type=statistics.last_close_type,
            close_reason=statistics.last_close_reason,
            closed_at=statistics.last_closed_at or datetime.now(timezone.utc),
            history_match_mode=statistics.history_match_mode,
            pending_close=False,
            pending_close_since=None,
        )

    @staticmethod
    def _trade_matches_close_ticket(trade: SentinelOwnedTrade, close_ticket: int | None) -> bool:
        """Return whether a ledger trade matches a broker close ticket or position id."""
        if close_ticket is None:
            return False
        return int(close_ticket) in {
            int(ticket)
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket, trade.close_ticket)
            if ticket is not None
        }

    def _trade_can_accept_resolved_close(
        self,
        trade: SentinelOwnedTrade,
        statistics: DailyTradeStatisticsSnapshot,
    ) -> bool:
        """Return True when the latest pending trade can accept a resolved Sentinel close deal."""
        if trade.closed or statistics.last_closed_result == "NONE":
            return False
        if trade.symbol != statistics.symbol or not trade.pending_close:
            return False
        pending_same_symbol = [
            candidate
            for candidate in self._sentinel_trade_ledger
            if candidate.symbol == trade.symbol and candidate.pending_close and not candidate.closed
        ]
        if not pending_same_symbol:
            return False
        latest_pending = sorted(
            pending_same_symbol,
            key=lambda item: item.pending_close_since or item.opened_at,
        )[-1]
        return self._sentinel_trade_key(trade) == self._sentinel_trade_key(latest_pending)

    def _statistics_with_ledger_totals(self, snapshot: DailyTradeStatisticsSnapshot) -> DailyTradeStatisticsSnapshot:
        """Overlay ledger totals with current-trade priority and stale backlog separation."""
        ledger_records = list(self._sentinel_trade_ledger)
        open_trades = [trade for trade in ledger_records if not trade.closed and not trade.pending_close]
        pending_records = [trade for trade in ledger_records if not trade.closed and trade.pending_close]
        stale_pending_trades = [trade for trade in pending_records if self._is_pending_trade_stale(trade)]
        current_pending_trades = [trade for trade in pending_records if not self._is_pending_trade_stale(trade)]
        closed_trades = [trade for trade in ledger_records if trade.closed and trade.close_result != "NONE"]

        ledger_total_records = len(ledger_records)
        ledger_open = len(open_trades)
        ledger_pending = len(current_pending_trades)
        pending_backlog = len(stale_pending_trades)
        stale_pending_count = len(stale_pending_trades)
        ledger_closed = len(closed_trades)
        ledger_wins = len([trade for trade in closed_trades if trade.close_result == "WIN"])
        ledger_losses = len([trade for trade in closed_trades if trade.close_result == "LOSS"])
        ledger_breakeven = len([trade for trade in closed_trades if trade.close_result == "BREAKEVEN"])
        ledger_net_profit = sum(float(trade.close_profit or 0.0) for trade in closed_trades)
        ledger_win_rate = (ledger_wins / ledger_closed * 100.0) if ledger_closed else 0.0

        diagnostic_pending_trades = current_pending_trades if current_pending_trades else stale_pending_trades
        lifecycle_stage = self._ledger_lifecycle_stage(ledger_open, ledger_pending, ledger_closed, ledger_total_records)
        tracked_ticket = self._diagnostic_tracked_ticket(open_trades, diagnostic_pending_trades, closed_trades)
        pending_age_seconds = self._pending_close_age_seconds(current_pending_trades)
        close_resolver_status = self._close_resolver_status(snapshot, ledger_open, ledger_pending, pending_age_seconds)
        audit_warning = self._audit_warning(snapshot, ledger_open, ledger_pending, stale_pending_count, pending_age_seconds)
        ledger_health = self._ledger_health_status(ledger_open, ledger_pending, stale_pending_count, ledger_closed, ledger_total_records)
        result_status = self._ledger_result_status(snapshot, ledger_open, ledger_pending, ledger_closed, ledger_total_records)
        if ledger_open > 0 and pending_backlog > 0:
            result_status = f"{ledger_open} Sentinel trade open. Waiting for close result. | Stale backlog: {pending_backlog}"

        today_closed = [trade for trade in closed_trades if self._is_trade_closed_today(trade)]
        if today_closed:
            today_total = len(today_closed)
            today_wins = len([trade for trade in today_closed if trade.close_result == "WIN"])
            today_losses = len([trade for trade in today_closed if trade.close_result == "LOSS"])
            today_breakeven = len([trade for trade in today_closed if trade.close_result == "BREAKEVEN"])
            today_net_profit = sum(float(trade.close_profit or 0.0) for trade in today_closed)
            today_win_rate = (today_wins / today_total * 100.0) if today_total else 0.0
            today_loss_rate = (today_losses / today_total * 100.0) if today_total else 0.0
            latest_trade = sorted(today_closed, key=lambda trade: trade.closed_at or trade.opened_at)[-1]
            if ledger_open == 0 and ledger_pending == 0 and pending_backlog == 0:
                result_status = f"Latest closed Sentinel trade: {latest_trade.close_result} {float(latest_trade.close_profit or 0.0):.2f}"
            snapshot = replace(
                snapshot,
                total_closed_trades=today_total,
                wins=today_wins,
                losses=today_losses,
                breakeven=today_breakeven,
                win_rate=today_win_rate,
                loss_rate=today_loss_rate,
                net_profit=today_net_profit,
                message=(
                    f"Ledger today: {today_total} | Wins {today_wins} | Losses {today_losses} | "
                    f"Net P/L {today_net_profit:.2f}"
                ),
                last_closed_ticket=latest_trade.close_ticket or latest_trade.position_ticket,
                last_closed_profit=latest_trade.close_profit,
                last_closed_result=latest_trade.close_result,
                last_closed_at=latest_trade.closed_at,
                last_close_reason=latest_trade.close_reason,
                last_close_type=latest_trade.close_type,
                history_match_mode=latest_trade.history_match_mode or snapshot.history_match_mode,
            )

        return replace(
            snapshot,
            ledger_total_trades=ledger_closed,
            ledger_open_trades=ledger_open,
            ledger_pending_close_trades=ledger_pending,
            ledger_closed_trades=ledger_closed,
            ledger_total_records=ledger_total_records,
            ledger_wins=ledger_wins,
            ledger_losses=ledger_losses,
            ledger_breakeven=ledger_breakeven,
            ledger_win_rate=ledger_win_rate,
            ledger_net_profit=ledger_net_profit,
            result_status=result_status,
            lifecycle_stage=lifecycle_stage,
            tracked_sentinel_ticket=tracked_ticket,
            pending_close_age_seconds=pending_age_seconds,
            close_resolver_status=close_resolver_status,
            audit_warning=audit_warning,
            pending_backlog_trades=pending_backlog,
            stale_pending_trades=stale_pending_count,
            ledger_health=ledger_health,
            build_stage="STAGE_5_TRADE_RESULT_VERIFICATION_COMPLETE",
            completion_status="MANUAL_MODE_FOUNDATION_COMPLETE_AUTO_TRADE_LOCKED",
        )

    @staticmethod
    def _ledger_lifecycle_stage(
        ledger_open: int,
        ledger_pending: int,
        ledger_closed: int,
        ledger_total_records: int,
    ) -> str:
        """Return the current lifecycle stage, prioritizing the current active Sentinel trade."""
        if ledger_open > 0:
            return "ACTIVE_OPEN"
        if ledger_pending > 0:
            return "PENDING_CLOSE_SETTLEMENT"
        if ledger_closed > 0:
            return "CLOSED_VERIFIED"
        if ledger_total_records > 0:
            return "LEDGER_UNVERIFIED"
        return "NO_SENTINEL_TRADE"

    def _diagnostic_tracked_ticket(
        self,
        open_trades: list[SentinelOwnedTrade],
        pending_trades: list[SentinelOwnedTrade],
        closed_trades: list[SentinelOwnedTrade],
    ) -> int | None:
        """Return the most useful Sentinel ticket for dashboard diagnostics."""
        if self._sentinel_owned_ticket() is not None:
            return self._sentinel_owned_ticket()
        for group in (open_trades, pending_trades, closed_trades):
            if group:
                trade = sorted(group, key=lambda item: item.closed_at or item.pending_close_since or item.opened_at)[-1]
                for ticket in (trade.position_ticket, trade.close_ticket, trade.order_ticket, trade.deal_ticket):
                    if ticket is not None:
                        return int(ticket)
        return None

    @staticmethod
    def _pending_close_age_seconds(pending_trades: list[SentinelOwnedTrade]) -> int:
        """Return the age in seconds of the oldest pending close record."""
        if not pending_trades:
            return 0
        now = datetime.now(timezone.utc)
        ages: list[int] = []
        for trade in pending_trades:
            pending_since = trade.pending_close_since
            if pending_since is None:
                continue
            if pending_since.tzinfo is None:
                pending_since = pending_since.replace(tzinfo=timezone.utc)
            ages.append(max(0, int((now - pending_since).total_seconds())))
        return max(ages) if ages else 0

    @staticmethod
    def _close_resolver_status(
        snapshot: DailyTradeStatisticsSnapshot,
        ledger_open: int,
        ledger_pending: int,
        pending_age_seconds: int,
    ) -> str:
        """Return a concise close resolver status while prioritizing the current active trade."""
        if snapshot.last_closed_result != "NONE":
            return f"Resolved by {snapshot.history_match_mode or 'MT5_HISTORY'}"
        if ledger_open > 0:
            return "Idle: current Sentinel trade is still open"
        if ledger_pending > 0:
            if pending_age_seconds >= 180:
                return "Resolving: extended MT5 history scan active"
            return "Resolving: waiting for MT5 close deal"
        if snapshot.history_match_mode:
            return snapshot.history_match_mode
        return "-"

    def _audit_warning(
        self,
        snapshot: DailyTradeStatisticsSnapshot,
        ledger_open: int,
        ledger_pending: int,
        stale_pending_count: int,
        pending_age_seconds: int,
    ) -> str:
        """Return a warning only when the lifecycle state needs user attention."""
        if snapshot.last_closed_result != "NONE":
            return "-"
        if stale_pending_count > 0:
            return f"{stale_pending_count} stale pending Sentinel trade(s) need history review."
        if ledger_open == 0 and ledger_pending > 0 and pending_age_seconds >= self._pending_stale_seconds:
            return "Close result not resolved after 5 minutes. Check MT5 Account History visibility."
        return "-"

    def _ledger_health_status(
        self,
        ledger_open: int,
        ledger_pending: int,
        stale_pending_count: int,
        ledger_closed: int,
        ledger_total_records: int,
    ) -> str:
        """Return a compact ledger health status for the dashboard."""
        if ledger_total_records == 0:
            return "EMPTY"
        if ledger_open > 0 and stale_pending_count > 0:
            return "CURRENT_ACTIVE_WITH_STALE_PENDING_BACKLOG"
        if ledger_open > 0:
            return "CURRENT_ACTIVE_OK"
        if stale_pending_count > 0:
            return "STALE_PENDING_REVIEW_REQUIRED"
        if ledger_pending > 0:
            return "PENDING_CLOSE_SETTLEMENT"
        if ledger_closed > 0:
            return "VERIFIED"
        return "UNVERIFIED"

    def _stale_pending_trade_count(self, pending_trades: list[SentinelOwnedTrade]) -> int:
        """Count pending trades older than the stale threshold."""
        return len([trade for trade in pending_trades if self._is_pending_trade_stale(trade)])

    def _is_pending_trade_stale(self, trade: SentinelOwnedTrade) -> bool:
        """Return whether a pending-close record is old enough to be treated as backlog."""
        pending_since = trade.pending_close_since
        if pending_since is None:
            return False
        if pending_since.tzinfo is None:
            pending_since = pending_since.replace(tzinfo=timezone.utc)
        age_seconds = int((datetime.now(timezone.utc) - pending_since).total_seconds())
        return age_seconds >= self._pending_stale_seconds

    @staticmethod
    def _ledger_result_status(
        snapshot: DailyTradeStatisticsSnapshot,
        ledger_open: int,
        ledger_pending: int,
        ledger_closed: int,
        ledger_total_records: int,
    ) -> str:
        """Return result status, prioritizing the current active Sentinel trade over old pending backlog."""
        if snapshot.last_closed_result != "NONE":
            profit = f"{snapshot.last_closed_profit:.2f}" if snapshot.last_closed_profit is not None else "-"
            return f"Closed result verified: {snapshot.last_closed_result} {profit}"
        if ledger_open > 0:
            backlog = f" | Stale backlog: {ledger_pending}" if ledger_pending > 0 else ""
            return f"{ledger_open} Sentinel trade open. Waiting for close result.{backlog}"
        if ledger_pending > 0:
            return f"{ledger_pending} Sentinel trade pending close result. Waiting for MT5 history settlement."
        if ledger_closed > 0:
            return f"{ledger_closed} closed Sentinel trade(s) saved in ledger."
        if ledger_total_records > 0:
            return "Ledger records found, but no verified closed outcome yet."
        return "No Sentinel ledger trades recorded yet."

    @staticmethod
    def _is_trade_closed_today(trade: SentinelOwnedTrade) -> bool:
        """Return whether a persisted trade closed on the current UTC date."""
        if trade.closed_at is None:
            return False
        now = datetime.now(timezone.utc)
        closed_at = trade.closed_at if trade.closed_at.tzinfo is not None else trade.closed_at.replace(tzinfo=timezone.utc)
        return closed_at.date() == now.date()

    def _empty_sentinel_statistics(self, message: str, match_mode: str) -> DailyTradeStatisticsSnapshot:
        """Build an empty Sentinel-only statistics snapshot."""
        return DailyTradeStatisticsSnapshot(
            symbol=self._active_symbol,
            total_closed_trades=0,
            wins=0,
            losses=0,
            breakeven=0,
            win_rate=0.0,
            loss_rate=0.0,
            net_profit=0.0,
            generated_at=datetime.now(timezone.utc),
            message=message,
            history_match_mode=match_mode,
            sentinel_owned_only=True,
        )

    def _sentinel_trade_store_path(self) -> Path:
        """Return the legacy latest Sentinel-owned trade journal path."""
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / ".sentinel_ai"
        return base_path / "SentinelAI" / "sentinel_owned_trade.json"

    def _sentinel_trade_ledger_path(self) -> Path:
        """Return the persistent Sentinel trade ledger path."""
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / ".sentinel_ai"
        return base_path / "SentinelAI" / "sentinel_trade_ledger.json"

    def _load_sentinel_owned_trade(self) -> SentinelOwnedTrade | None:
        """Load the legacy latest Sentinel-owned trade from local JSON persistence."""
        path = self._sentinel_trade_store_path()
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            trade = SentinelOwnedTrade.from_dict(payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            self._context.logger.warning("Sentinel-owned trade journal load failed: %s", error)
            return None
        if trade.source not in {"SENTINEL_APP_MANUAL", "SENTINEL_APP_AUTO"}:
            return None
        self._context.logger.info("Loaded legacy Sentinel-owned trade journal: %s", trade)
        return trade

    def _sentinel_archived_ledger_path(self) -> Path:
        """Return the archived stale Sentinel trade ledger path."""
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / ".sentinel_ai"
        return base_path / "SentinelAI" / "sentinel_trade_ledger_archived_stale.json"

    def _sentinel_ledger_export_dir(self) -> Path:
        """Return the local export directory for ledger maintenance files."""
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / ".sentinel_ai"
        return base_path / "SentinelAI" / "exports"

    def _load_sentinel_trade_ledger(self) -> list[SentinelOwnedTrade]:
        """Load all persisted Sentinel-created trades from the local ledger."""
        path = self._sentinel_trade_ledger_path()
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self._context.logger.warning("Sentinel trade ledger load failed: %s", error)
            return []
        if not isinstance(payload, list):
            return []
        trades: list[SentinelOwnedTrade] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                trade = SentinelOwnedTrade.from_dict(item)
            except (TypeError, ValueError):
                continue
            if trade.source in {"SENTINEL_APP_MANUAL", "SENTINEL_APP_AUTO"}:
                trades.append(trade)
        self._context.logger.info("Loaded %s Sentinel trade ledger records.", len(trades))
        return trades

    def _save_sentinel_owned_trade(self) -> None:
        """Save the latest Sentinel-owned trade and the full ledger."""
        if self._sentinel_owned_trade is not None:
            path = self._sentinel_trade_store_path()
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(self._sentinel_owned_trade.to_dict(), indent=2), encoding="utf-8")
            except OSError as error:
                self._context.logger.warning("Sentinel-owned trade journal save failed: %s", error)
        self._save_sentinel_trade_ledger()

    def _save_sentinel_trade_ledger(self) -> None:
        """Save every Sentinel-created trade to the persistent ledger."""
        path = self._sentinel_trade_ledger_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = [trade.to_dict() for trade in self._sentinel_trade_ledger]
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as error:
            self._context.logger.warning("Sentinel trade ledger save failed: %s", error)

    def _select_active_sentinel_trade(self) -> SentinelOwnedTrade | None:
        """Return the latest open Sentinel trade from the ledger for monitoring after restart."""
        open_trades = [trade for trade in self._sentinel_trade_ledger if not trade.closed and trade.symbol == self._active_symbol]
        if not open_trades:
            return None
        return sorted(open_trades, key=lambda trade: trade.opened_at)[-1]

    def _upsert_sentinel_trade(self, trade: SentinelOwnedTrade) -> None:
        """Insert or update one trade in the persistent Sentinel ledger."""
        key = self._sentinel_trade_key(trade)
        updated = False
        revised: list[SentinelOwnedTrade] = []
        for existing in self._sentinel_trade_ledger:
            if self._sentinel_trade_key(existing) == key or self._trades_share_ticket(existing, trade):
                revised.append(trade)
                updated = True
            else:
                revised.append(existing)
        if not updated:
            revised.append(trade)
        self._sentinel_trade_ledger = revised

    @staticmethod
    def _sentinel_trade_key(trade: SentinelOwnedTrade) -> str:
        """Build a stable local key for a Sentinel-created trade."""
        for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket):
            if ticket is not None:
                return f"{trade.symbol}:{ticket}"
        return f"{trade.symbol}:{trade.direction}:{trade.opened_at.isoformat()}"

    @staticmethod
    def _trades_share_ticket(first: SentinelOwnedTrade, second: SentinelOwnedTrade) -> bool:
        """Return whether two ledger entries refer to the same broker ticket family."""
        first_tickets = {
            int(ticket)
            for ticket in (first.position_ticket, first.order_ticket, first.deal_ticket, first.close_ticket)
            if ticket is not None
        }
        second_tickets = {
            int(ticket)
            for ticket in (second.position_ticket, second.order_ticket, second.deal_ticket, second.close_ticket)
            if ticket is not None
        }
        return bool(first_tickets and second_tickets and first_tickets & second_tickets)

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
        """Return open, current pending, stale pending, closed, and total ledger counts."""
        open_count = 0
        current_pending_count = 0
        stale_count = 0
        closed_count = 0
        for trade in self._sentinel_trade_ledger:
            if trade.closed and trade.close_result != "NONE":
                closed_count += 1
            elif trade.pending_close:
                if self._is_pending_trade_stale(trade):
                    stale_count += 1
                else:
                    current_pending_count += 1
            else:
                open_count += 1
        return open_count, current_pending_count, stale_count, closed_count, len(self._sentinel_trade_ledger)

    def _repair_pending_history_records(self) -> None:
        """Attempt to repair unresolved pending ledger records from MT5 history."""
        pending_records = [
            trade
            for trade in self._sentinel_trade_ledger
            if trade.pending_close and not trade.closed
        ]
        if not pending_records:
            QMessageBox.information(self._main_window, "Ledger Maintenance", "No pending records to repair.")
            return

        repaired = 0
        unresolved = 0
        revised: list[SentinelOwnedTrade] = []
        repaired_keys: set[str] = set()
        for trade in self._sentinel_trade_ledger:
            if not (trade.pending_close and not trade.closed):
                revised.append(trade)
                continue
            statistics = self._resolve_single_pending_trade_from_history(trade)
            if statistics is not None and statistics.last_closed_result != "NONE":
                revised.append(
                    self._trade_with_close_result(
                        trade=trade,
                        statistics=statistics,
                        close_ticket=statistics.last_closed_ticket or trade.position_ticket,
                    )
                )
                repaired += 1
                repaired_keys.add(self._sentinel_trade_key(trade))
            else:
                revised.append(trade)
                unresolved += 1

        self._sentinel_trade_ledger = revised
        for revised_trade in revised:
            if revised_trade.closed and revised_trade.close_result != "NONE":
                self._close_prediction_for_trade(revised_trade)
        if self._sentinel_owned_trade is not None and self._sentinel_trade_key(self._sentinel_owned_trade) in repaired_keys:
            self._sentinel_owned_trade = self._select_active_sentinel_trade()
        self._save_sentinel_owned_trade()
        self._update_position_monitoring()
        QMessageBox.information(
            self._main_window,
            "Ledger Maintenance",
            f"Pending history repair complete.\n\nRepaired: {repaired}\nStill unresolved: {unresolved}",
        )

    def _resolve_single_pending_trade_from_history(
        self,
        trade: SentinelOwnedTrade,
    ) -> DailyTradeStatisticsSnapshot | None:
        """Resolve one pending trade against MT5 history without touching current active positions."""
        try:
            manual_config = self._context.config.manual_trading
            tickets = self._trade_ticket_tuple(trade)
            statistics = self._context.mt5_service.daily_trade_statistics(
                symbol=trade.symbol,
                magic_number=manual_config.magic_number,
                owned_position_ticket=trade.position_ticket,
                owned_position_tickets=tickets,
                sentinel_owned_only=True,
                sentinel_comment=manual_config.order_comment,
                owned_trade_opened_at=trade.opened_at,
                settlement_search_hours=720,
            )
        except (Mt5ServiceError, ValueError) as error:
            self._context.logger.warning("Pending history repair failed for %s: %s", trade.position_ticket, error)
            return None
        if statistics.last_closed_result == "NONE":
            return None
        if not self._resolved_close_time_is_valid_for_trade(trade, statistics):
            self._context.logger.warning(
                "Pending repair rejected close result outside trade time window: trade=%s close=%s",
                trade.position_ticket,
                statistics.last_closed_at,
            )
            return None
        return statistics

    def _resolved_close_time_is_valid_for_trade(
        self,
        trade: SentinelOwnedTrade,
        statistics: DailyTradeStatisticsSnapshot,
    ) -> bool:
        """Guard repair so a later trade close is not assigned to an older pending record."""
        if statistics.last_closed_at is None:
            return bool(self._trade_matches_close_ticket(trade, statistics.last_closed_ticket))
        closed_at = statistics.last_closed_at if statistics.last_closed_at.tzinfo is not None else statistics.last_closed_at.replace(tzinfo=timezone.utc)
        opened_at = trade.opened_at if trade.opened_at.tzinfo is not None else trade.opened_at.replace(tzinfo=timezone.utc)
        if closed_at < opened_at:
            return False
        next_opened_at = self._next_trade_opened_at(trade)
        if next_opened_at is not None and closed_at > next_opened_at:
            return self._trade_matches_close_ticket(trade, statistics.last_closed_ticket)
        return True

    def _next_trade_opened_at(self, trade: SentinelOwnedTrade) -> datetime | None:
        """Return the next Sentinel ledger open time for the same symbol after the selected trade."""
        opened_at = trade.opened_at if trade.opened_at.tzinfo is not None else trade.opened_at.replace(tzinfo=timezone.utc)
        later_times: list[datetime] = []
        for candidate in self._sentinel_trade_ledger:
            if self._sentinel_trade_key(candidate) == self._sentinel_trade_key(trade):
                continue
            if candidate.symbol != trade.symbol:
                continue
            candidate_opened_at = candidate.opened_at if candidate.opened_at.tzinfo is not None else candidate.opened_at.replace(tzinfo=timezone.utc)
            if candidate_opened_at > opened_at:
                later_times.append(candidate_opened_at)
        return min(later_times) if later_times else None

    @staticmethod
    def _trade_ticket_tuple(trade: SentinelOwnedTrade) -> tuple[int, ...]:
        """Return all known MT5 ticket references for one Sentinel trade."""
        tickets = [
            trade.position_ticket,
            trade.order_ticket,
            trade.deal_ticket,
            trade.close_ticket,
        ]
        return tuple(sorted({int(ticket) for ticket in tickets if ticket is not None and int(ticket) > 0}))

    def _archive_stale_pending_records(self) -> None:
        """Archive stale pending records without touching open or current pending trades."""
        stale_records = [
            trade for trade in self._sentinel_trade_ledger
            if trade.pending_close and not trade.closed and self._is_pending_trade_stale(trade)
        ]
        if not stale_records:
            QMessageBox.information(self._main_window, "Ledger Maintenance", "No stale pending records to archive.")
            return

        archive_path = self._sentinel_archived_ledger_path()
        try:
            existing_archive: list[dict[str, object]] = []
            if archive_path.exists():
                loaded = json.loads(archive_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing_archive = [item for item in loaded if isinstance(item, dict)]
            existing_archive.extend(trade.to_dict() for trade in stale_records)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", f"Archive failed: {error}")
            return

        stale_keys = {self._sentinel_trade_key(trade) for trade in stale_records}
        self._sentinel_trade_ledger = [
            trade for trade in self._sentinel_trade_ledger
            if self._sentinel_trade_key(trade) not in stale_keys
        ]
        if self._sentinel_owned_trade is not None and self._sentinel_trade_key(self._sentinel_owned_trade) in stale_keys:
            self._sentinel_owned_trade = self._select_active_sentinel_trade()
        self._save_sentinel_owned_trade()
        self._update_position_monitoring()
        QMessageBox.information(
            self._main_window,
            "Ledger Maintenance",
            f"Archived {len(stale_records)} stale pending record(s).\n\nArchive: {archive_path}",
        )

    def _export_sentinel_ledger(self) -> None:
        """Export the Sentinel ledger to JSON and CSV files."""
        export_dir = self._sentinel_ledger_export_dir()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = export_dir / f"sentinel_trade_ledger_{timestamp}.json"
        csv_path = export_dir / f"sentinel_trade_ledger_{timestamp}.csv"
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            payload = [trade.to_dict() for trade in self._sentinel_trade_ledger]
            json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            headers = [
                "symbol", "direction", "order_ticket", "deal_ticket", "position_ticket",
                "entry_price", "stop_loss", "take_profit", "risk_reward_ratio",
                "confidence_percentage", "timeframe", "opened_at", "closed",
                "close_ticket", "close_profit", "close_result", "close_type",
                "close_reason", "closed_at", "history_match_mode", "pending_close",
                "pending_close_since",
            ]
            lines = [",".join(headers)]
            for trade in self._sentinel_trade_ledger:
                data = trade.to_dict()
                values = [self._csv_escape(data.get(header, "")) for header in headers]
                lines.append(",".join(values))
            csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", f"Export failed: {error}")
            return

        QMessageBox.information(
            self._main_window,
            "Ledger Maintenance",
            f"Export complete.\n\nJSON: {json_path}\nCSV: {csv_path}",
        )

    def _reset_test_ledger_guarded(self) -> None:
        """Reset test ledger only when no active Sentinel trade is open."""
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
        archive_path = self._sentinel_archived_ledger_path()
        try:
            existing_archive: list[dict[str, object]] = []
            if archive_path.exists():
                loaded = json.loads(archive_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing_archive = [item for item in loaded if isinstance(item, dict)]
            existing_archive.extend(trade.to_dict() for trade in self._sentinel_trade_ledger)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            QMessageBox.warning(self._main_window, "Ledger Maintenance", f"Reset archive failed: {error}")
            return
        self._sentinel_trade_ledger = []
        self._sentinel_owned_trade = None
        self._save_sentinel_owned_trade()
        self._update_position_monitoring()
        QMessageBox.information(self._main_window, "Ledger Maintenance", f"Test ledger reset complete. Archive: {archive_path}")

    @staticmethod
    def _csv_escape(value: object) -> str:
        """Escape one CSV cell without adding a new dependency."""
        text = "" if value is None else str(value)
        escaped = text.replace('"', '""')
        return f'"{escaped}"'

    def _handle_auto_trade_toggled(self, enabled: bool) -> None:
        """Enable or disable guarded auto-trade execution after explicit user confirmation."""
        if self._context.config.trading.auto_trade_locked:
            self._auto_trade_enabled = False
            self._main_window.set_auto_trade_state(False)
            self._main_window.update_runtime_status(
                "Auto Trade is locked until manual-mode lifecycle results are verified."
            )
            return
        if enabled:
            if self._latest_position_snapshot is not None and self._latest_position_snapshot.has_open_position:
                self._auto_trade_enabled = False
                self._main_window.set_auto_trade_state(False)
                QMessageBox.warning(
                    self._main_window,
                    "Auto Trade Blocked",
                    "Auto Trade cannot be enabled while a Sentinel trade is already open.",
                )
                return
            confirmation = QMessageBox.question(
                self._main_window,
                "Enable Auto Trade",
                (
                    "Auto Trade will place MT5 market orders automatically only when a BUY_READY or SELL_READY "
                    "plan passes the configured confidence and risk/reward checks.\n\n"
                    "Default safety remains one trade at a time. Continue?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirmation != QMessageBox.StandardButton.Yes:
                self._auto_trade_enabled = False
                self._main_window.set_auto_trade_state(False)
                return
            self._auto_trade_enabled = True
            self._last_auto_trade_plan_key = None
            self._main_window.update_runtime_status("Auto Trade enabled with guarded one-trade-at-a-time execution.")
        else:
            self._auto_trade_enabled = False
            self._main_window.update_runtime_status("Auto Trade disabled.")

    def _evaluate_auto_trade_after_analysis(self) -> None:
        """Place an automatic trade only when all guardrails pass."""
        if self._context.config.trading.auto_trade_locked:
            self._auto_trade_enabled = False
            self._last_auto_trade_plan_key = None
            return
        if not self._auto_trade_enabled:
            return
        snapshot = self._latest_risk_reward_snapshot
        if snapshot is None or snapshot.plan is None or not snapshot.plan.valid:
            return
        if snapshot.direction not in {"BUY_READY", "SELL_READY"}:
            return
        if self._latest_position_snapshot is not None and self._latest_position_snapshot.has_open_position:
            return
        if not self._auto_trade_plan_passes_guardrails(snapshot):
            return
        plan_key = self._auto_trade_plan_key(snapshot)
        if plan_key == self._last_auto_trade_plan_key:
            return

        result = self._place_manual_mt5_order(snapshot)
        self._manual_order_results.append(result)
        self._last_auto_trade_plan_key = plan_key
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
        """Return True when a ready plan passes configured auto-trade safety guardrails."""
        if snapshot.plan is None:
            return False
        trading_config = self._context.config.trading
        manual_config = self._context.config.manual_trading
        if trading_config.one_trade_at_a_time and self._latest_position_snapshot is not None and self._latest_position_snapshot.has_open_position:
            return False
        if float(snapshot.confidence_percentage) < float(trading_config.minimum_confidence):
            return False
        if float(snapshot.plan.risk_reward_ratio) < float(trading_config.default_risk_reward):
            return False
        if float(manual_config.default_volume) <= 0 or float(manual_config.default_volume) > float(manual_config.max_volume):
            return False
        return True

    @staticmethod
    def _auto_trade_plan_key(snapshot: RiskRewardSnapshot) -> str:
        """Return a stable key so the same ready plan is not submitted repeatedly."""
        if snapshot.plan is None:
            return "NO_PLAN"
        plan = snapshot.plan
        return (
            f"{snapshot.symbol}:{snapshot.timeframe}:{snapshot.direction}:"
            f"{round(float(plan.entry_price), 3)}:{round(float(plan.stop_loss), 3)}:"
            f"{round(float(plan.take_profit), 3)}:{round(float(snapshot.confidence_percentage), 2)}"
        )

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
