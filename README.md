# Sentinel AI

## Sprint 9: Liquidity Engine Foundation + BOS Visibility Patch

Sentinel AI is a professional Windows desktop application for MT5 market analysis, statistical prediction tracking, and future controlled trading execution.

Sprint 9 combines the requested **Sprint 8.1 BOS visibility patch** with the **Liquidity Engine Foundation**. It keeps recent BOS markers visible historically, makes BOS labels stronger on the chart, and adds read-only liquidity analysis for buy-side/sell-side liquidity pools, liquidity sweeps, and possible inducement candidates. This sprint does not generate BUY/SELL predictions and does not place trades.

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
- Persistent historical BOS markers on the chart
- Last bullish BOS and bearish BOS context in the Current Prediction panel
- Read-only Support and Resistance Engine
- Ranked support/resistance zones on the chart
- Nearest support/resistance context in the Current Prediction panel
- Read-only Liquidity Engine
- Buy-side liquidity and sell-side liquidity pool overlays
- Bullish and bearish liquidity sweep markers
- Possible inducement candidate context
- Toolbar trend label updated from structure bias
- Current Prediction panel remains WAIT while showing analysis context only
- Statistics panel backed by persisted prediction records

## What Sprint 9 Does Not Do

- No BUY/SELL prediction generation
- No confidence scoring
- No learning adjustments
- No manual trade placement
- No auto trade execution
- No GUI layout redesign

## Setup

Use Python 3.12 on Windows.

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\validate_sprint.py
```

Run the application:

```powershell
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Important Dependency Note

`numpy==1.26.4` is intentionally pinned because the current MetaTrader5 Python package used by Sentinel AI requires NumPy 1.x binary compatibility.

## Chart Controls

- Drag left/right: review previous candles
- Mouse wheel: zoom in/out
- Double-click: reset chart to latest view

## Chart Overlay Priority

1. Candles
2. Support/resistance zones
3. Swing markers
4. BOS markers
5. Liquidity pool and sweep markers

## Engineering Notes

- GUI does not call MT5 directly.
- GUI does not calculate structure, support/resistance, or liquidity.
- MT5 access remains isolated in the MT5 service and market data services.
- Market structure analysis is isolated in `MarketStructureEngine`.
- Support/resistance analysis is isolated in `SupportResistanceEngine`.
- Liquidity analysis is isolated in `LiquidityEngine`.
- Liquidity is treated as confirmation context only, not a standalone strategy.
- Trading controls remain disabled because trade execution is not implemented yet.
