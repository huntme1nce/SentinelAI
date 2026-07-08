# Sentinel AI

## Version 2.7.0: Stage 8 Trade Manager Service Completion Build

This build completes the controlled build path through **Stage 8**. The key architectural improvement is that Sentinel-owned trade lifecycle handling is now owned by a dedicated `TradeManagerService`, not the GUI bootstrapper.

Auto Trade remains locked/dormant by default. This sprint does **not** unlock Auto Trade and does **not** change strategy rules.

## Completed stages through Stage 8

```text
Stage 1: Foundation and Architecture                  Completed foundation
Stage 2: Market Data and Chart Display                Completed foundation
Stage 3: Analysis Engines                             Completed foundation
Stage 4: Prediction Lifecycle                         Started and wired to trade lifecycle
Stage 5: Manual Trade Lifecycle                       Service-managed and validation-ready
Stage 6: Statistics / Ledger Verification             Service-managed and validation-ready
Stage 7: Auto Trade Diagnostics                       Implemented, locked/dormant
Stage 8: Trade Manager Refactor                       Completed in this build
```

## What changed in 2.7.0

```text
TradeManagerService added
Trade lifecycle logic moved out of app.py
Sentinel-owned trade registration delegated to TradeManagerService
Position lifecycle tracking delegated to TradeManagerService
Ledger statistics and dashboard totals delegated to TradeManagerService
Pending-close settlement delegated to TradeManagerService
Repair Pending History delegated to TradeManagerService
Archive stale pending delegated to TradeManagerService
Export ledger delegated to TradeManagerService
Guarded reset delegated to TradeManagerService
Trade Manager service unit tests added
Sprint validator updated for Stage 8
```

## Stage 8 architecture result

`app.py` now coordinates UI, refresh events, manual confirmations, and Auto Trade diagnostics only. The service layer owns the Sentinel trade lifecycle:

```text
TradeManagerService
├─ register_sentinel_owned_trade
├─ sync_sentinel_owned_position_ticket
├─ sentinel_owned_daily_statistics
├─ track_position_lifecycle
├─ statistics_with_ledger_totals
├─ repair_pending_history_records
├─ archive_stale_pending_records
├─ export_sentinel_ledger
└─ reset_test_ledger_guarded
```

## Current safety default

```json
"auto_trade_enabled": false,
"auto_trade_locked": true,
"one_trade_at_a_time": true,
"minimum_confidence": 75.0,
"default_risk_reward": 2.0
```

## Current build stage

Sentinel AI is now through:

```text
Stage 8: Trade Manager Refactor
```

The next major stage should be **Stage 9: Learning Engine readiness**, but only after live demo/manual-mode results are verified.

## Manual-mode flow to verify

```text
Prediction generated
Prediction recorded
Manual trade placed
Trade active
Trade monitored by TradeManagerService
Trade closed
Result resolved as WIN / LOSS / BREAKEVEN
Ledger updated by TradeManagerService
Dashboard updated
Linked prediction closed
```

## Ledger Tools

```text
Repair Pending History
Archive Stale Pending
Export Ledger
Reset Test Ledger
```

Reset remains blocked while an active Sentinel trade is open.

## Run

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="src"
python scripts\validate_sprint.py
python -m sentinel_ai.main
```

## Validation

Expected validator result includes:

```text
Stage 8 Trade Manager service ready
```

## Testing Reminder

Use demo first. Auto Trade stays locked by default in this build.
