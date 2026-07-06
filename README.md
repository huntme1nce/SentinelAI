<!--
MODULE: DOC-001
FILE: DOC-001-001
Module Name: Project README
Version: 0.5.0
Purpose: Documents Sentinel AI setup, sprint scope, validation, chart rendering, live refresh, and build instructions.
Dependencies: Markdown
Change History:
- 0.1.0: Added Sprint 1 documentation.
- 0.2.0: Added Sprint 2 MT5 connection notes.
- 0.3.0: Added Sprint 3 market data feed notes and NumPy compatibility guidance.
- 0.4.0: Added Sprint 4 live chart rendering notes.
- 0.5.0: Added Sprint 5 live market refresh engine notes.
-->

# Sentinel AI

Sentinel AI is a professional Windows desktop trading workstation foundation built with PySide6, SQLite, JSON configuration, MT5 market-data integration, validated market feed services, embedded chart rendering, live chart refresh, and service-based architecture.

## Current Sprint

Version: 0.5.0

Sprint 5 adds the Live Market Refresh Engine while preserving the Sprint 1 GUI layout, Sprint 2 MT5 connection architecture, Sprint 3 market data feed layer, and Sprint 4 chart renderer.

## Completed Sprint Scope

### Sprint 1: Foundation

- Application entry point
- Welcome window with Proverbs 13:11
- Main application shell using the approved layout
- JSON configuration service
- Logging service
- SQLite database service
- Permanent prediction repository
- Service contracts
- PyInstaller-compatible path handling
- Windows build command

### Sprint 2: MT5 Connection Foundation

- Isolated MT5 market-data service
- MT5 terminal initialization
- Connection status reporting
- Read-only account snapshot model
- Symbol validation and Market Watch selection
- Timeframe mapping
- Safe OHLCV data fetcher
- Configuration migration for existing user configs

### Sprint 3: Market Data Feed Foundation

- Validated market data feed service
- Canonical OHLCV candle validation
- Immutable market data snapshot model
- TradingView Lightweight Charts-compatible candle payload preparation
- Startup candle loading after successful MT5 connection
- Timeframe-change candle reload using the selected timeframe
- Improved MT5 import diagnostics
- NumPy pinned to `1.26.4` for MetaTrader5 binary compatibility

### Sprint 4: Live Chart Rendering

- Embedded chart web view inside the existing chart panel
- Local packaged chart resources under `src/sentinel_ai/resources/chart`
- Live candlestick rendering from validated Sprint 3 OHLCV snapshots
- Timeframe-change chart refresh using the selected timeframe
- Crosshair and latest-price display inside the chart runtime
- PyInstaller hidden imports for Qt WebEngine chart rendering
- No prediction logic
- No trade execution logic
- No GUI layout redesign

### Sprint 5: Live Market Refresh Engine

- Service-driven refresh timer for validated MT5 candle snapshots
- Automatic chart updates after startup
- Timeframe-specific refresh intervals in JSON configuration
- Safe refresh restart when the selected timeframe changes
- Non-destructive status bar updates for live refresh events
- Refresh failure handling without closing the app or replacing the chart layout
- No prediction logic
- No trade execution logic
- No GUI layout redesign

Trade execution, prediction generation, and learning adjustments are intentionally outside Sprint 5 scope.

## Run Locally

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Validate Sprint

```powershell
$env:PYTHONPATH="src"
python scripts/validate_sprint.py
```

Expected result:

```text
Sprint validation passed: source compiled, resources verified, config loaded, MT5 mapping available, market feed conversion validated, chart assets ready, live refresh configured.
```

## Build EXE

```powershell
.\build_windows.ps1
```

The build output is created under `dist\SentinelAI`.

## MT5 Notes

- Install and log in to your broker's MT5 terminal before starting Sentinel AI.
- The configured default symbol is `GOLDm#`.
- If your broker uses a different symbol name, update the writable config file under `%LOCALAPPDATA%\SentinelAI\config\config.json`.
- Sprint 5 is read-only for market data and does not place trades.
- Keep `numpy==1.26.4` unless MT5 package compatibility is verified against a newer version.

## Live Refresh Notes

Default refresh intervals are configured under `market_data.refresh_intervals_seconds`:

- `M1`: 1 second
- `M5`: 2 seconds
- `M15`: 5 seconds
- `M30`: 10 seconds
- `H1`: 15 seconds
- `H4`: 30 seconds
- `D1`: 60 seconds

The GUI does not call MT5 directly. The live chart receives validated snapshots from `MarketRefreshService` through application-level signal handling.

## Chart Notes

- The chart panel renders only validated market-feed candles.
- The GUI does not calculate entries, confidence, trend, support, resistance, or trade signals.
- Chart rendering is isolated from MT5, trading, database, prediction, and learning services.
