# Sentinel AI

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
