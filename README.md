# Sentinel AI

Sentinel AI is a professional Windows desktop trading workstation foundation built with PySide6, SQLite, JSON configuration, MT5 market-data integration, and service-based architecture.

## Current Sprint

Version: 0.2.0

Sprint 2 adds the MT5 Connection Foundation while preserving the Sprint 1 GUI layout and service architecture.

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
- Configuration migration for existing Sprint 1 user configs

Trade execution, prediction generation, and learning adjustments are intentionally outside Sprint 2 scope.

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

## Build EXE

```powershell
.uild_windows.ps1
```

The build output is created under `dist\SentinelAI`.

## MT5 Notes

- Install and log in to your broker's MT5 terminal before starting Sentinel AI.
- The configured default symbol is `GOLDm#`.
- If your broker uses a different symbol name, update the writable config file under `%LOCALAPPDATA%\SentinelAI\config\config.json`.
- Sprint 2 is read-only for market data and does not place trades.
