"""
MODULE: OPS-001
FILE: OPS-001-001
Module Name: Sprint Validator
Version: 0.7.0
Purpose: Validates Sprint source syntax, resources, configuration loading, MT5 mapping, market feed conversion, chart assets, one-second refresh, symbol management, and market structure analysis.
Dependencies: compileall, datetime, json, logging, pathlib, sys, pandas
Change History:
- 0.1.0: Added compile and resource validation for stable milestone handoff.
- 0.2.0: Added Sprint 2 configuration and MT5 timeframe mapper validation.
- 0.3.0: Added Sprint 3 market data feed validation using a deterministic gateway.
- 0.4.0: Added Sprint 4 embedded chart resource and payload serialization validation.
- 0.5.0: Added Sprint 5 live refresh service file and configuration validation.
- 0.5.1: Added validation for one-second refresh defaults and chart navigation runtime controls.
- 0.6.0: Added validation for symbol catalog models, contract methods, resolution service, and config persistence.
- 0.7.0: Added validation for market structure models, engine output, and chart marker runtime.
"""

from __future__ import annotations

import compileall
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def main() -> int:
    """Compile project source and verify required Sprint 7 market structure foundation components."""
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
        source_root / "sentinel_ai" / "analysis" / "market_structure_engine.py",
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
    required_runtime_markers = ["mousedown", "wheel", "dblclick", "offsetFromRight", "resetViewToLatest", "setMarketStructure", "drawStructureMarkers"]
    if any(marker not in runtime_resource for marker in required_runtime_markers):
        print("Chart navigation runtime validation failed.", file=sys.stderr)
        return 1

    compiled = compileall.compile_dir(str(source_root), quiet=1)
    if not compiled:
        print("Python source compilation failed.", file=sys.stderr)
        return 1

    sys.path.insert(0, str(source_root))
    from sentinel_ai.analysis.market_structure_engine import MarketStructureEngine
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

        def fetch_ohlc(self, symbol: str, timeframe: str, bar_count: int | None = None) -> pd.DataFrame:
            """Return deterministic OHLCV candles using the canonical schema."""
            requested_count = int(bar_count or 3)
            base_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
            records = []
            for index in range(requested_count):
                open_price = 2000.0 + index
                records.append(
                    {
                        "time": base_time + pd.Timedelta(minutes=5 * index),
                        "open": open_price,
                        "high": open_price + 2.0,
                        "low": open_price - 1.0,
                        "close": open_price + 1.0,
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

    if not config.market_structure.enabled or config.market_structure.swing_window != 2:
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

    try:
        json.dumps(chart_payload)
    except TypeError as error:
        print(f"Chart payload serialization failed: {error}", file=sys.stderr)
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
        "market structure engine ready."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
