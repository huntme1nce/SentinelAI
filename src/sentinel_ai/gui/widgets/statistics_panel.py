"""
MODULE: GUI-003
FILE: GUI-003-003
Module Name: Statistics Panel
2.6.0
Purpose: Displays persistent prediction statistics and Auto Trade diagnostics in the bottom-right dashboard area.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 2.6.0: Added Auto Trade status and reason rows to expose execution blockers.
- 2.4.0: Preserved simplified dashboard for guarded auto-trade completion build.
- 2.3.0: Preserved simplified dashboard while ledger repair stays in tools/backend.
- 2.2.0: Simplified the main dashboard by hiding backend-only pending/resolver diagnostics.
- 2.1.0: Preserved backlog/stale dashboard rows for ledger maintenance tool build.
- 2.0.1: Preserved backlog/stale rows while pending-close count is limited to current settlement trades.
- 2.0.0: Added ledger health, stale backlog, and build-stage dashboard rows.
- 1.9.0.2: Preserved resolver dashboard rows for app helper binding hotfix.
- 1.9.0.1: Preserved resolver dashboard rows for MT5 resolver binding hotfix.
- 1.9.0: Added close resolver status and audit warning rows.
- 1.8.4.1: Preserved lifecycle dashboard rows for startup binding hotfix.
- 1.8.4: Added lifecycle stage, tracked ticket, and pending age diagnostic rows.
- 1.8.3: Added pending close trades row for MT5 close-history settlement visibility.
- 1.8.2: Preserved open/closed dashboard rows for active-ticket close guard.
- 1.8.1: Clarified ledger rows with open, closed, total records, and result status.
- 1.8.0: Added ledger performance rows for persistent Sentinel trade accuracy.
- 1.7.5: Preserved close type/history match dashboard for multi-trade Sentinel ledger statistics.
- 1.7.4: Preserved close type/history match dashboard for persistent Sentinel-owned trade recovery.
- 1.7.3: Preserved close type/history match dashboard for Sentinel-owned statistics.
- 1.7.2: Added last close type and history match mode rows for MT5 history fallback tracking.
- 1.7.1.3: Preserved lifecycle dashboard rows for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved lifecycle dashboard rows for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved lifecycle dashboard rows for candle countdown timer hotfix.
- 1.7.1: Preserved lifecycle dashboard rows for countdown timer sprint.
- 1.7.0: Added net P/L and last result rows for closed-trade lifecycle tracking.
- 1.6.2: Added active-position protection status row for missing SL/TP warnings.
- 1.6.1.2: Preserved active position rows for missing TP chart-scale hotfix.
- 1.6.1: Preserved active position rows for active-trade chart lock patch.
- 1.6.0: Added active position monitoring rows for Sprint 16.
- 0.1.0: Added statistics dashboard panel fed by repository output.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class StatisticsPanel(QFrame):
    """Display stored prediction statistics without performing database queries."""

    def __init__(self) -> None:
        """Initialize the statistics panel."""
        super().__init__()
        self.setObjectName("Panel")
        self._fields: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the statistics panel layout."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        title = QLabel("Statistics")
        title.setStyleSheet("font-weight: 700; font-size: 12pt;")
        outer_layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        labels = [
            "Today's Trades",
            "Win Rate",
            "Loss Rate",
            "Net P/L",
            "Open Trades",
            "Closed Trades",
            "Ledger Win Rate",
            "Ledger Net P/L",
            "Lifecycle Stage",
            "Result Status",
            "Last Result",
            "Last Close Type",
            "Active Position",
            "Open P/L",
            "Position Ticket",
            "Protection Status",
            "Ledger Warning",
            "Auto Trade Status",
            "Auto Trade Reason",
        ]
        for row, label_text in enumerate(labels):
            label = QLabel(f"{label_text}:")
            label.setObjectName("MutedLabel")
            value = QLabel("-")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._fields[label_text] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
        outer_layout.addLayout(grid)

    def update_statistics(self, statistics: dict[str, Any], learning_status: str) -> None:
        """Update visible statistics from persistent aggregate values."""
        self._fields["Today's Trades"].setText(str(statistics.get("todays_trades", 0)))
        self._fields["Win Rate"].setText(f"{statistics.get('win_rate', 0):.2f}%")
        self._fields["Loss Rate"].setText(f"{statistics.get('loss_rate', 0):.2f}%")
        self._fields["Net P/L"].setText(f"{statistics.get('net_profit', 0):.2f}")
        self._fields["Open Trades"].setText(str(statistics.get("ledger_open_trades", 0)))
        self._fields["Closed Trades"].setText(str(statistics.get("ledger_closed_trades", statistics.get("ledger_total_trades", 0))))
        self._fields["Ledger Win Rate"].setText(f"{statistics.get('ledger_win_rate', 0):.2f}%")
        self._fields["Ledger Net P/L"].setText(f"{statistics.get('ledger_net_profit', 0):.2f}")
        self._fields["Lifecycle Stage"].setText(str(statistics.get("lifecycle_stage", "-")))
        self._fields["Result Status"].setText(str(statistics.get("result_status", learning_status)))
        self._fields["Last Result"].setText(str(statistics.get("last_result", "-")))
        self._fields["Last Close Type"].setText(str(statistics.get("last_close_type", "-")))
        warning = str(statistics.get("audit_warning", "-"))
        if warning in {"", "-"}:
            warning = str(statistics.get("ledger_warning", "-"))
        self._fields["Ledger Warning"].setText(warning)

    def update_auto_trade_diagnostics(self, status: str, reason: str) -> None:
        """Update visible Auto Trade diagnostic fields without triggering trade execution."""
        self._fields["Auto Trade Status"].setText(status or "-")
        self._fields["Auto Trade Reason"].setText(reason or "-")

    def update_position_monitor(
        self,
        active_position: str,
        open_profit_loss: str,
        ticket: str,
        protection_status: str,
        learning_status: str,
    ) -> None:
        """Update active position monitoring fields."""
        self._fields["Active Position"].setText(active_position)
        self._fields["Open P/L"].setText(open_profit_loss)
        self._fields["Position Ticket"].setText(ticket)
        self._fields["Protection Status"].setText(protection_status)
        # Learning status is kept in the status bar/backend diagnostics to keep the main dashboard clean.
