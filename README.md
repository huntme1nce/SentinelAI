# Sentinel AI

## Version 2.8.0: Stage 9 Learning Readiness Build

This build completes the next controlled stage after the Stage 8 Trade Manager extraction.

Stage 9 does **not** change strategy parameters automatically. It prepares reliable evidence for future statistical learning by reviewing closed prediction records and Sentinel ledger context.

## Stage Status

```text
Stage 1: Foundation                     Complete / stable foundation
Stage 2: Market Data + Chart             Complete / functional
Stage 3: Analysis Engines                Complete foundation
Stage 4: Prediction Lifecycle            Foundation completed
Stage 5: Manual Trade Lifecycle          Strengthened
Stage 6: Statistics / Ledger             Strengthened
Stage 7: Auto Trade Diagnostics          Complete, still locked
Stage 8: Trade Manager Refactor          Complete
Stage 9: Learning Readiness              Complete foundation
```

## What Stage 9 Adds

```text
LearningReadinessService
LearningRepository
LearningReadinessSnapshot model
LearningFailurePattern model
LearningDatasetRow model
learning_reviews SQLite table
closed prediction dataset query
learning-readiness dashboard rows
formal learning-readiness unit tests
```

## Learning Philosophy

Sentinel AI still follows the official rule:

```text
Learning is statistical.
Learning is not emotional.
No parameter should change because of one losing trade.
```

This build only prepares and summarizes evidence. It does **not** rewrite strategy rules, confidence rules, entry rules, TP/SL logic, or Auto Trade behavior.

## New Dashboard Rows

The Statistics panel can now show:

```text
Learning Status
Learning Sample
Learning Pattern
Learning Action
```

Expected examples:

```text
Learning Status: COLLECTING_DATA
Learning Sample: 4/30
Learning Pattern: None yet
Learning Action: NO_PARAMETER_CHANGE
```

or, after enough recurring closed losses are recorded:

```text
Learning Status: PATTERN_REVIEW_READY
Learning Sample: 30/30
Learning Pattern: BUY XAUUSDm M5, confidence 80-89, RR 2.0-2.99: 5/8 losses (62.50%).
Learning Action: NO_PARAMETER_CHANGE
```

## Learning Config Safety Defaults

```json
"learning": {
  "statistical_review_enabled": true,
  "review_window_days": 30,
  "minimum_closed_trades_for_review": 30,
  "minimum_pattern_losses": 3,
  "max_failure_patterns": 3,
  "automatic_parameter_adjustment_enabled": false
}
```

`automatic_parameter_adjustment_enabled` is intentionally locked to `false` for Stage 9.

## Auto Trade Status

Auto Trade remains locked/dormant.

```text
Auto Trade: LOCKED
```

This build does not unlock Auto Trade.

## Guarded Auto Trade Diagnostics

The dashboard still supports:

```text
LOCKED
DISABLED
WAITING
BLOCKED
ARMED
ORDER_SENT
ORDER_FAILED
```

The purpose is still diagnosis only until manual-mode lifecycle results are verified.

## Trade Manager

Trade lifecycle orchestration remains delegated to:

```text
TradeManagerService
```

The GUI controller should not own ledger settlement, pending-history repair, or prediction-result closure logic.

## Validation

Run:

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="src"
python scripts\validate_sprint.py
```

Expected validator result includes:

```text
Stage 9 learning readiness ready
formal tests ready
```

## Run

```powershell
cd D:\projects\sentinelai
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="src"
python -m sentinel_ai.main
```

## Testing Reminder

Use demo first. Manual-mode lifecycle validation is still required before any future Auto Trade unlock sprint.
