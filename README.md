# Sentinel AI

## Version 2.5.0: Stabilization and Architecture Alignment Build

This sprint stabilizes the v2.4.0 functional completion baseline before adding more trading features.

Primary focus:

```text
Auto Trade locked/dormant for manual-mode verification
Prediction lifecycle persistence foundation
Deduplicated prediction recording during one-second refresh
Linked prediction UID on Sentinel-owned ledger trades
Formal unit tests for Auto Trade lock and prediction persistence
Validator updated for Sprint 2.5.0
```

## Safety Position

Auto Trade remains unavailable in the UI until manual-mode lifecycle results have enough verified wins/losses.

Toolbar:

```text
Auto Trade: LOCKED
```

Runtime guard:

```text
auto_trade_locked: true
```

Even if a signal is emitted programmatically, the application forces Auto Trade back to OFF while the lock is active.

## Preserved v2.4.0 Capability

The following v2.4.0 functionality remains preserved:

```text
Live MT5 connection
Live chart
Symbol selection and persistence
Market structure, support/resistance, liquidity, imbalance, momentum analysis
Confidence scoring
Entry validation
Risk/reward plan generation
Manual trade review
Manual MT5 order placement
Adaptive filling-mode fallback
Sentinel-owned trade ledger
Open trade tracking
Pending close settlement
TP/SL close result resolver
Closed-trade statistics
Ledger tools
Repair Pending History
Ledger export
Guarded reset
Simplified dashboard
Guarded auto-trade code retained but locked/dormant
```

## Prediction Persistence

Sprint 2.5.0 adds a dedicated `PredictionLifecycleService`.

It records material prediction changes from the risk/reward stage into SQLite and suppresses duplicate rows when the one-second refresh produces the same recommendation repeatedly.

When a Sentinel-owned trade is opened, the linked prediction is marked `TRADE_ACTIVE`.

When the ledger verifies a close result, the linked prediction is closed as:

```text
WIN
LOSS
BREAKEVEN
```

## Main Dashboard

Visible rows remain user-focused:

```text
Today's Trades
Win Rate
Loss Rate
Net P/L
Open Trades
Closed Trades
Ledger Win Rate
Ledger Net P/L
Lifecycle Stage
Result Status
Last Result
Last Close Type
Active Position
Open P/L
Position Ticket
Protection Status
Ledger Warning
```

Backend diagnostics stay in the app/ledger tools instead of the main dashboard.

## Ledger Tools

```text
Repair Pending History
Archive Stale Pending
Export Ledger
Reset Test Ledger
```

Reset is blocked while an active Sentinel trade is open.

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
auto-trade lock ready
prediction persistence ready
formal tests ready
```

## Testing Reminder

Use demo first. Manual mode remains the verification path before Auto Trade is unlocked in a future sprint.
