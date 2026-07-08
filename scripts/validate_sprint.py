"""
MODULE: OPS-001
FILE: OPS-001-001
Module Name: Sprint Validator
Version: 2.7.0
Purpose: Validates Sprint source syntax, resources, configuration loading, MT5 mapping, market feed conversion, chart assets, analysis engines, locked Auto Trade, prediction persistence, Auto Trade diagnostics, Trade Manager service extraction, and formal tests.
Dependencies: compileall, datetime, json, logging, pathlib, sys, pandas
Change History:
- 2.7.0: Added validation for Stage 8 TradeManagerService extraction and app delegation.
- 2.6.0: Added validation for Auto Trade diagnostics service, dashboard routing, prediction lifecycle service, and formal unit tests.
- 2.4.0: Added validation for guarded auto-trade execution engine and toolbar enablement.
- 2.3.0: Added validation for pending history repair tool and final manual-mode completion workflows.
- 2.2.0: Added validation for lenient close resolver and simplified dashboard rows.
- 2.1.0: Added validation for ledger maintenance tools, export, archive, and guarded reset workflows.
- 2.0.1: Added validation for pending-close/backlog separation and current settlement count.
- 2.0.0: Added validation for current trade priority, stale pending backlog, ledger health, and final stage dashboard fields.
- 1.9.0.2: Added AST validation that close resolver/audit helpers are bound inside SentinelApplication.
- 1.9.0.1: Added AST validation that robust close resolver methods are bound inside MetaTrader5Service.
- 1.9.0: Added validation for stabilization audit, robust close resolver, resolver status, and audit warning diagnostics.
- 1.8.4.1: Added validation for lifecycle result-status helper binding.
- 1.8.4: Added validation for lifecycle stage, tracked ticket, and pending close age diagnostics.
- 1.8.3: Added validation for pending close settlement state and dashboard row.
- 1.8.2: Added validation for active-ticket close guard and strict MT5 DEAL_ENTRY_OUT filtering.
- 1.8.1: Added validation for open/closed ledger counters and trade result verification dashboard rows.
- 1.8.0: Added validation for ledger close-result persistence and ledger performance dashboard rows.
- 1.7.5: Added validation for persistent Sentinel trade ledger and multi-ticket app-only statistics.
- 1.7.4: Added validation for persistent Sentinel-owned trade journal and magic/comment recovery.
- 1.7.3: Added validation for Sentinel-owned ticket-only statistics and outside MT5 trade suppression.
- 1.7.2: Added validation for countdown removal, MT5 history fallback matching, and close type display.
- 1.7.1.3: Added validation for timestamp normalization and live candle-cycle countdown synchronization.
- 1.7.1.2: Added validation for broker candle-open anchored countdown and no false full-duration reset.
- 1.7.1.1: Added validation for candle countdown wall-clock alignment and every-second repaint hotfix.
- 1.7.1: Added validation for timeframe-based chart candle countdown timer and active-header plan suppression.
- 1.7.0: Added validation for closed-trade lifecycle tracking and last result dashboard fields.
- 0.1.0: Added compile and resource validation for stable milestone handoff.
- 0.2.0: Added Sprint 2 configuration and MT5 timeframe mapper validation.
- 0.3.0: Added Sprint 3 market data feed validation using a deterministic gateway.
- 0.4.0: Added Sprint 4 embedded chart resource and payload serialization validation.
- 0.5.0: Added Sprint 5 live refresh service file and configuration validation.
- 0.5.1: Added validation for one-second refresh defaults and chart navigation runtime controls.
- 0.6.0: Added validation for symbol catalog models, contract methods, resolution service, and config persistence.
- 0.7.0: Added validation for market structure models, engine output, and chart marker runtime.
- 0.8.0: Added validation for support/resistance models, engine output, and chart zone runtime.
- 0.9.0: Added validation for persistent BOS markers and liquidity engine output.
- 0.9.1: Added bounded overlay segment validation for Sprint 9.1.
- 0.9.2: Added validation for BOS/COC structure events and imbalance overlays for Sprint 9.2.
- 0.9.3.1: Added validation for active-only overlay routing and fallback S/R range boxing.
- 0.9.3.2: Added validation for right-side future scrolling and coalesced chart redraw behavior.
- 0.9.3.3: Added validation for consolidation-only S/R range and overlay signature caching.
- 0.9.3.4: Added validation for close-based range invalidation and compact reason helpers.
- 1.0.0: Added validation for Momentum Engine models, configuration, service composition, and output.
- 1.1.0: Added validation for Confidence Engine models, configuration, service composition, and output.
- 1.1.1: Added validation that live refresh calls Confidence Engine after Momentum Engine.
- 1.2.0: Added validation for setup-only Entry Validation Engine models, configuration, service composition, and output.
- 1.2.1: Added validation for high-confidence structure-only setup alignment and precise WAIT reasons.
- 1.2.2: Added validation for pullback-aware setup behavior and pullback reason wording.
- 1.2.3: Added validation for neutral-momentum entry-zone setup allowance.
- 1.3.0: Added validation for Risk Reward Engine TP/SL and risk/reward output.
- 1.3.1: Added validation for smart TP candidate selection and TP rejection wording.
- 1.3.2: Added validation for rejected-plan display labeling and directional TP guard.
- 1.3.3: Added validation for extended TP target discovery from range, imbalance, and ATR projection.
- 1.4.0: Added validation for trade plan chart overlay, manual review gate, and no-execution confirmation modal.
- 1.4.1: Added validation for polished manual review modal, reviewed-plan snapshots, and no-order status message.
- 1.5.0: Added validation for user-confirmed manual MT5 order placement foundation.
- 1.5.1: Added validation for adaptive MT5 filling-mode fallback.
- 1.6.0: Added validation for position monitoring, daily trade statistics, and manual-trade lock.
- 1.6.2: Added validation for active-position protection status and missing SL/TP warnings.
- 1.6.1.2: Added validation for missing active-position TP/SL chart-scale protection.
- 1.6.1.1: Added validation for startup active-position lock initialization.
- 1.6.1: Added validation for active-position chart lock and position-priority display.
"""

from __future__ import annotations

