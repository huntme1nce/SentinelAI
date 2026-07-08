# Sentinel AI

## Version 2.20.0: Grouped Statistics Sidebar Build

This build keeps the chart-first workspace from v2.18.0 and v2.19.0, but improves readability in the left Statistics sidebar. The sidebar now groups long dashboard rows into sections instead of showing one dense uninterrupted list.

Visual layout remains:

```text
Left Sidebar: Grouped scrollable Statistics
Center Top: Larger Live Chart
Center Bottom: Compact Current Prediction / Active Trade / Trade Result
```

Statistics sections are now grouped as:

```text
Performance
Trade Lifecycle
Trade Monitoring
Profit Lock Preview
Automation
Learning
```

Why this matters:

```text
Chart size remains protected
Statistics are easier to scan
Active Trade stays below the chart
Long Auto Trade, Learning, and Profit Lock rows no longer feel like one cramped list
```

Safety behavior unchanged:

```text
Strategy logic unchanged
MT5 order logic unchanged
Ledger settlement unchanged
Auto Trade remains locked
Profit Lock remains preview-only
No SL modification is executed yet
```

Validation expectation:

```text
grouped statistics sidebar ready
```

## Version 2.19.0: Compact Chart Workspace Layout Build

This build keeps the v2.18.0 chart-first layout but gives the chart even more priority. The Statistics sidebar is narrower and the below-chart Active Trade / Current Prediction / Trade Result panel is capped to a compact fixed height.

Visual layout remains:

```text
Left Sidebar: Compact scrollable Statistics
Center Top: Larger Live Chart
Center Bottom: Compact Current Prediction / Active Trade / Trade Result
```

What changed visually:

```text
Statistics sidebar: narrower width pressure
Active Trade panel: fixed compact height
Chart area: larger vertical priority
Summary card: compact spacing and capped height
```

Safety behavior unchanged:

```text
Strategy logic unchanged
MT5 order logic unchanged
Ledger settlement unchanged
Auto Trade remains locked
Profit Lock remains preview-only
No SL modification is executed yet
```

Validation expectation:

```text
compact chart workspace layout ready
```

## Version 2.18.0: Chart-First Dashboard Layout Build

This build protects the live chart from shrinking as the Statistics panel grows.

Visual layout update:

```text
Left Sidebar: Statistics
Center Top: Live Chart
Center Bottom: Current Prediction / Active Trade / Trade Result
```

The Statistics panel is now inside a scrollable left sidebar. Long dashboard lists such as learning status, Auto Trade diagnostics, active-trade health, and Profit Lock preview rows no longer compete with the chart for vertical space.

The Active Trade panel now sits below the chart. It keeps the same display-only fields introduced in earlier builds:

```text
Current price
Open P/L
Distance to TP
Distance to SL
Closer target
Trade Pressure
Risk Alert
TP Progress
SL Risk
Route State
Trade Health
Profit Lock preview
```

Safety behavior unchanged:

```text
Strategy logic unchanged
MT5 order logic unchanged
Ledger settlement unchanged
Auto Trade remains locked
Profit Lock remains preview-only
No SL modification is executed yet
```

Validation expectation:

```text
chart-first dashboard layout ready
```

## Version 2.17.0: Profit Lock Preview Visibility Build

This build adds a **display-only Profit Lock preview** for future SL-based profit protection. It does not move stop loss, close trades, place hedge trades, modify TP/SL, or unlock Auto Trade.

## What changed visually

The Active Trade panel now shows future profit-lock readiness while a Sentinel-owned trade is open:

```text
Profit Lock: WATCHING_50_TRIGGER / STAGE_1_LOCK_READY / STAGE_2_LOCK_READY / ALREADY_PROTECTED_OR_INVALID
Next: 50% trigger / 50% reached / 75% reached
Suggested SL: previewed SL level
Lock: 25% lock preview / 50% lock preview
```

The Statistics panel now includes:

```text
Profit Lock
Next Lock Trigger
Suggested Lock SL
Suggested Lock
```

## Current safety status

```text
Strategy logic changed: No
MT5 order logic changed: No
Ledger settlement logic changed: No
Auto Trade unlocked: No
Profit Lock execution: Disabled
SL modification: Disabled
```

## Future Profit Lock Manager intent

When later enabled after demo validation, the intended SL protection model is:

```text
At 50% TP Progress: move SL beyond entry to lock around 25% progress.
At 75% TP Progress: move SL farther to lock around 50% progress.
```

It is intended to support both Manual Sentinel trades and future Auto Sentinel trades, with guardrails:

```text
Only move SL in trade direction
Never widen risk
Broker stop-level checks
Spread safety checks
Sentinel-owned trades only
Separate execution toggle
```

## Run

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
python scripts\validate_sprint.py
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Validation

Expected validator result includes:

```text
Profit Lock preview visibility ready
```

Use demo first. Auto Trade and Profit Lock execution remain locked/disabled in this build.
