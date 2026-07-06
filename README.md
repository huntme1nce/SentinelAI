# Sentinel AI

## Sprint 6: Symbol Management Foundation

Sentinel AI is a professional Windows desktop application for MT5 market analysis, statistical prediction tracking, and future controlled trading execution.

Sprint 6 adds broker/account-specific symbol management. Sentinel AI is no longer hard-locked to `GOLDm#`. It now reads the active MT5 account symbol catalog, validates the configured symbol, attempts safe alias resolution when the configured symbol is unavailable, lets the user select or type a broker symbol in the toolbar, persists the selected symbol to the writable JSON config, reloads candles after a symbol change, and restarts live refresh safely.

## Current Capability

- PySide6 Windows desktop shell
- Manual welcome window with Proverbs 13:11
- SQLite database initialization
- Prediction repository foundation
- MT5 read-only connection foundation
- MT5 account/session status
- Broker symbol catalog loading
- Active symbol validation and persistence
- Symbol alias fallback for common gold symbols such as `XAUUSD`, `GOLD`, `XAUUSDm`, and `GOLDm#`
- Validated MT5 candle feed
- Embedded TradingView Lightweight Charts rendering
- One-second live market refresh
- Chart drag left/right, mouse-wheel zoom, and double-click reset to latest
- Statistics panel backed by persisted prediction records

## Not Included Yet

Sprint 6 does not include BUY/SELL prediction logic, confidence scoring, learning adjustments, manual trade execution, or auto trading. Manual Trade and Auto Trade remain disabled until the trading service sprint.

## Installation

Use Python 3.12 on Windows.

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Validation

```powershell
python scripts\validate_sprint.py
```

Expected result:

```text
Sprint validation passed: source compiled, resources verified, config loaded, MT5 mapping available, market feed conversion validated, chart assets ready, one-second live refresh configured, chart navigation ready, symbol management ready.
```

## Run

```powershell
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Symbol Management Behavior

At startup, Sentinel AI performs this safe sequence:

1. Connect to MT5.
2. Load the active account symbol catalog.
3. Validate the configured symbol from JSON.
4. Use it if available and visible.
5. If unavailable, search preferred aliases.
6. Auto-resolve to the first usable broker symbol when enabled.
7. Persist the active symbol to the writable config.
8. Load candles and start refresh only after symbol validation succeeds.

The toolbar symbol field is editable. You may select a listed broker symbol or type a broker-specific symbol such as `XAUUSD`, `XAUUSDm`, `EURUSD`, or another symbol available in the active MT5 account.

## Configuration

Packaged defaults are stored in:

```text
src/sentinel_ai/resources/config/default_config.json
```

Writable user config is created at runtime and is not reset during sprint upgrades.

New Sprint 6 config section:

```json
"symbol_management": {
  "auto_resolve_enabled": true,
  "preferred_aliases": [
    "GOLDm#",
    "XAUUSD",
    "GOLD",
    "XAUUSDm",
    "XAUUSD#",
    "GOLDm",
    "GOLDmicro"
  ],
  "toolbar_max_symbols": 5000
}
```

## Build

```powershell
.\build_windows.ps1
```

The project remains PyInstaller-compatible and Windows standalone compatible.

## Git

Sprint 6 stable commit:

```text
Sprint 6 symbol management foundation
```