import compileall
import json
import logging
import sys
import ast
import unittest
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def main() -> int:
    """Compile project source and verify required Sprint 9 BOS visibility and liquidity foundation components."""
    project_root = Path(__file__).resolve().parents[1]
    source_root = project_root / "src"
    required_files = [
        source_root / "sentinel_ai" / "resources" / "config" / "default_config.json",
        source_root / "sentinel_ai" / "resources" / "theme" / "dark_neon.json",
        source_root / "sentinel_ai" / "resources" / "chart" / "chart_view.html",
        source_root / "sentinel_ai" / "resources" / "chart" / "sentinel_chart_runtime.js",
        source_root / "sentinel_ai" / "mt5" / "mt5_service.py",
        source_root / "sentinel_ai" / "mt5" / "timeframe_mapper.py",
        source_root / "sentinel_ai" / "market_data" / "candle_validator.py",
        source_root / "sentinel_ai" / "market_data" / "lightweight_chart_feed.py",
        source_root / "sentinel_ai" / "market_data" / "market_data_feed.py",
        source_root / "sentinel_ai" / "market_data" / "market_refresh_service.py",
        source_root / "sentinel_ai" / "symbols" / "symbol_management_service.py",
        source_root / "sentinel_ai" / "models" / "symbol.py",
        source_root / "sentinel_ai" / "models" / "market_structure.py",
        source_root / "sentinel_ai" / "models" / "support_resistance.py",
        source_root / "sentinel_ai" / "models" / "liquidity.py",
        source_root / "sentinel_ai" / "models" / "imbalance.py",
        source_root / "sentinel_ai" / "models" / "momentum.py",
        source_root / "sentinel_ai" / "models" / "confidence.py",
        source_root / "sentinel_ai" / "models" / "entry_validation.py",
        source_root / "sentinel_ai" / "models" / "risk_reward.py",
        source_root / "sentinel_ai" / "models" / "trade_execution.py",
        source_root / "sentinel_ai" / "analysis" / "market_structure_engine.py",
        source_root / "sentinel_ai" / "analysis" / "support_resistance_engine.py",
        source_root / "sentinel_ai" / "analysis" / "liquidity_engine.py",
        source_root / "sentinel_ai" / "analysis" / "imbalance_engine.py",
        source_root / "sentinel_ai" / "analysis" / "momentum_engine.py",
        source_root / "sentinel_ai" / "analysis" / "confidence_engine.py",
        source_root / "sentinel_ai" / "analysis" / "entry_validation_engine.py",
        source_root / "sentinel_ai" / "analysis" / "risk_reward_engine.py",
        source_root / "sentinel_ai" / "services" / "prediction_lifecycle_service.py",
        source_root / "sentinel_ai" / "services" / "trade_manager_service.py",
        project_root / "tests" / "test_trading_config_lock.py",
        project_root / "tests" / "test_prediction_lifecycle_service.py",
        project_root / "tests" / "test_trade_manager_service.py",
        project_root / "SentinelAI.spec",
        project_root / "requirements.txt",
    ]

    missing_files = [path for path in required_files if not path.exists()]
    if missing_files:
        for path in missing_files:
            print(f"Missing required file: {path}", file=sys.stderr)
        return 1

    html_resource = (source_root / "sentinel_ai" / "resources" / "chart" / "chart_view.html").read_text(encoding="utf-8")
    runtime_resource = (source_root / "sentinel_ai" / "resources" / "chart" / "sentinel_chart_runtime.js").read_text(
        encoding="utf-8"
    )
    if "sentinel_chart_runtime.js" not in html_resource or "window.SentinelChart" not in runtime_resource:
        print("Embedded chart resources failed validation.", file=sys.stderr)
        return 1
    required_runtime_markers = ["mousedown", "wheel", "dblclick", "offsetFromRight", "resetViewToLatest", "setMarketStructure", "drawStructureMarkers", "setSupportResistance", "drawSupportResistanceZones", "setLiquidity", "drawLiquidityOverlays", "drawStructureBreakMarkers", "setImbalance", "drawImbalanceZones", "drawCombinedSupportResistanceRange", "MAX_FUTURE_EMPTY_SLOTS", "requestRender", "resolveActiveRangeBox", "lastSupportResistanceSignature", "closedBelowSupport", "closedAboveResistance", "assessConsolidationCandidate", "countSeparatedTouches", "renderDebounceTimer", "renderedActiveRange", "getContext(\"2d\", { alpha: false })"]
    if any(marker not in runtime_resource for marker in required_runtime_markers):
        print("Chart navigation runtime validation failed.", file=sys.stderr)
        return 1

    compiled = compileall.compile_dir(str(source_root), quiet=1)
    if not compiled:
        print("Python source compilation failed.", file=sys.stderr)
        return 1

    sys.path.insert(0, str(source_root))
    from sentinel_ai.analysis.confidence_engine import ConfidenceEngine
    from sentinel_ai.analysis.entry_validation_engine import EntryValidationEngine
    from sentinel_ai.analysis.imbalance_engine import ImbalanceEngine
    from sentinel_ai.analysis.liquidity_engine import LiquidityEngine
    from sentinel_ai.analysis.momentum_engine import MomentumEngine
    from sentinel_ai.analysis.risk_reward_engine import RiskRewardEngine
    from sentinel_ai.models.trade_execution import ManualTradeOrderRequest, ManualTradeOrderResult
    from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
    from sentinel_ai.models.sentinel_trade import SentinelOwnedTrade
    from sentinel_ai.services.trade_manager_service import TradeManagerService
    from sentinel_ai.analysis.market_structure_engine import MarketStructureEngine
    from sentinel_ai.analysis.support_resistance_engine import SupportResistanceEngine
    from sentinel_ai.config.config_service import ConfigService
    from sentinel_ai.market_data.candle_validator import CandleDataValidator
    from sentinel_ai.market_data.lightweight_chart_feed import LightweightChartFeedAdapter
    from sentinel_ai.market_data.market_data_feed import MarketDataFeedService
    from sentinel_ai.models.market import Mt5ConnectionStatus, SymbolValidationResult
    from sentinel_ai.models.symbol import SymbolCatalogItem
    from sentinel_ai.mt5.timeframe_mapper import Mt5TimeframeMapper
    from sentinel_ai.services.contracts import MarketDataServiceContract
    from sentinel_ai.symbols.symbol_management_service import SymbolManagementService

    class _DeterministicMarketDataGateway(MarketDataServiceContract):
        """Provide deterministic OHLCV data for Sprint validation without requiring MT5."""

        def connect(self) -> Mt5ConnectionStatus:
            """Return a connected validation status."""
            return Mt5ConnectionStatus(connected=True, message="Validation gateway connected.")

        def disconnect(self) -> None:
            """Disconnect the validation gateway."""
            return None

        def connection_status(self) -> Mt5ConnectionStatus:
            """Return the validation gateway status."""
            return Mt5ConnectionStatus(connected=True, message="Validation gateway active.")

        def account_snapshot(self) -> None:
            """Return no account details for the validation gateway."""
            return None

        def validate_symbol(self, symbol: str) -> SymbolValidationResult:
            """Return a valid symbol result only when the symbol exists in the validation catalog."""
            if symbol in {"XAUUSDm", "EURUSD"}:
                return SymbolValidationResult(symbol=symbol, valid=True, visible=True, selected=True, message="Validation symbol.")
            return SymbolValidationResult(symbol=symbol, valid=False, visible=False, selected=False, message="Validation symbol missing.")

        def list_symbols(self) -> tuple[SymbolCatalogItem, ...]:
            """Return deterministic symbols for symbol-management validation."""
            return (
                SymbolCatalogItem(
                    symbol="XAUUSDm",
                    description="Gold versus US Dollar",
                    path="Metals",
                    visible=True,
                    digits=2,
                    point=0.01,
                    currency_base="XAU",
                    currency_profit="USD",
                    trade_mode=4,
                ),
                SymbolCatalogItem(
                    symbol="EURUSD",
                    description="Euro versus US Dollar",
                    path="Forex/Majors",
                    visible=True,
                    digits=5,
                    point=0.00001,
                    currency_base="EUR",
                    currency_profit="USD",
                    trade_mode=4,
                ),
            )

        def search_symbols(self, query: str, limit: int) -> tuple[SymbolCatalogItem, ...]:
            """Return deterministic symbol search results."""
            clean_query = str(query).upper()
            matches = [item for item in self.list_symbols() if clean_query in item.symbol.upper()]
            return tuple(matches[: int(limit)])

        def place_manual_market_order(
            self,
            request: ManualTradeOrderRequest,
            one_position_per_symbol: bool,
        ) -> ManualTradeOrderResult:
            """Return a rejected validation result without touching MT5."""
            return ManualTradeOrderResult(
                accepted=False,
                symbol=request.symbol,
                direction=request.direction,
                volume=request.volume,
                requested_price=None,
                filled_price=None,
                stop_loss=request.stop_loss,
                take_profit=request.take_profit,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                comment=request.comment,
                message="validation gateway does not place orders",
                sent_at=datetime.now(timezone.utc),
            )

        def monitor_symbol_position(self, symbol: str, magic_number: int | None = None) -> PositionMonitorSnapshot:
            """Return a deterministic no-position snapshot."""
            return PositionMonitorSnapshot(
                symbol=symbol,
                has_open_position=False,
                ticket=None,
                direction="NONE",
                volume=0.0,
                open_price=None,
                current_price=None,
                stop_loss=None,
                take_profit=None,
                profit=0.0,
                swap=0.0,
                commission=0.0,
                magic_number=magic_number,
                comment="",
                opened_at=None,
                monitored_at=datetime.now(timezone.utc),
                message=f"No active Sentinel AI position for {symbol}.",
            )

        def daily_trade_statistics(
            self,
            symbol: str,
            magic_number: int | None = None,
            owned_position_ticket: int | None = None,
            owned_position_tickets: tuple[int, ...] | None = None,
            sentinel_owned_only: bool = True,
            sentinel_comment: str | None = None,
            owned_trade_opened_at: datetime | None = None,
            settlement_search_hours: int = 168,
        ) -> DailyTradeStatisticsSnapshot:
            """Return deterministic Sentinel-only statistics."""
            return DailyTradeStatisticsSnapshot(
                symbol=symbol,
                total_closed_trades=0,
                wins=0,
                losses=0,
                breakeven=0,
                win_rate=0.0,
                loss_rate=0.0,
                net_profit=0.0,
                generated_at=datetime.now(timezone.utc),
                message="No Sentinel app trade closed yet.",
                history_match_mode="SENTINEL_ONLY_NO_TICKET",
                sentinel_owned_only=sentinel_owned_only,
            )

        def fetch_ohlc(self, symbol: str, timeframe: str, bar_count: int | None = None) -> pd.DataFrame:
            """Return deterministic OHLCV candles using the canonical schema."""
            requested_count = int(bar_count or 3)
            base_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
            wave = (0.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0)
            records = []
            for index in range(requested_count):
                current_wave = wave[index % len(wave)]
                next_wave = wave[(index + 1) % len(wave)]
                base_price = 2000.0 + index * 0.03
                open_price = base_price + current_wave
                close_price = base_price + next_wave
                high_price = max(open_price, close_price) + 0.8
                low_price = min(open_price, close_price) - 0.8
                records.append(
                    {
                        "time": base_time + pd.Timedelta(minutes=5 * index),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "tick_volume": 100 + index,
                        "spread": 20,
                        "real_volume": 0,
                    }
                )
            return pd.DataFrame.from_records(records)

    config = ConfigService(config_path=project_root / ".validation_config.json").load()
    if "M5" not in Mt5TimeframeMapper.SUPPORTED_TIMEFRAMES:
        print("MT5 timeframe mapper validation failed.", file=sys.stderr)
        return 1
    if config.application.version != "2.7.0":
        print("Application version must be 2.7.0 for Sprint 2.7 Stage 8 Trade Manager service completion.", file=sys.stderr)
        return 1
    if not config.trading.auto_trade_locked:
        print("Auto Trade must remain locked for Sprint 2.7 Stage 8 Trade Manager service completion.", file=sys.stderr)
        return 1
    if config.market_data.default_feed_bar_count < 1:
        print("Market data configuration validation failed.", file=sys.stderr)
        return 1
    if not config.market_data.auto_refresh_enabled:
        print("Market refresh configuration should be enabled by default for Sprint 5.", file=sys.stderr)
        return 1
    if config.market_data.refresh_interval_for("M5") != 1:
        print("M5 refresh interval must be one second for Sprint 5.1.", file=sys.stderr)
        return 1
    if any(interval != 1 for interval in config.market_data.refresh_intervals_seconds.values()):
        print("All packaged refresh intervals must default to one second for Sprint 5.1.", file=sys.stderr)
        return 1

    refresh_service_resource = (source_root / "sentinel_ai" / "market_data" / "market_refresh_service.py").read_text(
        encoding="utf-8"
    )
    if "class MarketRefreshService" not in refresh_service_resource or "snapshot_refreshed" not in refresh_service_resource:
        print("Market refresh service validation failed.", file=sys.stderr)
        return 1

    feed_service = MarketDataFeedService(
        market_data_gateway=_DeterministicMarketDataGateway(),
        validator=CandleDataValidator(),
        chart_feed_adapter=LightweightChartFeedAdapter(),
        logger=logging.getLogger("sentinel_ai.validation"),
    )
    snapshot = feed_service.load_snapshot("XAUUSDm", "M5", 3)
    chart_payload = feed_service.chart_payload()
    if snapshot.candle_count != 3 or len(chart_payload) != 3:
        print("Market data feed validation failed.", file=sys.stderr)
        return 1


    symbol_service = SymbolManagementService(
        market_data_gateway=_DeterministicMarketDataGateway(),
        config_service=ConfigService(config_path=project_root / ".validation_symbol_config.json"),
        logger=logging.getLogger("sentinel_ai.validation.symbols"),
    )
    symbol_service.load_available_symbols()
    resolution = symbol_service.resolve_startup_symbol(
        configured_symbol="GOLDm#",
        preferred_aliases=("XAUUSD", "XAUUSDm"),
        auto_resolve_enabled=True,
    )
    if not resolution.resolved or resolution.active_symbol != "XAUUSDm":
        print("Symbol management resolution validation failed.", file=sys.stderr)
        return 1
    direct_resolution = symbol_service.activate_symbol("EURUSD")
    if not direct_resolution.resolved or direct_resolution.active_symbol != "EURUSD":
        print("Symbol activation validation failed.", file=sys.stderr)
        return 1

    if not config.market_structure.enabled or config.market_structure.swing_window != 2 or config.market_structure.max_bos_markers < 1:
        print("Market structure configuration validation failed.", file=sys.stderr)
        return 1

    structure_snapshot = MarketStructureEngine(
        config=config.market_structure,
        logger=logging.getLogger("sentinel_ai.validation.structure"),
    ).analyze(snapshot)
    if structure_snapshot.bias not in {"BULLISH", "BEARISH", "RANGING", "INSUFFICIENT_STRUCTURE"}:
        print("Market structure bias validation failed.", file=sys.stderr)
        return 1
    if structure_snapshot.analyzed_candle_count != snapshot.candle_count:
        print("Market structure candle-count validation failed.", file=sys.stderr)
        return 1
    if structure_snapshot.summary.strip() == "":
        print("Market structure summary validation failed.", file=sys.stderr)
        return 1
    if not hasattr(structure_snapshot, "historical_breaks"):
        print("Market structure historical BOS storage validation failed.", file=sys.stderr)
        return 1
    if structure_snapshot.historical_breaks and not hasattr(structure_snapshot.historical_breaks[0], "event_type"):
        print("Market structure BOS/COC event typing validation failed.", file=sys.stderr)
        return 1

    analysis_snapshot = feed_service.load_snapshot("XAUUSDm", "M5", 80)
    analysis_structure_snapshot = MarketStructureEngine(
        config=config.market_structure,
        logger=logging.getLogger("sentinel_ai.validation.structure.extended"),
    ).analyze(analysis_snapshot)
    support_resistance_snapshot = SupportResistanceEngine(
        config=config.support_resistance,
        logger=logging.getLogger("sentinel_ai.validation.support_resistance"),
    ).analyze(analysis_snapshot, analysis_structure_snapshot)
    if not config.support_resistance.enabled or config.support_resistance.max_chart_zones < 1:
        print("Support/resistance configuration validation failed.", file=sys.stderr)
        return 1
    if support_resistance_snapshot.summary.strip() == "":
        print("Support/resistance summary validation failed.", file=sys.stderr)
        return 1
    if support_resistance_snapshot.zone_tolerance_price <= 0:
        print("Support/resistance zone tolerance validation failed.", file=sys.stderr)
        return 1
    if not support_resistance_snapshot.all_zones:
        print("Support/resistance zone detection validation failed.", file=sys.stderr)
        return 1

    liquidity_snapshot = LiquidityEngine(
        config=config.liquidity,
        logger=logging.getLogger("sentinel_ai.validation.liquidity"),
    ).analyze(analysis_snapshot, analysis_structure_snapshot)
    if not config.liquidity.enabled or config.liquidity.max_chart_pools < 1 or config.liquidity.max_chart_sweeps < 1:
        print("Liquidity configuration validation failed.", file=sys.stderr)
        return 1
    if liquidity_snapshot.summary.strip() == "":
        print("Liquidity summary validation failed.", file=sys.stderr)
        return 1
    if not liquidity_snapshot.pools:
        print("Liquidity pool detection validation failed.", file=sys.stderr)
        return 1
    if not hasattr(liquidity_snapshot.pools[0], "segment_end_time"):
        print("Liquidity bounded segment model validation failed.", file=sys.stderr)
        return 1
    if support_resistance_snapshot.all_zones and not hasattr(support_resistance_snapshot.all_zones[0], "segment_start_time"):
        print("Support/resistance bounded segment model validation failed.", file=sys.stderr)
        return 1



    imbalance_snapshot = ImbalanceEngine(
        config=config.imbalance,
        logger=logging.getLogger("sentinel_ai.validation.imbalance"),
    ).analyze(analysis_snapshot, analysis_structure_snapshot)
    if not config.imbalance.enabled or config.imbalance.max_chart_fvg_zones < 1 or config.imbalance.max_chart_order_blocks < 1:
        print("Imbalance configuration validation failed.", file=sys.stderr)
        return 1
    if imbalance_snapshot.summary.strip() == "":
        print("Imbalance summary validation failed.", file=sys.stderr)
        return 1
    if not hasattr(imbalance_snapshot, "fair_value_gaps") or not hasattr(imbalance_snapshot, "order_blocks"):
        print("Imbalance snapshot shape validation failed.", file=sys.stderr)
        return 1

    momentum_snapshot = MomentumEngine(
        config=config.momentum,
        logger=logging.getLogger("sentinel_ai.validation.momentum"),
    ).analyze(analysis_snapshot)
    if not config.momentum.enabled or config.momentum.ema_slow_period <= config.momentum.ema_fast_period:
        print("Momentum configuration validation failed.", file=sys.stderr)
        return 1
    if momentum_snapshot.summary.strip() == "":
        print("Momentum summary validation failed.", file=sys.stderr)
        return 1
    if momentum_snapshot.bias not in {"BULLISH", "BEARISH", "LEAN_BULLISH", "LEAN_BEARISH", "NEUTRAL", "INSUFFICIENT_DATA"}:
        print("Momentum bias validation failed.", file=sys.stderr)
        return 1
    if momentum_snapshot.analyzed_candle_count != analysis_snapshot.candle_count:
        print("Momentum candle-count validation failed.", file=sys.stderr)
        return 1
    if momentum_snapshot.ema is None or momentum_snapshot.macd is None or momentum_snapshot.stochastic is None or momentum_snapshot.candle_momentum is None:
        print("Momentum component validation failed.", file=sys.stderr)
        return 1

    confidence_snapshot = ConfidenceEngine(
        config=config.confidence,
        logger=logging.getLogger("sentinel_ai.validation.confidence"),
    ).analyze(
        market_snapshot=analysis_snapshot,
        structure_snapshot=analysis_structure_snapshot,
        support_resistance_snapshot=support_resistance_snapshot,
        liquidity_snapshot=liquidity_snapshot,
        imbalance_snapshot=imbalance_snapshot,
        momentum_snapshot=momentum_snapshot,
    )
    if not config.confidence.enabled or config.confidence.high_context_threshold < config.confidence.medium_context_threshold:
        print("Confidence configuration validation failed.", file=sys.stderr)
        return 1
    if confidence_snapshot.direction != "WAIT":
        print("Confidence engine must not generate BUY/SELL direction in Sprint 11.", file=sys.stderr)
        return 1
    if not 0.0 <= confidence_snapshot.score_percentage <= 100.0:
        print("Confidence score range validation failed.", file=sys.stderr)
        return 1
    if confidence_snapshot.summary.strip() == "" or confidence_snapshot.reason.strip() == "":
        print("Confidence summary validation failed.", file=sys.stderr)
        return 1
    if len(confidence_snapshot.contributions) != 5:
        print("Confidence contribution validation failed.", file=sys.stderr)
        return 1

    entry_snapshot = EntryValidationEngine(
        config=config.entry_validation,
        logger=logging.getLogger("sentinel_ai.validation.entry_validation"),
    ).analyze(
        market_snapshot=analysis_snapshot,
        structure_snapshot=analysis_structure_snapshot,
        support_resistance_snapshot=support_resistance_snapshot,
        liquidity_snapshot=liquidity_snapshot,
        imbalance_snapshot=imbalance_snapshot,
        momentum_snapshot=momentum_snapshot,
        confidence_snapshot=confidence_snapshot,
    )
    if not config.entry_validation.enabled or config.entry_validation.minimum_setup_confidence < 0:
        print("Entry validation configuration failed.", file=sys.stderr)
        return 1
    if entry_snapshot.direction not in {"WAIT", "BUY_SETUP", "SELL_SETUP"}:
        print("Entry validation direction validation failed.", file=sys.stderr)
        return 1
    if entry_snapshot.direction in {"BUY_SETUP", "SELL_SETUP"} and entry_snapshot.entry_zone is None:
        print("Entry setup must include an entry zone.", file=sys.stderr)
        return 1
    if entry_snapshot.reason.strip() == "" or entry_snapshot.summary.strip() == "":
        print("Entry validation summary validation failed.", file=sys.stderr)
        return 1

    risk_reward_snapshot = RiskRewardEngine(
        config=config.risk_reward,
        logger=logging.getLogger("sentinel_ai.validation.risk_reward"),
    ).analyze(
        market_snapshot=analysis_snapshot,
        entry_snapshot=entry_snapshot,
        support_resistance_snapshot=support_resistance_snapshot,
        liquidity_snapshot=liquidity_snapshot,
        imbalance_snapshot=imbalance_snapshot,
    )
    if not config.risk_reward.enabled or config.risk_reward.minimum_risk_reward_ratio <= 0:
        print("Risk/reward configuration validation failed.", file=sys.stderr)
        return 1
    if risk_reward_snapshot.direction not in {"WAIT", "BUY_READY", "SELL_READY"}:
        print("Risk/reward direction validation failed.", file=sys.stderr)
        return 1
    if risk_reward_snapshot.direction in {"BUY_READY", "SELL_READY"} and risk_reward_snapshot.plan is None:
        print("Ready risk/reward state must include a plan.", file=sys.stderr)
        return 1
    if risk_reward_snapshot.plan is not None and risk_reward_snapshot.plan.valid:
        if risk_reward_snapshot.plan.risk_reward_ratio < config.risk_reward.minimum_risk_reward_ratio:
            print("Risk/reward minimum-ratio validation failed.", file=sys.stderr)
            return 1
    if risk_reward_snapshot.reason.strip() == "" or risk_reward_snapshot.summary.strip() == "":
        print("Risk/reward summary validation failed.", file=sys.stderr)
        return 1

    chart_runtime_resource = (source_root / "sentinel_ai" / "resources" / "chart" / "sentinel_chart_runtime.js").read_text(
        encoding="utf-8"
    )
    if "resolveSegmentXRange" not in chart_runtime_resource:
        print("Bounded chart segment renderer validation failed.", file=sys.stderr)
        return 1
    if "drawCombinedSupportResistanceRange" not in chart_runtime_resource:
        print("Fallback support/resistance range-box renderer validation failed.", file=sys.stderr)
        return 1
    if any(marker in chart_runtime_resource for marker in ("bufferCanvas", "bufferContext", "screenContext", "flushBuffer")):
        print("Single-canvas repaint path validation failed: buffer-copy artifacts are still present.", file=sys.stderr)
        return 1
    chart_html_resource = (source_root / "sentinel_ai" / "resources" / "chart" / "chart_view.html").read_text(
        encoding="utf-8"
    )
    if "contain: strict" not in chart_html_resource:
        print("Chart containment validation failed.", file=sys.stderr)
        return 1

    app_resource = (source_root / "sentinel_ai" / "app.py").read_text(encoding="utf-8")
    live_handler_start = app_resource.find("def _handle_market_snapshot_refreshed")
    live_handler_end = app_resource.find("def _update_market_structure", live_handler_start)
    live_handler_resource = app_resource[live_handler_start:live_handler_end]
    if "_update_momentum" not in live_handler_resource or "_update_confidence" not in live_handler_resource or "_update_entry_validation" not in live_handler_resource or "_update_risk_reward" not in live_handler_resource:
        print("Live refresh confidence pipeline validation failed.", file=sys.stderr)
        return 1

    entry_engine_resource = (source_root / "sentinel_ai" / "analysis" / "entry_validation_engine.py").read_text(
        encoding="utf-8"
    )
    if "BULLISH_STRUCTURE" not in entry_engine_resource or "BEARISH_STRUCTURE" not in entry_engine_resource:
        print("Entry validation structure-only setup alignment validation failed.", file=sys.stderr)
        return 1
    if "price is not in valid entry zone" not in entry_engine_resource or "momentum is not aligned" not in entry_engine_resource:
        print("Entry validation precise WAIT reason validation failed.", file=sys.stderr)
        return 1

    if "_pullback_momentum_allowed" not in entry_engine_resource:
        print("Entry validation pullback-aware logic validation failed.", file=sys.stderr)
        return 1
    if "Bullish pullback into" not in entry_engine_resource or "Bearish pullback into" not in entry_engine_resource:
        print("Entry validation pullback reason validation failed.", file=sys.stderr)
        return 1
    if "momentum_bias == \"LEAN_BEARISH\"" not in entry_engine_resource or "momentum_bias == \"LEAN_BULLISH\"" not in entry_engine_resource:
        print("Entry validation counter-leaning momentum validation failed.", file=sys.stderr)
        return 1

    if "_neutral_momentum_allowed" not in entry_engine_resource:
        print("Entry validation neutral momentum allowance validation failed.", file=sys.stderr)
        return 1
    if "with neutral momentum" not in entry_engine_resource or 'momentum_snapshot.bias != "NEUTRAL"' not in entry_engine_resource:
        print("Entry validation neutral momentum reason validation failed.", file=sys.stderr)
        return 1

    risk_reward_engine_resource = (source_root / "sentinel_ai" / "analysis" / "risk_reward_engine.py").read_text(
        encoding="utf-8"
    )
    if "_select_target_from_candidates" not in risk_reward_engine_resource:
        print("Smart TP candidate selector validation failed.", file=sys.stderr)
        return 1
    if "TP{index} RR" not in risk_reward_engine_resource or "no valid {self._directional_label(setup_direction)} TP meets RR" not in risk_reward_engine_resource:
        print("Smart TP rejection wording validation failed.", file=sys.stderr)
        return 1
    if "TP{index} selected" not in risk_reward_engine_resource:
        print("Smart TP selected-target wording validation failed.", file=sys.stderr)
        return 1
    if "_external_high_target" not in risk_reward_engine_resource or "_external_low_target" not in risk_reward_engine_resource:
        print("External swing TP candidate validation failed.", file=sys.stderr)
        return 1

    if "_directional_tp_guard" not in risk_reward_engine_resource:
        print("Directional TP guard validation failed.", file=sys.stderr)
        return 1
    if "No valid BUY TP above entry" not in risk_reward_engine_resource or "No valid SELL TP below entry" not in risk_reward_engine_resource:
        print("Directional TP rejection wording validation failed.", file=sys.stderr)
        return 1
    main_window_resource = (source_root / "sentinel_ai" / "gui" / "main_window.py").read_text(encoding="utf-8")
    if "Auto Trade: LOCKED" not in main_window_resource or "auto_trade_locked" not in main_window_resource:
        print("Auto Trade locked UI validation failed.", file=sys.stderr)
        return 1
    if "Rejected" not in main_window_resource or "rejected" not in main_window_resource:
        print("Rejected TP/SL display validation failed.", file=sys.stderr)
        return 1

    if "_range_high_target" not in risk_reward_engine_resource or "_range_low_target" not in risk_reward_engine_resource:
        print("Range high/low TP target validation failed.", file=sys.stderr)
        return 1
    if "_buy_imbalance_targets" not in risk_reward_engine_resource or "_sell_imbalance_targets" not in risk_reward_engine_resource:
        print("Imbalance far-edge TP target validation failed.", file=sys.stderr)
        return 1
    if "_atr_projected_target" not in risk_reward_engine_resource or "ATR projected target" not in risk_reward_engine_resource:
        print("ATR projected TP target validation failed.", file=sys.stderr)
        return 1
    if "current range high" not in risk_reward_engine_resource or "current range low" not in risk_reward_engine_resource:
        print("Range TP target wording validation failed.", file=sys.stderr)
        return 1
    if "FVG far edge" not in risk_reward_engine_resource or "OB far edge" not in risk_reward_engine_resource:
        print("Imbalance TP target wording validation failed.", file=sys.stderr)
        return 1

    chart_runtime_resource = (source_root / "sentinel_ai" / "resources" / "chart" / "sentinel_chart_runtime.js").read_text(
        encoding="utf-8"
    )
    if "setTradePlan" not in chart_runtime_resource or "drawTradePlanOverlay" not in chart_runtime_resource:
        print("Trade plan chart overlay runtime validation failed.", file=sys.stderr)
        return 1
    if "ENTRY" not in chart_runtime_resource or "SL" not in chart_runtime_resource or "TP" not in chart_runtime_resource:
        print("Trade plan overlay label validation failed.", file=sys.stderr)
        return 1
    chart_panel_resource = (source_root / "sentinel_ai" / "gui" / "widgets" / "chart_panel.py").read_text(encoding="utf-8")
    if "set_trade_plan_snapshot" not in chart_panel_resource:
        print("Chart panel trade plan routing validation failed.", file=sys.stderr)
        return 1
    if "set_active_position_snapshot" not in chart_panel_resource or "setActivePosition" not in chart_panel_resource:
        print("Chart panel active-position routing validation failed.", file=sys.stderr)
        return 1
    if "drawActivePositionOverlay" not in runtime_resource or "ACTIVE ENTRY" not in runtime_resource:
        print("Chart runtime active-position overlay validation failed.", file=sys.stderr)
        return 1
    if "drawCandleCountdownBadge" in runtime_resource or "resolveCandleCountdown" in runtime_resource or "startCountdownTimer" in runtime_resource:
        print("Countdown removal validation failed.", file=sys.stderr)
        return 1
    if "Active Trade:" not in runtime_resource or "Plan:" not in runtime_resource:
        print("Active trade header priority validation failed.", file=sys.stderr)
        return 1
    if "protectionStatus" not in runtime_resource or "missingTakeProfit" not in runtime_resource:
        print("Chart runtime protection warning validation failed.", file=sys.stderr)
        return 1
    if "isUsablePrice" not in runtime_resource or ".filter(isUsablePrice)" not in runtime_resource:
        print("Missing active-position TP/SL chart-scale guard validation failed.", file=sys.stderr)
        return 1
    if "drawActivePositionOrTradePlanOverlay" not in runtime_resource:
        print("Chart runtime active-position priority validation failed.", file=sys.stderr)
        return 1
    if "set_manual_trade_review_enabled" not in main_window_resource:
        print("Manual review gate enablement validation failed.", file=sys.stderr)
        return 1
    app_resource = (source_root / "sentinel_ai" / "app.py").read_text(encoding="utf-8")
    if "_handle_manual_trade_review_requested" not in app_resource or "_build_trade_plan_review_snapshot" not in app_resource:
        print("Manual review confirmation modal validation failed.", file=sys.stderr)
        return 1
    if "Place Manual Order" not in app_resource or "Cancel" not in app_resource:
        print("Manual order modal button validation failed.", file=sys.stderr)
        return 1
    if "_place_manual_mt5_order" not in app_resource or "place_manual_market_order" not in app_resource:
        print("Manual MT5 order placement wiring validation failed.", file=sys.stderr)
        return 1
    if "_manual_order_results" not in app_resource or "manual_order_requested_after_confirmation" not in app_resource:
        print("Manual order result tracking validation failed.", file=sys.stderr)
        return 1
    if "manual_trade_requested.connect" not in app_resource:
        print("Manual trade review signal wiring validation failed.", file=sys.stderr)
        return 1
    mt5_service_resource = (source_root / "sentinel_ai" / "mt5" / "mt5_service.py").read_text(encoding="utf-8")
    if "place_manual_market_order" not in mt5_service_resource or "order_send" not in mt5_service_resource:
        print("MT5 manual order_send validation failed.", file=sys.stderr)
        return 1
    if "order_check" not in mt5_service_resource or "one_position_per_symbol" not in mt5_service_resource:
        print("Manual order safety check validation failed.", file=sys.stderr)
        return 1
    if "_candidate_filling_modes" not in mt5_service_resource or "Manual order check rejected after filling fallback" not in mt5_service_resource:
        print("Adaptive filling-mode fallback validation failed.", file=sys.stderr)
        return 1
    if "ORDER_FILLING_FOK" not in mt5_service_resource or "ORDER_FILLING_IOC" not in mt5_service_resource or "ORDER_FILLING_RETURN" not in mt5_service_resource:
        print("Filling-mode candidate coverage validation failed.", file=sys.stderr)
        return 1

    if "monitor_symbol_position" not in mt5_service_resource or "daily_trade_statistics" not in mt5_service_resource:
        print("Position monitoring MT5 service validation failed.", file=sys.stderr)
        return 1
    if "_latest_closed_deal" not in mt5_service_resource or "_closed_trade_result" not in mt5_service_resource:
        print("Closed-trade lifecycle MT5 extraction validation failed.", file=sys.stderr)
        return 1
    if "_filter_closed_deals" not in mt5_service_resource or "SYMBOL_24H_FALLBACK" not in mt5_service_resource:
        print("MT5 history fallback matching validation failed.", file=sys.stderr)
        return 1
    if "owned_position_ticket" not in mt5_service_resource or "SENTINEL_TICKET_MATCH" not in mt5_service_resource:
        print("Sentinel-owned ticket matching validation failed.", file=sys.stderr)
        return 1
    if "owned_position_tickets" not in mt5_service_resource or "_normalize_owned_tickets" not in mt5_service_resource:
        print("Sentinel ledger multi-ticket statistics validation failed.", file=sys.stderr)
        return 1
    if "_is_strict_close_entry_deal" not in mt5_service_resource or "or close_entry) != close_entry" in mt5_service_resource:
        print("Strict MT5 closed-deal entry filtering validation failed.", file=sys.stderr)
        return 1
    if "_filter_magic_after_open_close_deals" not in mt5_service_resource or "SENTINEL_MAGIC_AFTER_OPEN_RESOLUTION" not in mt5_service_resource:
        print("Robust close-history resolver validation failed.", file=sys.stderr)
        return 1
    if "_is_close_or_profit_resolution_deal" not in mt5_service_resource or "_close_entry_values" not in mt5_service_resource:
        print("Lenient close resolver validation failed.", file=sys.stderr)
        return 1
    if "DEAL_ENTRY_INOUT" not in mt5_service_resource or "DEAL_ENTRY_OUT_BY" not in mt5_service_resource:
        print("Expanded close entry validation failed.", file=sys.stderr)
        return 1
    if "settlement_search_hours" not in mt5_service_resource or "_deal_datetime" not in mt5_service_resource:
        print("Extended close-history search validation failed.", file=sys.stderr)
        return 1
    mt5_ast = ast.parse(mt5_service_resource)
    mt5_class_methods: set[str] = set()
    for node in mt5_ast.body:
        if isinstance(node, ast.ClassDef) and node.name == "MetaTrader5Service":
            mt5_class_methods = {child.name for child in node.body if isinstance(child, ast.FunctionDef)}
            break
    required_mt5_methods = {
        "_filter_magic_after_open_close_deals",
        "_filter_sentinel_recovery_deals",
        "_filter_closed_deals",
        "_normalize_datetime",
        "_deal_datetime",
    }
    if not required_mt5_methods.issubset(mt5_class_methods):
        print("MT5 resolver method binding validation failed.", file=sys.stderr)
        return 1
    if "_filter_sentinel_recovery_deals" not in mt5_service_resource or "SENTINEL_MAGIC_COMMENT_RECOVERY" not in mt5_service_resource:
        print("Sentinel magic/comment recovery validation failed.", file=sys.stderr)
        return 1
    if "SENTINEL_ONLY_NO_TICKET" not in mt5_service_resource or "sentinel_owned_only" not in mt5_service_resource:
        print("Outside MT5 trade suppression validation failed.", file=sys.stderr)
        return 1
    if "_deal_close_type" not in mt5_service_resource or "TP HIT" not in mt5_service_resource or "MANUAL CLOSE" not in mt5_service_resource:
        print("Close type detection validation failed.", file=sys.stderr)
        return 1
    if "raw_take_profit" not in mt5_service_resource or "take_profit = raw_take_profit if raw_take_profit > 0 else None" not in mt5_service_resource:
        print("MT5 missing TP normalization validation failed.", file=sys.stderr)
        return 1
    if "_position_protection_status" not in mt5_service_resource or "WARNING: Missing TP" not in mt5_service_resource:
        print("MT5 protection status warning validation failed.", file=sys.stderr)
        return 1
    if "positions_get" not in mt5_service_resource or "history_deals_get" not in mt5_service_resource:
        print("MT5 position/history API validation failed.", file=sys.stderr)
        return 1
    position_resource = (source_root / "sentinel_ai" / "models" / "position_monitoring.py").read_text(encoding="utf-8")
    if "PositionMonitorSnapshot" not in position_resource or "DailyTradeStatisticsSnapshot" not in position_resource:
        print("Position monitoring model validation failed.", file=sys.stderr)
        return 1
    if "last_closed_result" not in position_resource or "last_closed_profit" not in position_resource:
        print("Closed-trade lifecycle model validation failed.", file=sys.stderr)
        return 1
    if "history_match_mode" not in position_resource or "last_close_type" not in position_resource:
        print("History fallback model validation failed.", file=sys.stderr)
        return 1
    if "sentinel_owned_only" not in position_resource:
        print("Sentinel-only statistics model validation failed.", file=sys.stderr)
        return 1
    if "ledger_open_trades" not in position_resource or "ledger_closed_trades" not in position_resource or "result_status" not in position_resource:
        print("Ledger open/closed result status model validation failed.", file=sys.stderr)
        return 1
    if "ledger_pending_close_trades" not in position_resource:
        print("Pending close model validation failed.", file=sys.stderr)
        return 1
    if "lifecycle_stage" not in position_resource or "tracked_sentinel_ticket" not in position_resource:
        print("Lifecycle diagnostics model validation failed.", file=sys.stderr)
        return 1
    if "pending_close_age_seconds" not in position_resource:
        print("Pending close age model validation failed.", file=sys.stderr)
        return 1
    if "close_resolver_status" not in position_resource or "audit_warning" not in position_resource:
        print("Close resolver/audit model validation failed.", file=sys.stderr)
        return 1
    if "pending_backlog_trades" not in position_resource or "stale_pending_trades" not in position_resource:
        print("Pending backlog/stale model validation failed.", file=sys.stderr)
        return 1
    if "ledger_health" not in position_resource or "completion_status" not in position_resource or "build_stage" not in position_resource:
        print("Final stabilization model validation failed.", file=sys.stderr)
        return 1
    sentinel_trade_resource = (source_root / "sentinel_ai" / "models" / "sentinel_trade.py").read_text(encoding="utf-8")
    if "SentinelOwnedTrade" not in sentinel_trade_resource or "SENTINEL_APP_MANUAL" not in sentinel_trade_resource:
        print("Sentinel-owned trade model validation failed.", file=sys.stderr)
        return 1
    if "to_dict" not in sentinel_trade_resource or "from_dict" not in sentinel_trade_resource:
        print("Sentinel-owned trade persistence model validation failed.", file=sys.stderr)
        return 1
    if "pending_close" not in sentinel_trade_resource or "pending_close_since" not in sentinel_trade_resource:
        print("Pending close trade model validation failed.", file=sys.stderr)
        return 1
    if "close_profit" not in sentinel_trade_resource or "closed_at" not in sentinel_trade_resource:
        print("Sentinel ledger close-result persistence model validation failed.", file=sys.stderr)
        return 1
    main_window_resource = (source_root / "sentinel_ai" / "gui" / "main_window.py").read_text(encoding="utf-8")
    if "update_position_monitor_status" not in main_window_resource or "_has_active_position_lock" not in main_window_resource:
        print("Position monitor GUI validation failed.", file=sys.stderr)
        return 1
    if "ledger_maintenance_requested" not in main_window_resource or "Ledger Tools" not in main_window_resource:
        print("Ledger maintenance toolbar validation failed.", file=sys.stderr)
        return 1
    statistics_panel_resource = (source_root / "sentinel_ai" / "gui" / "widgets" / "statistics_panel.py").read_text(encoding="utf-8")
    if "protection_status" not in main_window_resource or "Protection Status" not in statistics_panel_resource:
        print("Protection status GUI validation failed.", file=sys.stderr)
        return 1
    if "Last Result" not in statistics_panel_resource or "Net P/L" not in statistics_panel_resource:
        print("Closed-trade result dashboard validation failed.", file=sys.stderr)
        return 1
    if "Last Close Type" not in statistics_panel_resource or "History Match" in statistics_panel_resource:
        print("Simplified close type dashboard validation failed.", file=sys.stderr)
        return 1
    if "Closed Trades" not in statistics_panel_resource or "Open Trades" not in statistics_panel_resource:
        print("Ledger open/closed dashboard validation failed.", file=sys.stderr)
        return 1
    if "Total Ledger Records" in statistics_panel_resource or "Result Status" not in statistics_panel_resource:
        print("Trade result verification dashboard validation failed.", file=sys.stderr)
        return 1
    if "Open Trades" not in statistics_panel_resource or "Closed Trades" not in statistics_panel_resource:
        print("Simplified open/closed dashboard validation failed.", file=sys.stderr)
        return 1
    if "Lifecycle Stage" not in statistics_panel_resource or "Result Status" not in statistics_panel_resource:
        print("Simplified lifecycle dashboard validation failed.", file=sys.stderr)
        return 1
    if "Ledger Warning" not in statistics_panel_resource or "Close Resolver" in statistics_panel_resource:
        print("Simplified ledger warning dashboard validation failed.", file=sys.stderr)
        return 1
    if "Pending Backlog Trades" in statistics_panel_resource or "Build Stage" in statistics_panel_resource:
        print("Backend diagnostics should not be on the main dashboard.", file=sys.stderr)
        return 1
    if "self._has_active_position_lock = False" not in main_window_resource:
        print("Startup active-position lock initialization validation failed.", file=sys.stderr)
        return 1
    if "ACTIVE_{position_snapshot.direction}_POSITION" not in main_window_resource:
        print("Active position prediction-priority validation failed.", file=sys.stderr)
        return 1
    if "set_active_position_snapshot" not in main_window_resource:
        print("Active position chart-lock routing validation failed.", file=sys.stderr)
        return 1
    app_resource = (source_root / "sentinel_ai" / "app.py").read_text(encoding="utf-8")
    trade_manager_resource = (source_root / "sentinel_ai" / "services" / "trade_manager_service.py").read_text(encoding="utf-8")
    if "_update_position_monitoring" not in app_resource or "monitor_symbol_position" not in app_resource:
        print("Position monitor app wiring validation failed.", file=sys.stderr)
        return 1
    if "self._trade_manager" not in app_resource or "sync_sentinel_owned_position_ticket" not in app_resource:
        print("Application Trade Manager delegation validation failed.", file=sys.stderr)
        return 1
    legacy_lifecycle_methods = {
        "_track_position_lifecycle",
        "_sentinel_owned_daily_statistics",
        "_statistics_with_ledger_totals",
        "_load_sentinel_trade_ledger",
        "_save_sentinel_trade_ledger",
        "_resolve_single_pending_trade_from_history",
    }
    if any(method in app_resource for method in legacy_lifecycle_methods):
        print("Stage 8 validation failed: lifecycle helpers should live in TradeManagerService, not app.py.", file=sys.stderr)
        return 1
    required_trade_manager_markers = (
        "class TradeManagerService",
        "register_sentinel_owned_trade",
        "track_position_lifecycle",
        "Sentinel app trade closed:",
        "sentinel_owned_daily_statistics",
        "save_sentinel_owned_trade",
        "load_sentinel_owned_trade",
        "sentinel_trade_ledger_path",
        "load_sentinel_trade_ledger",
        "save_sentinel_trade_ledger",
        "upsert_sentinel_trade",
        "sentinel_owned_tickets",
        "Recovered active Sentinel-owned trade",
        "close_sentinel_owned_trade",
        "statistics_with_ledger_totals",
        "ledger_result_status",
        "Sentinel trade open",
        "active_trade_guard_statistics",
        "SENTINEL_ACTIVE_TICKET_GUARD",
        "mark_sentinel_trade_pending_close",
        "SENTINEL_PENDING_CLOSE",
        "ledger_lifecycle_stage",
        "diagnostic_tracked_ticket",
        "pending_close_age_seconds",
        "close_resolver_status",
        "audit_warning",
        "current_resolution_opened_at",
        "owned_trade_opened_at=self.current_resolution_opened_at(active_symbol)",
        "trade_can_accept_resolved_close",
        "self._tracked_active_position_ticket = None",
        "CURRENT_ACTIVE_WITH_STALE_PENDING_BACKLOG",
        "STAGE_8_COMPLETE_AUTO_TRADE_LOCKED",
        "current_pending_trades",
        "stale_pending_trades",
        "is_pending_trade_stale",
        "pending_backlog = len(stale_pending_trades)",
        "ledger_pending = len(current_pending_trades)",
        "repair_pending_history_records",
        "resolve_single_pending_trade_from_history",
        "resolved_close_time_is_valid_for_trade",
        "trade_ticket_tuple",
        "export_sentinel_ledger",
        "reset_test_ledger_guarded",
        "Reset blocked because an active Sentinel trade is open",
        "reopen_sentinel_trade_from_active_position",
        "trade_matches_position_ticket",
        "Ignored false close result for still-active Sentinel ticket",
        "trades_share_ticket",
        "sentinel_comment=self._manual_config.order_comment",
        "STAGE_8_TRADE_MANAGER_SERVICE_COMPLETE",
    )
    if any(marker not in trade_manager_resource for marker in required_trade_manager_markers):
        print("Trade Manager service lifecycle validation failed.", file=sys.stderr)
        return 1
    if "_show_ledger_maintenance_tools" not in app_resource or "_archive_stale_pending_records" not in app_resource:
        print("Ledger maintenance GUI action validation failed.", file=sys.stderr)
        return 1
    if "_repair_pending_history_records" not in app_resource or "self._trade_manager.repair_pending_history_records" not in app_resource:
        print("Pending history repair delegation validation failed.", file=sys.stderr)
        return 1
    if "_handle_auto_trade_toggled" not in app_resource or "_evaluate_auto_trade_after_analysis" not in app_resource:
        print("Guarded auto-trade app validation failed.", file=sys.stderr)
        return 1
    if "auto_trade_locked" not in app_resource:
        print("Auto Trade lock app validation failed.", file=sys.stderr)
        return 1
    auto_trade_diagnostics_resource = (source_root / "sentinel_ai" / "services" / "auto_trade_diagnostics_service.py").read_text(encoding="utf-8")
    if "class AutoTradeDiagnosticsService" not in auto_trade_diagnostics_resource or "AutoTradeDiagnostic" not in auto_trade_diagnostics_resource:
        print("Auto Trade diagnostics service validation failed.", file=sys.stderr)
        return 1
    if "LOCKED" not in auto_trade_diagnostics_resource or "ARMED" not in auto_trade_diagnostics_resource or "ORDER_FAILED" not in auto_trade_diagnostics_resource:
        print("Auto Trade diagnostic state validation failed.", file=sys.stderr)
        return 1
    if "Auto Trade Status" not in statistics_panel_resource or "update_auto_trade_diagnostics" not in statistics_panel_resource:
        print("Auto Trade diagnostics dashboard validation failed.", file=sys.stderr)
        return 1
    prediction_lifecycle_resource = (source_root / "sentinel_ai" / "services" / "prediction_lifecycle_service.py").read_text(encoding="utf-8")
    if "class PredictionLifecycleService" not in prediction_lifecycle_resource or "record_from_risk_reward_snapshot" not in prediction_lifecycle_resource or "_build_signature" not in prediction_lifecycle_resource:
        print("Prediction lifecycle service validation failed.", file=sys.stderr)
        return 1
    app_context_resource = (source_root / "sentinel_ai" / "services" / "app_context.py").read_text(encoding="utf-8")
    if "prediction_lifecycle_service" not in app_context_resource or "PredictionLifecycleService" not in app_context_resource:
        print("Prediction lifecycle service composition validation failed.", file=sys.stderr)
        return 1
    if "trade_manager_service" not in app_context_resource or "TradeManagerService" not in app_context_resource:
        print("Trade Manager service composition validation failed.", file=sys.stderr)
        return 1
    sentinel_trade_resource = (source_root / "sentinel_ai" / "models" / "sentinel_trade.py").read_text(encoding="utf-8")
    if "prediction_uid" not in sentinel_trade_resource:
        print("Sentinel trade prediction linkage validation failed.", file=sys.stderr)
        return 1
    if "_auto_trade_plan_passes_guardrails" not in app_resource or "SENTINEL_APP_AUTO" not in app_resource:
        print("Auto-trade guardrail/ledger validation failed.", file=sys.stderr)
        return 1
    if "No Sentinel app trade closed yet" not in mt5_service_resource or "Sentinel app trade is still open" not in mt5_service_resource:
        print("Sentinel-only statistics status validation failed.", file=sys.stderr)
        return 1

    trade_execution_resource = (source_root / "sentinel_ai" / "models" / "trade_execution.py").read_text(encoding="utf-8")
    if "ManualTradeOrderRequest" not in trade_execution_resource or "ManualTradeOrderResult" not in trade_execution_resource:
        print("Manual trade execution model validation failed.", file=sys.stderr)
        return 1
    if not config.manual_trading.enabled or config.manual_trading.default_volume <= 0:
        print("Manual trading configuration validation failed.", file=sys.stderr)
        return 1
    dummy_position = PositionMonitorSnapshot(
        symbol="TEST",
        has_open_position=False,
        ticket=None,
        direction="NONE",
        volume=0.0,
        open_price=None,
        current_price=None,
        stop_loss=None,
        take_profit=None,
        profit=0.0,
        swap=0.0,
        commission=0.0,
        magic_number=config.manual_trading.magic_number,
        comment="",
        opened_at=None,
        monitored_at=datetime.now(timezone.utc),
        message="validation only",
        missing_stop_loss=True,
        missing_take_profit=True,
        protection_status="WARNING: Missing SL and TP",
    )
    dummy_daily_stats = DailyTradeStatisticsSnapshot(
        symbol="TEST",
        total_closed_trades=1,
        wins=1,
        losses=0,
        breakeven=0,
        win_rate=100.0,
        loss_rate=0.0,
        net_profit=5.0,
        generated_at=datetime.now(timezone.utc),
        message="validation only",
        last_closed_ticket=12345,
        last_closed_profit=5.0,
        last_closed_result="WIN",
        last_closed_at=datetime.now(timezone.utc),
        last_close_reason="validation close",
        last_close_type="TP HIT",
        history_match_mode="SENTINEL_TICKET_MATCH",
        sentinel_owned_only=True,
        ledger_total_trades=1,
        ledger_open_trades=1,
        ledger_pending_close_trades=1,
        ledger_closed_trades=1,
        ledger_total_records=2,
        ledger_wins=1,
        ledger_losses=0,
        ledger_breakeven=0,
        ledger_win_rate=100.0,
        ledger_net_profit=5.0,
        result_status="Closed result verified: WIN 5.00",
        lifecycle_stage="CLOSED_VERIFIED",
        tracked_sentinel_ticket=12345,
        pending_close_age_seconds=0,
        close_resolver_status="Resolved by SENTINEL_TICKET_MATCH",
        audit_warning="-",
        pending_backlog_trades=0,
        stale_pending_trades=0,
        ledger_health="VERIFIED",
        build_stage="STAGE_5_TRADE_RESULT_VERIFICATION_COMPLETE",
        completion_status="MANUAL_MODE_FOUNDATION_COMPLETE_AUTO_TRADE_LOCKED",
    )
    dummy_owned_trade = SentinelOwnedTrade(
        symbol="TEST",
        direction="BUY",
        order_ticket=12345,
        deal_ticket=67890,
        position_ticket=12345,
        entry_price=2000.0,
        stop_loss=1995.0,
        take_profit=2010.0,
        risk_reward_ratio=2.0,
        confidence_percentage=75.0,
        timeframe="M5",
        opened_at=datetime.now(timezone.utc),
        closed=True,
        close_ticket=12345,
        close_profit=5.0,
        close_result="WIN",
        close_type="TP HIT",
        closed_at=datetime.now(timezone.utc),
        history_match_mode="SENTINEL_TICKET_MATCH",
        pending_close=False,
        pending_close_since=None,
    )
    if dummy_owned_trade.source != "SENTINEL_APP_MANUAL":
        print("Sentinel-owned trade model validation failed.", file=sys.stderr)
        return 1
    if dummy_position.has_open_position or dummy_daily_stats.last_closed_result != "WIN":
        print("Position monitoring model validation failed.", file=sys.stderr)
        return 1

    dummy_request = ManualTradeOrderRequest(
        symbol="TEST",
        direction="BUY",
        volume=config.manual_trading.default_volume,
        stop_loss=1.0,
        take_profit=2.0,
        deviation_points=config.manual_trading.deviation_points,
        magic_number=config.manual_trading.magic_number,
        comment=config.manual_trading.order_comment,
        order_filling=config.manual_trading.order_filling,
    )
    dummy_result = ManualTradeOrderResult(
        accepted=False,
        symbol=dummy_request.symbol,
        direction=dummy_request.direction,
        volume=dummy_request.volume,
        requested_price=None,
        filled_price=None,
        stop_loss=dummy_request.stop_loss,
        take_profit=dummy_request.take_profit,
        retcode=None,
        order_ticket=None,
        deal_ticket=None,
        comment=dummy_request.comment,
        message="validation only",
        sent_at=datetime.now(timezone.utc),
    )
    if dummy_result.accepted:
        print("Manual trade execution model validation failed.", file=sys.stderr)
        return 1

    try:
        json.dumps(chart_payload)
    except TypeError as error:
        print(f"Chart payload serialization failed: {error}", file=sys.stderr)
        return 1

    test_suite = unittest.defaultTestLoader.discover(str(project_root / "tests"))
    test_result = unittest.TextTestRunner(verbosity=0).run(test_suite)
    if not test_result.wasSuccessful():
        print("Formal unit tests failed.", file=sys.stderr)
        return 1

    validation_config = project_root / ".validation_config.json"
    if validation_config.exists():
        validation_config.unlink()
    validation_symbol_config = project_root / ".validation_symbol_config.json"
    if validation_symbol_config.exists():
        validation_symbol_config.unlink()

    print(
        "Sprint validation passed: source compiled, resources verified, config loaded, "
        "MT5 mapping available, market feed conversion validated, chart assets ready, "
        "one-second live refresh configured, chart navigation ready, symbol management ready, "
        "market structure engine ready, support/resistance engine ready, liquidity engine ready, imbalance engine ready, momentum engine ready, confidence engine ready, entry validation engine ready, risk/reward engine ready, active overlay range boxing ready, chart right-scroll ready, true consolidation filter ready, rendered-range status ready, single-canvas repaint path ready, trade plan overlay ready, manual review gate ready, polished manual order modal ready, manual MT5 order placement ready, adaptive filling-mode fallback ready, position monitoring ready, daily trade statistics ready, active trade chart lock ready, position-priority display ready, startup lock initialization ready, missing TP chart-scale guard ready, active protection warning ready, closed-trade lifecycle tracking ready, last result dashboard ready, active header priority ready, countdown removed ready, MT5 history fallback ready, close type dashboard ready, Sentinel-owned tracking ready, outside MT5 trade suppression ready, Sentinel journal persistence ready, Sentinel magic/comment recovery ready, persistent Sentinel trade ledger ready, multi-ticket app statistics ready, active Sentinel trade recovery ready, ledger outcome persistence ready, ledger performance dashboard ready, open/closed ledger dashboard ready, trade result verification status ready, active-ticket close guard ready, strict DEAL_ENTRY_OUT filtering ready, false close suppression ready, pending close settlement ready, lifecycle diagnostics ready, pending close age diagnostics ready, lifecycle result-status binding hotfix ready, robust close resolver ready, resolver audit diagnostics ready, MT5 resolver binding hotfix ready, app resolver helper binding hotfix ready, final stabilization dashboard ready, current trade priority ready, stale pending backlog audit ready, pending close/backlog separation ready, ledger maintenance tools ready, stale archive/export/reset ready, lenient TP close resolver ready, simplified dashboard ready, pending history repair ready, manual-mode completion build ready, guarded auto-trade completion ready, auto-trade lock ready, prediction persistence ready, Auto Trade diagnostics ready, Stage 8 Trade Manager service ready, formal tests ready."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
