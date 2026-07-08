"""
MODULE: GUI-003
FILE: GUI-003-002
Module Name: Prediction Panel
Version: 2.19.0
Purpose: Displays current prediction, active-trade health/profit-lock preview, progress ratios, pressure/risk progress, or verified trade-result fields below the chart in the chart-first workspace.
Dependencies: PySide6.QtCore, PySide6.QtWidgets
Change History:
- 2.19.0: Compacted below-chart panel margins, row spacing, and height so the chart keeps priority.
- 2.18.0: Prepared the prediction/active-trade panel for placement below the chart in the chart-first dashboard layout.
- 2.17.0: Added display-only Profit Lock readiness preview for future SL protection stages.
- 2.16.0: Added display-only active-trade health interpretation to simplify TP/SL progress context.
- 2.15.0: Added display-only TP progress, SL risk, and route-state active-trade ratios.
- 2.14.0: Added display-only active-trade risk alert state for TP approach and SL danger visibility.
- 2.13.0: Added active-trade pressure state to show whether the open trade is under TP, SL, neutral, or unknown pressure.
- 2.12.0: Added active-trade progress summary with current price, TP/SL distance, and nearest target.
- 2.11.0: Added trade-result display mode for closed verified Sentinel trades.
- 2.10.0: Added active-trade summary card to remove empty dashboard space and improve readability.
- 2.9.0: Added dynamic panel title and active-trade display mode for GUI clarity.
- 0.1.0: Added current prediction dashboard panel.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class PredictionPanel(QFrame):
    """Display current prediction details without calculating trading decisions."""

    def __init__(self) -> None:
        """Initialize the current prediction panel."""
        super().__init__()
        self.setObjectName("Panel")
        self._fields: dict[str, QLabel] = {}
        self._title_label: QLabel | None = None
        self._summary_label: QLabel | None = None
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        """Build the prediction panel layout."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 10, 12, 10)
        outer_layout.setSpacing(6)
        outer_layout.setAlignment(Qt.AlignTop)

        self._title_label = QLabel("Current Prediction")
        self._title_label.setStyleSheet("font-weight: 700; font-size: 11pt;")
        outer_layout.addWidget(self._title_label)

        self._summary_label = QLabel("Waiting for a validated setup.")
        self._summary_label.setObjectName("ActiveTradeSummary")
        self._summary_label.setWordWrap(True)
        self._summary_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._summary_label.setMinimumHeight(92)
        self._summary_label.setMaximumHeight(135)
        self._summary_label.setStyleSheet(
            "QLabel#ActiveTradeSummary {"
            "border: 1px solid rgba(46, 204, 184, 0.35);"
            "border-radius: 6px;"
            "padding: 8px;"
            "background-color: rgba(9, 24, 31, 0.80);"
            "font-size: 9pt;"
            "}"
        )
        outer_layout.addWidget(self._summary_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)
        labels = ["Direction", "Confidence", "Timeframe", "Reason", "TP", "SL", "Risk Reward"]
        for row, label_text in enumerate(labels):
            label = QLabel(f"{label_text}:")
            label.setObjectName("MutedLabel")
            value = QLabel("-")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._fields[label_text] = value
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1)
        outer_layout.addLayout(grid)
        outer_layout.addStretch(1)

    def clear(self) -> None:
        """Reset the panel to a neutral prediction display state."""
        self._set_title("Current Prediction")
        self._set_summary("Waiting for a validated setup.")
        for value_label in self._fields.values():
            value_label.setText("-")

    def current_title(self) -> str:
        """Return the current panel title for validation and diagnostics."""
        if self._title_label is None:
            return ""
        return self._title_label.text()

    def _set_title(self, title: str) -> None:
        """Set the panel title without exposing QLabel ownership outside the widget."""
        if self._title_label is not None:
            self._title_label.setText(title)

    def _set_summary(self, summary: str) -> None:
        """Set the summary-card text without exposing QLabel ownership outside the widget."""
        if self._summary_label is not None:
            self._summary_label.setText(summary)

    @staticmethod
    def _build_prediction_summary(direction: str, confidence: str, timeframe: str, reason: str) -> str:
        """Build a compact prediction summary for the upper card."""
        clean_reason = " ".join(str(reason).split()).strip() or "No current setup reason."
        return (
            f"Setup: {direction} | Confidence: {confidence} | TF: {timeframe}\n"
            f"Reason: {clean_reason}"
        )

    @staticmethod
    def _build_active_trade_summary(
        direction: str,
        status: str,
        take_profit: str,
        stop_loss: str,
        open_profit_loss: str,
        current_price: str = "-",
        distance_to_take_profit: str = "-",
        distance_to_stop_loss: str = "-",
        closer_target: str = "-",
        trade_pressure: str = "-",
        risk_alert: str = "-",
        take_profit_progress: str = "-",
        stop_loss_risk: str = "-",
        route_state: str = "-",
        trade_health: str = "-",
        profit_lock_state: str = "-",
        next_lock_trigger: str = "-",
        suggested_lock_sl: str = "-",
        suggested_lock_progress: str = "-",
    ) -> str:
        """Build a compact active-trade progress, ratio, risk-alert, and health summary for the upper card."""
        clean_profit_loss = str(open_profit_loss).strip() or "Open P/L -"
        if "P/L" not in clean_profit_loss.upper():
            clean_profit_loss = f"Open P/L {clean_profit_loss}"
        clean_current_price = str(current_price).strip() or "-"
        clean_take_profit_distance = str(distance_to_take_profit).strip() or "-"
        clean_stop_loss_distance = str(distance_to_stop_loss).strip() or "-"
        clean_closer_target = str(closer_target).strip() or "-"
        clean_trade_pressure = str(trade_pressure).strip() or "-"
        clean_risk_alert = str(risk_alert).strip() or "-"
        clean_take_profit_progress = str(take_profit_progress).strip() or "-"
        clean_stop_loss_risk = str(stop_loss_risk).strip() or "-"
        clean_route_state = str(route_state).strip() or "-"
        clean_trade_health = str(trade_health).strip() or "-"
        clean_profit_lock_state = str(profit_lock_state).strip() or "-"
        clean_next_lock_trigger = str(next_lock_trigger).strip() or "-"
        clean_suggested_lock_sl = str(suggested_lock_sl).strip() or "-"
        clean_suggested_lock_progress = str(suggested_lock_progress).strip() or "-"
        return (
            f"{direction} | {status} | Current: {clean_current_price}\n"
            f"{clean_profit_loss} | TP: {take_profit} | SL: {stop_loss}\n"
            f"Distance to TP: {clean_take_profit_distance} | Distance to SL: {clean_stop_loss_distance} | Closer: {clean_closer_target}\n"
            f"Trade Pressure: {clean_trade_pressure} | Risk Alert: {clean_risk_alert}\n"
            f"TP Progress: {clean_take_profit_progress} | SL Risk: {clean_stop_loss_risk} | Route: {clean_route_state}\n"
            f"Trade Health: {clean_trade_health}\n"
            f"Profit Lock: {clean_profit_lock_state} | Next: {clean_next_lock_trigger} | Suggested SL: {clean_suggested_lock_sl} | Lock: {clean_suggested_lock_progress}"
        )

    @staticmethod
    def _build_trade_result_summary(
        result: str,
        close_type: str,
        profit_loss: str,
        ticket: str,
        closed_at: str,
    ) -> str:
        """Build a compact closed-trade result summary for the upper card."""
        clean_result = str(result).strip() or "RESULT"
        clean_close_type = str(close_type).strip() or "Close verified"
        clean_profit_loss = str(profit_loss).strip() or "P/L -"
        if "P/L" not in clean_profit_loss.upper():
            clean_profit_loss = f"P/L {clean_profit_loss}"
        clean_ticket = str(ticket).strip() or "-"
        clean_closed_at = str(closed_at).strip() or "-"
        return (
            f"{clean_result} | {clean_close_type} | {clean_profit_loss}\n"
            f"Ticket: {clean_ticket} | Closed: {clean_closed_at}"
        )

    def current_summary(self) -> str:
        """Return the current summary-card text for validation and diagnostics."""
        if self._summary_label is None:
            return ""
        return self._summary_label.text()

    def update_prediction(
        self,
        direction: str,
        confidence: str,
        timeframe: str,
        reason: str,
        take_profit: str,
        stop_loss: str,
        risk_reward: str,
    ) -> None:
        """Update visible prediction fields from already computed prediction values."""
        self._set_title("Current Prediction")
        self._set_summary(self._build_prediction_summary(direction, confidence, timeframe, reason))
        self._fields["Direction"].setText(direction)
        self._fields["Confidence"].setText(confidence)
        self._fields["Timeframe"].setText(timeframe)
        self._fields["Reason"].setText(reason)
        self._fields["TP"].setText(take_profit)
        self._fields["SL"].setText(stop_loss)
        self._fields["Risk Reward"].setText(risk_reward)


    def update_active_trade(
        self,
        direction: str,
        status: str,
        timeframe: str,
        reason: str,
        take_profit: str,
        stop_loss: str,
        open_profit_loss: str,
        current_price: str = "-",
        distance_to_take_profit: str = "-",
        distance_to_stop_loss: str = "-",
        closer_target: str = "-",
        trade_pressure: str = "-",
        risk_alert: str = "-",
        take_profit_progress: str = "-",
        stop_loss_risk: str = "-",
        route_state: str = "-",
        trade_health: str = "-",
        profit_lock_state: str = "-",
        next_lock_trigger: str = "-",
        suggested_lock_sl: str = "-",
        suggested_lock_progress: str = "-",
    ) -> None:
        """Update the panel as an active-trade health, progress, ratio, and risk-alert monitor instead of a prediction card."""
        self._set_title("Active Trade")
        self._set_summary(
            self._build_active_trade_summary(
                direction=direction,
                status=status,
                take_profit=take_profit,
                stop_loss=stop_loss,
                open_profit_loss=open_profit_loss,
                current_price=current_price,
                distance_to_take_profit=distance_to_take_profit,
                distance_to_stop_loss=distance_to_stop_loss,
                closer_target=closer_target,
                trade_pressure=trade_pressure,
                risk_alert=risk_alert,
                take_profit_progress=take_profit_progress,
                stop_loss_risk=stop_loss_risk,
                route_state=route_state,
                trade_health=trade_health,
                profit_lock_state=profit_lock_state,
                next_lock_trigger=next_lock_trigger,
                suggested_lock_sl=suggested_lock_sl,
                suggested_lock_progress=suggested_lock_progress,
            )
        )
        self._fields["Direction"].setText(direction)
        self._fields["Confidence"].setText(status)
        self._fields["Timeframe"].setText(timeframe)
        self._fields["Reason"].setText(reason)
        self._fields["TP"].setText(take_profit)
        self._fields["SL"].setText(stop_loss)
        self._fields["Risk Reward"].setText(open_profit_loss)

    def update_trade_result(
        self,
        result: str,
        close_type: str,
        timeframe: str,
        reason: str,
        profit_loss: str,
        ticket: str,
        closed_at: str,
    ) -> None:
        """Update the panel as a verified closed-trade result card."""
        self._set_title("Trade Result")
        self._set_summary(
            self._build_trade_result_summary(
                result=result,
                close_type=close_type,
                profit_loss=profit_loss,
                ticket=ticket,
                closed_at=closed_at,
            )
        )
        self._fields["Direction"].setText(result)
        self._fields["Confidence"].setText("Closed Verified")
        self._fields["Timeframe"].setText(timeframe)
        self._fields["Reason"].setText(reason)
        self._fields["TP"].setText(profit_loss)
        self._fields["SL"].setText(close_type)
        self._fields["Risk Reward"].setText(f"Ticket {ticket}" if ticket not in {"", "-"} else "Ticket -")

