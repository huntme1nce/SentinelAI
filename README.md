# Sentinel AI

## Sprint 7: Market Structure Engine Foundation

Sentinel AI is a professional Windows desktop application for MT5 market analysis, statistical prediction tracking, and future controlled trading execution.

Sprint 7 adds the first read-only analysis engine: **Market Structure Engine**. It detects confirmed swing highs, confirmed swing lows, structural bias, and close-based break-of-structure context from validated MT5 candles. This sprint does not generate BUY/SELL predictions and does not place trades.

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
- Embedded TradingView Lightweight Charts-style canvas rendering
- One-second live market refresh
- Chart drag left/right, mouse-wheel zoom, and double-click reset to latest
- Read-only Market Structure Engine
- Swing High / Swing Low markers on the chart
- Basic close-based BOS marker on the chart when structure breaks
- Toolbar trend label updated from structure bias
- Current Prediction panel remains WAIT while showing structure context only
- Statistics panel backed by persisted prediction records

## Not Included Yet

Sprint 7 does not include BUY/SELL prediction logic, confidence scoring, liquidity engine, support/resistance engine, learning adjustments, manual trade execution, or auto trading. Manual Trade and Auto Trade remain disabled until the trading service sprint.

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
Sprint validation passed: source compiled, resources verified, config loaded, MT5 mapping available, market feed conversion validated, chart assets ready, one-second live refresh configured, chart navigation ready, symbol management ready, market structure engine ready.
```

## Run

```powershell
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Market Structure Behavior

At startup and on every validated market refresh, Sentinel AI performs this safe sequence:

1. MT5 returns broker-specific candles.
2. Market Data Feed validates and normalizes the candles.
3. Market Structure Engine analyzes only the validated snapshot.
4. The GUI receives only the completed structure snapshot.
5. The chart displays swing markers and BOS context.
6. The Current Prediction panel remains WAIT because no prediction engine is active yet.

## Configuration

Packaged defaults are stored in:

```text
src/sentinel_ai/resources/config/default_config.json
```

Market structure defaults are under:

```json
"analysis": {
  "market_structure": {
    "enabled": true,
    "lookback_candles": 200,
    "swing_window": 2,
    "minimum_swing_distance_price": 0.0,
    "max_chart_markers": 80
  }
}
```

Do not edit packaged defaults for local settings after installation. The writable runtime config is automatically created in the Sentinel AI config directory.

## Build

```powershell
.\build_windows.ps1
```

The build remains PyInstaller-compatible and Windows standalone-ready.
