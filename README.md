<!--
MODULE: DOC-001
FILE: DOC-001-001
Module Name: Project README
Version: 0.3.0
Purpose: Documents Sentinel AI setup, sprint scope, validation, and build instructions.
Dependencies: Markdown
Change History:
- 0.1.0: Added Sprint 1 documentation.
- 0.2.0: Added Sprint 2 MT5 connection notes.
- 0.3.0: Added Sprint 3 market data feed notes and NumPy compatibility guidance.
-->

# Sentinel AI

Sentinel AI is a professional Windows desktop trading workstation foundation built with PySide6, SQLite, JSON configuration, MT5 market-data integration, validated market feed services, and service-based architecture.

## Current Sprint

Version: 0.3.0

Sprint 3 adds the Market Data Feed Foundation while preserving the Sprint 1 GUI layout and Sprint 2 MT5 connection architecture.

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

Trade execution, prediction generation, and learning adjustments are intentionally outside Sprint 3 scope.

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
Sprint validation passed: source compiled, resources verified, config loaded, MT5 mapping available, market feed conversion validated.
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
- Sprint 3 is read-only for market data and does not place trades.
- Keep `numpy==1.26.4` unless MT5 package compatibility is verified against a newer version.
