# Sentinel AI

## Version 2.16.0: Active Trade Health Interpretation Build

This build improves open Sentinel trade readability while preserving the manual-mode stabilization posture.

### Visual Update

The **Active Trade** panel now shows a display-only health interpretation that summarizes the existing progress fields:

```text
BUY POSITION | Position Open | Current: 4114.44
Open P/L 4.72 | TP: 4129.36 | SL: 4093.65
Distance to TP: 14.92 | Distance to SL: 20.79 | Closer: TP
Trade Pressure: TP_PRESSURE | Risk Alert: NEUTRAL_ZONE
TP Progress: 24.03% | SL Risk: 0.00% | Route: PROFIT_PROGRESS
Trade Health: HEALTHY_PROGRESS
```

The **Statistics** panel also exposes:

```text
Trade Health
```

### Trade Health States

```text
HEALTHY_PROGRESS
STRONG_PROGRESS_NEAR_TP
WATCH_DRAWDOWN
HIGH_RISK_NEAR_SL
ENTRY_ZONE_MONITOR
STABLE_MONITOR
UNKNOWN_HEALTH
NO_TRADE
```

### Safety

These fields are display-only. This build does not:

```text
move SL
move TP
close trades
unlock Auto Trade
change strategy rules
change MT5 execution logic
change ledger settlement logic
```

### Auto Trade

Auto Trade remains locked/dormant until manual-mode lifecycle results are verified.

### Validation

Run:

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="src"
python scriptsalidate_sprint.py
```

Expected result includes:

```text
active-trade health interpretation ready
```
