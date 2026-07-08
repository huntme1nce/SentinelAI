"""
MODULE: SVC-006
FILE: SVC-006-001
Module Name: Trade Manager Service
Version: 2.7.0
Purpose: Owns Sentinel-created trade lifecycle orchestration, ledger persistence, close-result settlement, history repair, and prediction result closure outside the GUI controller.
Dependencies: dataclasses, datetime, json, logging, os, pathlib, sentinel_ai.config, sentinel_ai.models, sentinel_ai.services
Change History:
- 2.7.0: Extracted Sentinel-owned trade lifecycle, ledger statistics, pending-history repair, and maintenance operations from the GUI bootstrapper.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from sentinel_ai.config.config_schema import ManualTradingConfig
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.sentinel_trade import SentinelOwnedTrade
from sentinel_ai.models.trade_execution import ManualTradeOrderResult
from sentinel_ai.mt5.exceptions import Mt5ServiceError
from sentinel_ai.services.contracts import MarketDataServiceContract
from sentinel_ai.services.prediction_lifecycle_service import PredictionLifecycleService


@dataclass(frozen=True)
class TradeLifecycleEvent:
    """Describe a material trade lifecycle transition for the GUI/runtime log."""

    message: str = ""
    closed_trade: SentinelOwnedTrade | None = None
    pending_close_marked: bool = False


@dataclass(frozen=True)
class LedgerMaintenanceCounts:
    """Represent summarized Sentinel ledger maintenance counts."""

    open_count: int
    current_pending_count: int
    stale_count: int
    closed_count: int
    total_count: int


@dataclass(frozen=True)
class LedgerMaintenanceResult:
    """Represent the outcome of one ledger maintenance operation."""

    success: bool
    message: str
    archive_path: Path | None = None
    json_path: Path | None = None
    csv_path: Path | None = None
    repaired_count: int = 0
    unresolved_count: int = 0


class TradeManagerService:
    """Manage Sentinel-owned trade state without depending on Qt widgets."""

    def __init__(
        self,
        *,
        mt5_service: MarketDataServiceContract,
        manual_config: ManualTradingConfig,
        prediction_lifecycle_service: PredictionLifecycleService,
        logger: logging.Logger,
        pending_stale_seconds: int = 300,
        pending_extended_scan_seconds: int = 180,
    ) -> None:
        """Initialize the trade manager and hydrate persisted Sentinel ledger state."""
        self._mt5_service = mt5_service
        self._manual_config = manual_config
        self._prediction_lifecycle_service = prediction_lifecycle_service
        self._logger = logger
        self._pending_stale_seconds = int(pending_stale_seconds)
        self._pending_extended_scan_seconds = int(pending_extended_scan_seconds)
        self._tracked_active_position_ticket: int | None = None
        self._last_reported_closed_trade_key: str | None = None
        self._sentinel_trade_ledger: list[SentinelOwnedTrade] = self.load_sentinel_trade_ledger()
        legacy_trade = self.load_sentinel_owned_trade()
        if legacy_trade is not None:
            self.upsert_sentinel_trade(legacy_trade)
        self._sentinel_owned_trade: SentinelOwnedTrade | None = legacy_trade or self.select_active_sentinel_trade(None)
        self.save_sentinel_owned_trade()

    @property
    def sentinel_owned_trade(self) -> SentinelOwnedTrade | None:
        """Return the current active or latest Sentinel-owned trade under management."""
        return self._sentinel_owned_trade

    @property
    def tracked_active_position_ticket(self) -> int | None:
        """Return the currently tracked active MT5 position ticket."""
        return self._tracked_active_position_ticket

    @property
    def ledger_records(self) -> tuple[SentinelOwnedTrade, ...]:
        """Return an immutable view of all loaded Sentinel ledger records."""
        return tuple(self._sentinel_trade_ledger)

    def activate_symbol_context(self, symbol: str) -> None:
        """Select the latest open trade for the newly active symbol when available."""
        selected = self.select_active_sentinel_trade(symbol)
        if selected is not None:
            self._sentinel_owned_trade = selected
            self.save_sentinel_owned_trade()

    def register_sentinel_owned_trade(
        self,
        snapshot: RiskRewardSnapshot,
        result: ManualTradeOrderResult,
        *,
        source: str = "SENTINEL_APP_MANUAL",
    ) -> SentinelOwnedTrade | None:
        """Persist an accepted Sentinel-created trade and link it to its prediction record."""
        if snapshot.plan is None:
            return None
        prediction_uid = self._prediction_lifecycle_service.record_from_risk_reward_snapshot(snapshot)
        self._prediction_lifecycle_service.mark_trade_active(prediction_uid)
        plan = snapshot.plan
        trade = SentinelOwnedTrade(
            symbol=result.symbol,
            direction=result.direction,
            order_ticket=result.order_ticket,
            deal_ticket=result.deal_ticket,
            position_ticket=result.order_ticket or result.deal_ticket,
            entry_price=result.filled_price or result.requested_price or plan.entry_price,
            stop_loss=result.stop_loss,
            take_profit=result.take_profit,
            risk_reward_ratio=plan.risk_reward_ratio,
            confidence_percentage=snapshot.confidence_percentage,
            timeframe=snapshot.timeframe,
            opened_at=result.sent_at,
            source=source,
            prediction_uid=prediction_uid,
        )
        self._sentinel_owned_trade = trade
        self._tracked_active_position_ticket = trade.position_ticket
        self._last_reported_closed_trade_key = None
        self.upsert_sentinel_trade(trade)
        self.save_sentinel_owned_trade()
        self._logger.info("Registered Sentinel-owned trade through TradeManagerService: %s", trade)
        return trade

    def sync_sentinel_owned_position_ticket(
        self,
        position_snapshot: PositionMonitorSnapshot,
        *,
        active_timeframe: str,
    ) -> None:
        """Update, recover, or reopen the active Sentinel ledger record from MT5 position state."""
        if not position_snapshot.has_open_position or position_snapshot.ticket is None:
            return
        magic_matches = (
            position_snapshot.magic_number is not None
            and int(position_snapshot.magic_number) == int(self._manual_config.magic_number)
        )

        reopened_trade = self.reopen_sentinel_trade_from_active_position(position_snapshot)
        if reopened_trade is not None:
            self._sentinel_owned_trade = reopened_trade
            self._tracked_active_position_ticket = position_snapshot.ticket
            self.save_sentinel_owned_trade()
            self._logger.info("Reopened Sentinel ledger trade because MT5 position is still active: %s", reopened_trade)
            return

        if self._sentinel_owned_trade is None and magic_matches:
            self._sentinel_owned_trade = SentinelOwnedTrade(
                symbol=position_snapshot.symbol,
                direction=position_snapshot.direction,
                order_ticket=None,
                deal_ticket=None,
                position_ticket=position_snapshot.ticket,
                entry_price=position_snapshot.open_price,
                stop_loss=position_snapshot.stop_loss or 0.0,
                take_profit=position_snapshot.take_profit or 0.0,
                risk_reward_ratio=0.0,
                confidence_percentage=0.0,
                timeframe=active_timeframe,
                opened_at=position_snapshot.opened_at or datetime.now(timezone.utc),
            )
            self._tracked_active_position_ticket = position_snapshot.ticket
            self.upsert_sentinel_trade(self._sentinel_owned_trade)
            self.save_sentinel_owned_trade()
            self._logger.info("Recovered active Sentinel-owned trade from MT5 position: %s", self._sentinel_owned_trade)
            return

        if self._sentinel_owned_trade is None:
            return
        if position_snapshot.symbol != self._sentinel_owned_trade.symbol:
            return
        current_ticket = self._sentinel_owned_trade.position_ticket
        candidate_tickets = {
            ticket
            for ticket in (
                current_ticket,
                self._sentinel_owned_trade.order_ticket,
                self._sentinel_owned_trade.deal_ticket,
                self._sentinel_owned_trade.close_ticket,
            )
            if ticket is not None
        }
        ticket_matches = position_snapshot.ticket in candidate_tickets
        if current_ticket is None or ticket_matches or magic_matches:
            if current_ticket != position_snapshot.ticket or self._sentinel_owned_trade.closed:
                self._sentinel_owned_trade = replace(
                    self._sentinel_owned_trade,
                    position_ticket=position_snapshot.ticket,
                    closed=False,
                    close_ticket=None,
                    close_profit=None,
                    close_result="NONE",
                    close_type="",
                    close_reason="",
                    closed_at=None,
                    history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
                    pending_close=False,
                    pending_close_since=None,
                )
                self.upsert_sentinel_trade(self._sentinel_owned_trade)
                self.save_sentinel_owned_trade()
            self._tracked_active_position_ticket = position_snapshot.ticket

    def sentinel_owned_daily_statistics(
        self,
        *,
        position_snapshot: PositionMonitorSnapshot,
        active_symbol: str,
    ) -> DailyTradeStatisticsSnapshot:
        """Return Sentinel-only statistics while guarding active tickets from false close results."""
        if position_snapshot.has_open_position and self.is_position_sentinel_owned(position_snapshot):
            return self.active_trade_guard_statistics(position_snapshot)

        owned_tickets = self.sentinel_owned_tickets()
        if owned_tickets:
            snapshot = self._mt5_service.daily_trade_statistics(
                symbol=active_symbol,
                magic_number=self._manual_config.magic_number,
                owned_position_ticket=self.sentinel_owned_ticket(),
                owned_position_tickets=owned_tickets,
                sentinel_owned_only=True,
                sentinel_comment=self._manual_config.order_comment,
                owned_trade_opened_at=self.current_resolution_opened_at(active_symbol),
                settlement_search_hours=168,
            )
        else:
            snapshot = self._mt5_service.daily_trade_statistics(
                symbol=active_symbol,
                magic_number=self._manual_config.magic_number,
                owned_position_ticket=None,
                owned_position_tickets=None,
                sentinel_owned_only=True,
                sentinel_comment=self._manual_config.order_comment,
                owned_trade_opened_at=self.current_resolution_opened_at(active_symbol),
                settlement_search_hours=168,
            )
        self.sync_ledger_with_statistics(snapshot)
        return self.statistics_with_ledger_totals(snapshot)

    def track_position_lifecycle(
        self,
        position_snapshot: PositionMonitorSnapshot,
        daily_statistics: DailyTradeStatisticsSnapshot,
    ) -> TradeLifecycleEvent:
        """Detect Sentinel-owned open-to-closed transitions without GUI dependencies."""
        if self._sentinel_owned_trade is None:
            self._tracked_active_position_ticket = None
            return TradeLifecycleEvent()

        owned_ticket = self.sentinel_owned_ticket()
        if position_snapshot.has_open_position and self.is_position_sentinel_owned(position_snapshot):
            self._tracked_active_position_ticket = position_snapshot.ticket or owned_ticket
            return TradeLifecycleEvent()

        if owned_ticket is None:
            return TradeLifecycleEvent()

        if daily_statistics.last_closed_result == "NONE":
            self.mark_sentinel_trade_pending_close()
            return TradeLifecycleEvent(
                message="Sentinel-owned trade is pending close result. Waiting for MT5 history settlement.",
                pending_close_marked=True,
            )

        close_ticket = daily_statistics.last_closed_ticket or owned_ticket
        close_key = f"{daily_statistics.symbol}:{close_ticket}:{daily_statistics.last_closed_result}:{daily_statistics.last_closed_profit}"
        if self._last_reported_closed_trade_key == close_key:
            return TradeLifecycleEvent()

        profit_text = f"{daily_statistics.last_closed_profit:.2f}" if daily_statistics.last_closed_profit is not None else "-"
        close_reason = f" | {daily_statistics.last_close_reason}" if daily_statistics.last_close_reason else ""
        match_mode = f" | Match {daily_statistics.history_match_mode}" if daily_statistics.history_match_mode else ""
        message = (
            f"Sentinel app trade closed: {daily_statistics.last_closed_result} | "
            f"{daily_statistics.last_close_type or 'CLOSED'} | "
            f"P/L {profit_text} | Ticket {close_ticket}{close_reason}{match_mode}"
        )
        self._last_reported_closed_trade_key = close_key
        self._tracked_active_position_ticket = None
        closed_trade = self.close_sentinel_owned_trade(daily_statistics, close_ticket)
        self._logger.info(message)
        return TradeLifecycleEvent(message=message, closed_trade=closed_trade)

    def active_trade_guard_statistics(self, position_snapshot: PositionMonitorSnapshot) -> DailyTradeStatisticsSnapshot:
        """Build a zero-closed-trade statistics snapshot for a still-open Sentinel ticket."""
        snapshot = DailyTradeStatisticsSnapshot(
            symbol=position_snapshot.symbol,
            total_closed_trades=0,
            wins=0,
            losses=0,
            breakeven=0,
            win_rate=0.0,
            loss_rate=0.0,
            net_profit=0.0,
            generated_at=datetime.now(timezone.utc),
            message="Sentinel active ticket guard: open position is not counted as closed.",
            last_closed_ticket=None,
            last_closed_profit=None,
            last_closed_result="NONE",
            last_closed_at=None,
            last_close_reason="",
            last_close_type="",
            history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
            sentinel_owned_only=True,
            result_status="1 Sentinel trade open. Waiting for close result.",
        )
        return self.statistics_with_ledger_totals(snapshot)

    def close_sentinel_owned_trade(
        self,
        statistics: DailyTradeStatisticsSnapshot,
        close_ticket: int | None,
    ) -> SentinelOwnedTrade | None:
        """Persist the close result into the Sentinel trade ledger and linked prediction."""
        if self._sentinel_owned_trade is None:
            return None
        self._sentinel_owned_trade = self.trade_with_close_result(
            trade=self._sentinel_owned_trade,
            statistics=statistics,
            close_ticket=close_ticket,
        )
        self.upsert_sentinel_trade(self._sentinel_owned_trade)
        self.save_sentinel_owned_trade()
        self.close_prediction_for_trade(self._sentinel_owned_trade)
        return self._sentinel_owned_trade

    def mark_sentinel_trade_pending_close(self) -> None:
        """Mark the active Sentinel trade as pending close while MT5 history settles."""
        if self._sentinel_owned_trade is None or self._sentinel_owned_trade.closed:
            return
        pending_since = self._sentinel_owned_trade.pending_close_since or datetime.now(timezone.utc)
        self._sentinel_owned_trade = replace(
            self._sentinel_owned_trade,
            pending_close=True,
            pending_close_since=pending_since,
            history_match_mode="SENTINEL_PENDING_CLOSE",
        )
        self.upsert_sentinel_trade(self._sentinel_owned_trade)
        self.save_sentinel_owned_trade()

    def sync_ledger_with_statistics(self, statistics: DailyTradeStatisticsSnapshot) -> None:
        """Update persisted ledger records when MT5 reports a Sentinel-owned close."""
        if statistics.last_closed_result == "NONE" or statistics.last_closed_ticket is None:
            return
        if self._tracked_active_position_ticket is not None and int(statistics.last_closed_ticket) == int(self._tracked_active_position_ticket):
            self._logger.info("Ignored false close result for still-active Sentinel ticket: %s", statistics.last_closed_ticket)
            return
        updated = False
        revised: list[SentinelOwnedTrade] = []
        for trade in self._sentinel_trade_ledger:
            if self.trade_matches_close_ticket(trade, statistics.last_closed_ticket) or self.trade_can_accept_resolved_close(trade, statistics):
                revised.append(self.trade_with_close_result(trade=trade, statistics=statistics, close_ticket=statistics.last_closed_ticket))
                updated = True
            else:
                revised.append(trade)
        if updated:
            self._sentinel_trade_ledger = revised
            for revised_trade in revised:
                if revised_trade.closed and revised_trade.close_result != "NONE":
                    self.close_prediction_for_trade(revised_trade)
            if self._sentinel_owned_trade is not None and (
                self.trade_matches_close_ticket(self._sentinel_owned_trade, statistics.last_closed_ticket)
                or self.trade_can_accept_resolved_close(self._sentinel_owned_trade, statistics)
            ):
                self._sentinel_owned_trade = self.trade_with_close_result(
                    trade=self._sentinel_owned_trade,
                    statistics=statistics,
                    close_ticket=statistics.last_closed_ticket,
                )
            self.save_sentinel_trade_ledger()

    def close_prediction_for_trade(self, trade: SentinelOwnedTrade) -> None:
        """Close a linked prediction record when a Sentinel ledger result is verified."""
        self._prediction_lifecycle_service.close_from_ledger_result(
            prediction_uid=trade.prediction_uid,
            close_result=trade.close_result,
            close_type=trade.close_type,
        )

    @staticmethod
    def trade_with_close_result(
        trade: SentinelOwnedTrade,
        statistics: DailyTradeStatisticsSnapshot,
        close_ticket: int | None,
    ) -> SentinelOwnedTrade:
        """Return a ledger trade updated with a closed-trade outcome."""
        return replace(
            trade,
            closed=True,
            close_ticket=close_ticket,
            close_profit=statistics.last_closed_profit,
            close_result=statistics.last_closed_result,
            close_type=statistics.last_close_type,
            close_reason=statistics.last_close_reason,
            closed_at=statistics.last_closed_at or datetime.now(timezone.utc),
            history_match_mode=statistics.history_match_mode,
            pending_close=False,
            pending_close_since=None,
        )

    @staticmethod
    def trade_matches_close_ticket(trade: SentinelOwnedTrade, close_ticket: int | None) -> bool:
        """Return whether a ledger trade matches a broker close ticket or position id."""
        if close_ticket is None:
            return False
        return int(close_ticket) in {
            int(ticket)
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket, trade.close_ticket)
            if ticket is not None
        }

    def trade_can_accept_resolved_close(self, trade: SentinelOwnedTrade, statistics: DailyTradeStatisticsSnapshot) -> bool:
        """Return True when the latest pending trade can accept a resolved Sentinel close deal."""
        if trade.closed or statistics.last_closed_result == "NONE":
            return False
        if trade.symbol != statistics.symbol or not trade.pending_close:
            return False
        pending_same_symbol = [
            candidate
            for candidate in self._sentinel_trade_ledger
            if candidate.symbol == trade.symbol and candidate.pending_close and not candidate.closed
        ]
        if not pending_same_symbol:
            return False
        latest_pending = sorted(pending_same_symbol, key=lambda item: item.pending_close_since or item.opened_at)[-1]
        return self.sentinel_trade_key(trade) == self.sentinel_trade_key(latest_pending)

    def statistics_with_ledger_totals(self, snapshot: DailyTradeStatisticsSnapshot) -> DailyTradeStatisticsSnapshot:
        """Overlay ledger totals with current-trade priority and stale backlog separation."""
        ledger_records = list(self._sentinel_trade_ledger)
        open_trades = [trade for trade in ledger_records if not trade.closed and not trade.pending_close]
        pending_records = [trade for trade in ledger_records if not trade.closed and trade.pending_close]
        stale_pending_trades = [trade for trade in pending_records if self.is_pending_trade_stale(trade)]
        current_pending_trades = [trade for trade in pending_records if not self.is_pending_trade_stale(trade)]
        closed_trades = [trade for trade in ledger_records if trade.closed and trade.close_result != "NONE"]

        ledger_total_records = len(ledger_records)
        ledger_open = len(open_trades)
        ledger_pending = len(current_pending_trades)
        pending_backlog = len(stale_pending_trades)
        stale_pending_count = len(stale_pending_trades)
        ledger_closed = len(closed_trades)
        ledger_wins = len([trade for trade in closed_trades if trade.close_result == "WIN"])
        ledger_losses = len([trade for trade in closed_trades if trade.close_result == "LOSS"])
        ledger_breakeven = len([trade for trade in closed_trades if trade.close_result == "BREAKEVEN"])
        ledger_net_profit = sum(float(trade.close_profit or 0.0) for trade in closed_trades)
        ledger_win_rate = (ledger_wins / ledger_closed * 100.0) if ledger_closed else 0.0

        diagnostic_pending_trades = current_pending_trades if current_pending_trades else stale_pending_trades
        lifecycle_stage = self.ledger_lifecycle_stage(ledger_open, ledger_pending, ledger_closed, ledger_total_records)
        tracked_ticket = self.diagnostic_tracked_ticket(open_trades, diagnostic_pending_trades, closed_trades)
        pending_age_seconds = self.pending_close_age_seconds(current_pending_trades)
        close_resolver_status = self.close_resolver_status(snapshot, ledger_open, ledger_pending, pending_age_seconds)
        audit_warning = self.audit_warning(snapshot, ledger_open, ledger_pending, stale_pending_count, pending_age_seconds)
        ledger_health = self.ledger_health_status(ledger_open, ledger_pending, stale_pending_count, ledger_closed, ledger_total_records)
        result_status = self.ledger_result_status(snapshot, ledger_open, ledger_pending, ledger_closed, ledger_total_records)
        if ledger_open > 0 and pending_backlog > 0:
            result_status = f"{ledger_open} Sentinel trade open. Waiting for close result. | Stale backlog: {pending_backlog}"

        today_closed = [trade for trade in closed_trades if self.is_trade_closed_today(trade)]
        if today_closed:
            today_total = len(today_closed)
            today_wins = len([trade for trade in today_closed if trade.close_result == "WIN"])
            today_losses = len([trade for trade in today_closed if trade.close_result == "LOSS"])
            today_breakeven = len([trade for trade in today_closed if trade.close_result == "BREAKEVEN"])
            today_net_profit = sum(float(trade.close_profit or 0.0) for trade in today_closed)
            today_win_rate = (today_wins / today_total * 100.0) if today_total else 0.0
            today_loss_rate = (today_losses / today_total * 100.0) if today_total else 0.0
            latest_trade = sorted(today_closed, key=lambda trade: trade.closed_at or trade.opened_at)[-1]
            if ledger_open == 0 and ledger_pending == 0 and pending_backlog == 0:
                result_status = f"Latest closed Sentinel trade: {latest_trade.close_result} {float(latest_trade.close_profit or 0.0):.2f}"
            snapshot = replace(
                snapshot,
                total_closed_trades=today_total,
                wins=today_wins,
                losses=today_losses,
                breakeven=today_breakeven,
                win_rate=today_win_rate,
                loss_rate=today_loss_rate,
                net_profit=today_net_profit,
                message=(
                    f"Ledger today: {today_total} | Wins {today_wins} | Losses {today_losses} | "
                    f"Net P/L {today_net_profit:.2f}"
                ),
                last_closed_ticket=latest_trade.close_ticket or latest_trade.position_ticket,
                last_closed_profit=latest_trade.close_profit,
                last_closed_result=latest_trade.close_result,
                last_closed_at=latest_trade.closed_at,
                last_close_reason=latest_trade.close_reason,
                last_close_type=latest_trade.close_type,
                history_match_mode=latest_trade.history_match_mode or snapshot.history_match_mode,
            )

        return replace(
            snapshot,
            ledger_total_trades=ledger_closed,
            ledger_open_trades=ledger_open,
            ledger_pending_close_trades=ledger_pending,
            ledger_closed_trades=ledger_closed,
            ledger_total_records=ledger_total_records,
            ledger_wins=ledger_wins,
            ledger_losses=ledger_losses,
            ledger_breakeven=ledger_breakeven,
            ledger_win_rate=ledger_win_rate,
            ledger_net_profit=ledger_net_profit,
            result_status=result_status,
            lifecycle_stage=lifecycle_stage,
            tracked_sentinel_ticket=tracked_ticket,
            pending_close_age_seconds=pending_age_seconds,
            close_resolver_status=close_resolver_status,
            audit_warning=audit_warning,
            pending_backlog_trades=pending_backlog,
            stale_pending_trades=stale_pending_count,
            ledger_health=ledger_health,
            build_stage="STAGE_8_TRADE_MANAGER_SERVICE_COMPLETE",
            completion_status="STAGE_8_COMPLETE_AUTO_TRADE_LOCKED",
        )

    @staticmethod
    def ledger_lifecycle_stage(ledger_open: int, ledger_pending: int, ledger_closed: int, ledger_total_records: int) -> str:
        """Return the current lifecycle stage, prioritizing the current active Sentinel trade."""
        if ledger_open > 0:
            return "ACTIVE_OPEN"
        if ledger_pending > 0:
            return "PENDING_CLOSE_SETTLEMENT"
        if ledger_closed > 0:
            return "CLOSED_VERIFIED"
        if ledger_total_records > 0:
            return "LEDGER_UNVERIFIED"
        return "NO_SENTINEL_TRADE"

    def diagnostic_tracked_ticket(
        self,
        open_trades: list[SentinelOwnedTrade],
        pending_trades: list[SentinelOwnedTrade],
        closed_trades: list[SentinelOwnedTrade],
    ) -> int | None:
        """Return the most useful Sentinel ticket for dashboard diagnostics."""
        if self.sentinel_owned_ticket() is not None:
            return self.sentinel_owned_ticket()
        for group in (open_trades, pending_trades, closed_trades):
            if group:
                trade = sorted(group, key=lambda item: item.closed_at or item.pending_close_since or item.opened_at)[-1]
                for ticket in (trade.position_ticket, trade.close_ticket, trade.order_ticket, trade.deal_ticket):
                    if ticket is not None:
                        return int(ticket)
        return None

    @staticmethod
    def pending_close_age_seconds(pending_trades: list[SentinelOwnedTrade]) -> int:
        """Return the age in seconds of the oldest pending close record."""
        if not pending_trades:
            return 0
        now = datetime.now(timezone.utc)
        ages: list[int] = []
        for trade in pending_trades:
            pending_since = trade.pending_close_since
            if pending_since is None:
                continue
            if pending_since.tzinfo is None:
                pending_since = pending_since.replace(tzinfo=timezone.utc)
            ages.append(max(0, int((now - pending_since).total_seconds())))
        return max(ages) if ages else 0

    @staticmethod
    def close_resolver_status(snapshot: DailyTradeStatisticsSnapshot, ledger_open: int, ledger_pending: int, pending_age_seconds: int) -> str:
        """Return a concise close resolver status while prioritizing the current active trade."""
        if snapshot.last_closed_result != "NONE":
            return f"Resolved by {snapshot.history_match_mode or 'MT5_HISTORY'}"
        if ledger_open > 0:
            return "Idle: current Sentinel trade is still open"
        if ledger_pending > 0:
            if pending_age_seconds >= 180:
                return "Resolving: extended MT5 history scan active"
            return "Resolving: waiting for MT5 close deal"
        if snapshot.history_match_mode:
            return snapshot.history_match_mode
        return "-"

    def audit_warning(self, snapshot: DailyTradeStatisticsSnapshot, ledger_open: int, ledger_pending: int, stale_pending_count: int, pending_age_seconds: int) -> str:
        """Return a warning only when the lifecycle state needs user attention."""
        if snapshot.last_closed_result != "NONE":
            return "-"
        if stale_pending_count > 0:
            return f"{stale_pending_count} stale pending Sentinel trade(s) need history review."
        if ledger_open == 0 and ledger_pending > 0 and pending_age_seconds >= self._pending_stale_seconds:
            return "Close result not resolved after 5 minutes. Check MT5 Account History visibility."
        return "-"

    @staticmethod
    def ledger_health_status(ledger_open: int, ledger_pending: int, stale_pending_count: int, ledger_closed: int, ledger_total_records: int) -> str:
        """Return a compact ledger health status for the dashboard."""
        if ledger_total_records == 0:
            return "EMPTY"
        if ledger_open > 0 and stale_pending_count > 0:
            return "CURRENT_ACTIVE_WITH_STALE_PENDING_BACKLOG"
        if ledger_open > 0:
            return "CURRENT_ACTIVE_OK"
        if stale_pending_count > 0:
            return "STALE_PENDING_REVIEW_REQUIRED"
        if ledger_pending > 0:
            return "PENDING_CLOSE_SETTLEMENT"
        if ledger_closed > 0:
            return "VERIFIED"
        return "UNVERIFIED"

    @staticmethod
    def ledger_result_status(snapshot: DailyTradeStatisticsSnapshot, ledger_open: int, ledger_pending: int, ledger_closed: int, ledger_total_records: int) -> str:
        """Return result status, prioritizing the current active Sentinel trade over old pending backlog."""
        if snapshot.last_closed_result != "NONE":
            profit = f"{snapshot.last_closed_profit:.2f}" if snapshot.last_closed_profit is not None else "-"
            return f"Closed result verified: {snapshot.last_closed_result} {profit}"
        if ledger_open > 0:
            backlog = f" | Stale backlog: {ledger_pending}" if ledger_pending > 0 else ""
            return f"{ledger_open} Sentinel trade open. Waiting for close result.{backlog}"
        if ledger_pending > 0:
            return f"{ledger_pending} Sentinel trade pending close result. Waiting for MT5 history settlement."
        if ledger_closed > 0:
            return f"{ledger_closed} closed Sentinel trade(s) saved in ledger."
        if ledger_total_records > 0:
            return "Ledger records found, but no verified closed outcome yet."
        return "No Sentinel ledger trades recorded yet."

    def ledger_maintenance_counts(self) -> LedgerMaintenanceCounts:
        """Return open, current pending, stale pending, closed, and total ledger counts."""
        open_count = 0
        current_pending_count = 0
        stale_count = 0
        closed_count = 0
        for trade in self._sentinel_trade_ledger:
            if trade.closed and trade.close_result != "NONE":
                closed_count += 1
            elif trade.pending_close:
                if self.is_pending_trade_stale(trade):
                    stale_count += 1
                else:
                    current_pending_count += 1
            else:
                open_count += 1
        return LedgerMaintenanceCounts(
            open_count=open_count,
            current_pending_count=current_pending_count,
            stale_count=stale_count,
            closed_count=closed_count,
            total_count=len(self._sentinel_trade_ledger),
        )

    def repair_pending_history_records(self) -> LedgerMaintenanceResult:
        """Attempt to repair unresolved pending ledger records from MT5 history."""
        pending_records = [trade for trade in self._sentinel_trade_ledger if trade.pending_close and not trade.closed]
        if not pending_records:
            return LedgerMaintenanceResult(success=True, message="No pending records to repair.")

        repaired = 0
        unresolved = 0
        revised: list[SentinelOwnedTrade] = []
        repaired_keys: set[str] = set()
        for trade in pending_records:
            statistics = self.resolve_single_pending_trade_from_history(trade)
            if statistics is not None and statistics.last_closed_result != "NONE":
                revised.append(
                    self.trade_with_close_result(
                        trade=trade,
                        statistics=statistics,
                        close_ticket=statistics.last_closed_ticket or trade.position_ticket,
                    )
                )
                repaired += 1
                repaired_keys.add(self.sentinel_trade_key(trade))
            else:
                revised.append(trade)
                unresolved += 1
        other_records = [trade for trade in self._sentinel_trade_ledger if not (trade.pending_close and not trade.closed)]
        self._sentinel_trade_ledger = other_records + revised
        for revised_trade in revised:
            if revised_trade.closed and revised_trade.close_result != "NONE":
                self.close_prediction_for_trade(revised_trade)
        if self._sentinel_owned_trade is not None and self.sentinel_trade_key(self._sentinel_owned_trade) in repaired_keys:
            self._sentinel_owned_trade = self.select_active_sentinel_trade(None)
        self.save_sentinel_owned_trade()
        return LedgerMaintenanceResult(
            success=True,
            message=f"Pending history repair complete.\n\nRepaired: {repaired}\nStill unresolved: {unresolved}",
            repaired_count=repaired,
            unresolved_count=unresolved,
        )

    def resolve_single_pending_trade_from_history(self, trade: SentinelOwnedTrade) -> DailyTradeStatisticsSnapshot | None:
        """Resolve one pending trade from MT5 close history when possible."""
        owned_tickets = self.trade_ticket_tuple(trade)
        try:
            statistics = self._mt5_service.daily_trade_statistics(
                symbol=trade.symbol,
                magic_number=self._manual_config.magic_number,
                owned_position_ticket=trade.position_ticket,
                owned_position_tickets=owned_tickets,
                sentinel_owned_only=True,
                sentinel_comment=self._manual_config.order_comment,
                owned_trade_opened_at=trade.opened_at,
                settlement_search_hours=720,
            )
        except (Mt5ServiceError, ValueError) as error:
            self._logger.warning("Pending history repair failed for %s: %s", trade.position_ticket, error)
            return None
        if statistics.last_closed_result == "NONE":
            return None
        if not self.resolved_close_time_is_valid_for_trade(trade, statistics):
            self._logger.warning(
                "Pending repair rejected close result outside trade time window: trade=%s close=%s",
                trade.position_ticket,
                statistics.last_closed_at,
            )
            return None
        return statistics

    def resolved_close_time_is_valid_for_trade(self, trade: SentinelOwnedTrade, statistics: DailyTradeStatisticsSnapshot) -> bool:
        """Guard repair so a later trade close is not assigned to an older pending record."""
        if statistics.last_closed_at is None:
            return bool(self.trade_matches_close_ticket(trade, statistics.last_closed_ticket))
        closed_at = statistics.last_closed_at if statistics.last_closed_at.tzinfo is not None else statistics.last_closed_at.replace(tzinfo=timezone.utc)
        opened_at = trade.opened_at if trade.opened_at.tzinfo is not None else trade.opened_at.replace(tzinfo=timezone.utc)
        if closed_at < opened_at:
            return False
        next_opened_at = self.next_trade_opened_at(trade)
        if next_opened_at is not None and closed_at > next_opened_at:
            return self.trade_matches_close_ticket(trade, statistics.last_closed_ticket)
        return True

    def next_trade_opened_at(self, trade: SentinelOwnedTrade) -> datetime | None:
        """Return the next Sentinel ledger open time for the same symbol after the selected trade."""
        opened_at = trade.opened_at if trade.opened_at.tzinfo is not None else trade.opened_at.replace(tzinfo=timezone.utc)
        later_times: list[datetime] = []
        for candidate in self._sentinel_trade_ledger:
            if self.sentinel_trade_key(candidate) == self.sentinel_trade_key(trade):
                continue
            if candidate.symbol != trade.symbol:
                continue
            candidate_opened_at = candidate.opened_at if candidate.opened_at.tzinfo is not None else candidate.opened_at.replace(tzinfo=timezone.utc)
            if candidate_opened_at > opened_at:
                later_times.append(candidate_opened_at)
        return min(later_times) if later_times else None

    def archive_stale_pending_records(self) -> LedgerMaintenanceResult:
        """Archive stale pending records without touching open or current pending trades."""
        stale_records = [trade for trade in self._sentinel_trade_ledger if trade.pending_close and not trade.closed and self.is_pending_trade_stale(trade)]
        if not stale_records:
            return LedgerMaintenanceResult(success=True, message="No stale pending records to archive.")

        archive_path = self.sentinel_archived_ledger_path()
        try:
            existing_archive: list[dict[str, object]] = []
            if archive_path.exists():
                loaded = json.loads(archive_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing_archive = [item for item in loaded if isinstance(item, dict)]
            existing_archive.extend(trade.to_dict() for trade in stale_records)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            return LedgerMaintenanceResult(success=False, message=f"Archive failed: {error}")

        stale_keys = {self.sentinel_trade_key(trade) for trade in stale_records}
        self._sentinel_trade_ledger = [trade for trade in self._sentinel_trade_ledger if self.sentinel_trade_key(trade) not in stale_keys]
        if self._sentinel_owned_trade is not None and self.sentinel_trade_key(self._sentinel_owned_trade) in stale_keys:
            self._sentinel_owned_trade = self.select_active_sentinel_trade(None)
        self.save_sentinel_owned_trade()
        return LedgerMaintenanceResult(
            success=True,
            message=f"Archived {len(stale_records)} stale pending record(s).\n\nArchive: {archive_path}",
            archive_path=archive_path,
        )

    def export_sentinel_ledger(self) -> LedgerMaintenanceResult:
        """Export the Sentinel ledger to JSON and CSV files."""
        export_dir = self.sentinel_ledger_export_dir()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = export_dir / f"sentinel_trade_ledger_{timestamp}.json"
        csv_path = export_dir / f"sentinel_trade_ledger_{timestamp}.csv"
        try:
            export_dir.mkdir(parents=True, exist_ok=True)
            payload = [trade.to_dict() for trade in self._sentinel_trade_ledger]
            json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            headers = [
                "symbol", "direction", "order_ticket", "deal_ticket", "position_ticket",
                "entry_price", "stop_loss", "take_profit", "risk_reward_ratio",
                "confidence_percentage", "timeframe", "opened_at", "closed",
                "close_ticket", "close_profit", "close_result", "close_type",
                "close_reason", "closed_at", "history_match_mode", "pending_close",
                "pending_close_since", "source", "prediction_uid",
            ]
            lines = [",".join(headers)]
            for trade in self._sentinel_trade_ledger:
                data = trade.to_dict()
                values = [self.csv_escape(data.get(header, "")) for header in headers]
                lines.append(",".join(values))
            csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError as error:
            return LedgerMaintenanceResult(success=False, message=f"Export failed: {error}")
        return LedgerMaintenanceResult(
            success=True,
            message=f"Export complete.\n\nJSON: {json_path}\nCSV: {csv_path}",
            json_path=json_path,
            csv_path=csv_path,
        )

    def reset_test_ledger_guarded(self) -> LedgerMaintenanceResult:
        """Reset test ledger only when no active Sentinel trade is open."""
        counts = self.ledger_maintenance_counts()
        if counts.open_count > 0:
            return LedgerMaintenanceResult(
                success=False,
                message="Reset blocked because an active Sentinel trade is open. Close or wait for the active trade first.",
            )
        archive_path = self.sentinel_archived_ledger_path()
        try:
            existing_archive: list[dict[str, object]] = []
            if archive_path.exists():
                loaded = json.loads(archive_path.read_text(encoding="utf-8"))
                if isinstance(loaded, list):
                    existing_archive = [item for item in loaded if isinstance(item, dict)]
            existing_archive.extend(trade.to_dict() for trade in self._sentinel_trade_ledger)
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            archive_path.write_text(json.dumps(existing_archive, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            return LedgerMaintenanceResult(success=False, message=f"Reset archive failed: {error}")
        self._sentinel_trade_ledger = []
        self._sentinel_owned_trade = None
        self.save_sentinel_owned_trade()
        return LedgerMaintenanceResult(success=True, message=f"Test ledger reset complete. Archive: {archive_path}", archive_path=archive_path)

    def reopen_sentinel_trade_from_active_position(self, position_snapshot: PositionMonitorSnapshot) -> SentinelOwnedTrade | None:
        """Reopen any ledger record that matches a still-active MT5 position ticket."""
        if position_snapshot.ticket is None:
            return None
        updated_trade: SentinelOwnedTrade | None = None
        revised: list[SentinelOwnedTrade] = []
        for trade in self._sentinel_trade_ledger:
            if self.trade_matches_position_ticket(trade, position_snapshot.ticket):
                updated_trade = replace(
                    trade,
                    symbol=position_snapshot.symbol or trade.symbol,
                    direction=position_snapshot.direction or trade.direction,
                    position_ticket=position_snapshot.ticket,
                    entry_price=position_snapshot.open_price or trade.entry_price,
                    stop_loss=position_snapshot.stop_loss if position_snapshot.stop_loss is not None else trade.stop_loss,
                    take_profit=position_snapshot.take_profit if position_snapshot.take_profit is not None else trade.take_profit,
                    opened_at=position_snapshot.opened_at or trade.opened_at,
                    closed=False,
                    close_ticket=None,
                    close_profit=None,
                    close_result="NONE",
                    close_type="",
                    close_reason="",
                    closed_at=None,
                    history_match_mode="SENTINEL_ACTIVE_TICKET_GUARD",
                    pending_close=False,
                    pending_close_since=None,
                )
                revised.append(updated_trade)
            else:
                revised.append(trade)
        if updated_trade is not None:
            self._sentinel_trade_ledger = revised
            return updated_trade
        return None

    @staticmethod
    def trade_matches_position_ticket(trade: SentinelOwnedTrade, position_ticket: int | None) -> bool:
        """Return whether a ledger record refers to a still-open MT5 position ticket."""
        if position_ticket is None:
            return False
        return int(position_ticket) in {
            int(ticket)
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket, trade.close_ticket)
            if ticket is not None
        }

    def sentinel_owned_ticket(self) -> int | None:
        """Return the most reliable Sentinel-owned trade ticket."""
        if self._sentinel_owned_trade is None:
            return None
        return self._sentinel_owned_trade.position_ticket or self._sentinel_owned_trade.order_ticket or self._sentinel_owned_trade.deal_ticket

    def sentinel_owned_tickets(self) -> tuple[int, ...]:
        """Return all persisted Sentinel-owned ticket references for ledger statistics."""
        values: list[int] = []
        for trade in self._sentinel_trade_ledger:
            for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket):
                if ticket is not None:
                    values.append(int(ticket))
        return tuple(sorted({ticket for ticket in values if ticket > 0}))

    def is_position_sentinel_owned(self, position_snapshot: PositionMonitorSnapshot) -> bool:
        """Return whether the active MT5 position belongs to Sentinel AI."""
        if self._sentinel_owned_trade is None or self._sentinel_owned_trade.closed:
            return False
        if not position_snapshot.has_open_position or position_snapshot.symbol != self._sentinel_owned_trade.symbol:
            return False
        owned_ticket = self.sentinel_owned_ticket()
        ticket_matches = owned_ticket is not None and position_snapshot.ticket == owned_ticket
        close_ticket_matches = self._sentinel_owned_trade.close_ticket is not None and position_snapshot.ticket == self._sentinel_owned_trade.close_ticket
        magic_matches = position_snapshot.magic_number is not None and int(position_snapshot.magic_number) == int(self._manual_config.magic_number)
        return ticket_matches or close_ticket_matches or magic_matches

    def current_resolution_opened_at(self, active_symbol: str) -> datetime | None:
        """Return the active or pending Sentinel trade open time for close-history resolution."""
        if self._sentinel_owned_trade is not None:
            return self._sentinel_owned_trade.opened_at
        candidates = [trade for trade in self._sentinel_trade_ledger if trade.symbol == active_symbol and not trade.closed]
        if not candidates:
            return None
        return sorted(candidates, key=lambda trade: trade.opened_at)[-1].opened_at

    def select_active_sentinel_trade(self, active_symbol: str | None) -> SentinelOwnedTrade | None:
        """Return the latest open Sentinel trade from the ledger for monitoring after restart."""
        open_trades = [trade for trade in self._sentinel_trade_ledger if not trade.closed and (active_symbol is None or trade.symbol == active_symbol)]
        if not open_trades:
            return None
        return sorted(open_trades, key=lambda trade: trade.opened_at)[-1]

    def upsert_sentinel_trade(self, trade: SentinelOwnedTrade) -> None:
        """Insert or update one trade in the persistent Sentinel ledger."""
        key = self.sentinel_trade_key(trade)
        updated = False
        revised: list[SentinelOwnedTrade] = []
        for existing in self._sentinel_trade_ledger:
            if self.sentinel_trade_key(existing) == key or self.trades_share_ticket(existing, trade):
                revised.append(trade)
                updated = True
            else:
                revised.append(existing)
        if not updated:
            revised.append(trade)
        self._sentinel_trade_ledger = revised

    @staticmethod
    def sentinel_trade_key(trade: SentinelOwnedTrade) -> str:
        """Build a stable local key for a Sentinel-created trade."""
        for ticket in (trade.position_ticket, trade.order_ticket, trade.deal_ticket):
            if ticket is not None:
                return f"{trade.symbol}:{ticket}"
        return f"{trade.symbol}:{trade.direction}:{trade.opened_at.isoformat()}"

    @staticmethod
    def trades_share_ticket(first: SentinelOwnedTrade, second: SentinelOwnedTrade) -> bool:
        """Return whether two ledger entries refer to the same broker ticket family."""
        first_tickets = {int(ticket) for ticket in (first.position_ticket, first.order_ticket, first.deal_ticket, first.close_ticket) if ticket is not None}
        second_tickets = {int(ticket) for ticket in (second.position_ticket, second.order_ticket, second.deal_ticket, second.close_ticket) if ticket is not None}
        return bool(first_tickets and second_tickets and first_tickets & second_tickets)

    def is_pending_trade_stale(self, trade: SentinelOwnedTrade) -> bool:
        """Return whether a pending-close record is old enough to be treated as backlog."""
        pending_since = trade.pending_close_since
        if pending_since is None:
            return False
        if pending_since.tzinfo is None:
            pending_since = pending_since.replace(tzinfo=timezone.utc)
        age_seconds = int((datetime.now(timezone.utc) - pending_since).total_seconds())
        return age_seconds >= self._pending_stale_seconds

    @staticmethod
    def is_trade_closed_today(trade: SentinelOwnedTrade) -> bool:
        """Return whether a persisted trade closed on the current UTC date."""
        if trade.closed_at is None:
            return False
        now = datetime.now(timezone.utc)
        closed_at = trade.closed_at if trade.closed_at.tzinfo is not None else trade.closed_at.replace(tzinfo=timezone.utc)
        return closed_at.date() == now.date()

    @staticmethod
    def trade_ticket_tuple(trade: SentinelOwnedTrade) -> tuple[int, ...]:
        """Return all known MT5 ticket references for one Sentinel trade."""
        tickets = [trade.position_ticket, trade.order_ticket, trade.deal_ticket, trade.close_ticket]
        return tuple(sorted({int(ticket) for ticket in tickets if ticket is not None and int(ticket) > 0}))

    def load_sentinel_owned_trade(self) -> SentinelOwnedTrade | None:
        """Load the legacy latest Sentinel-owned trade from local JSON persistence."""
        path = self.sentinel_trade_store_path()
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            trade = SentinelOwnedTrade.from_dict(payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            self._logger.warning("Sentinel-owned trade journal load failed: %s", error)
            return None
        if trade.source not in {"SENTINEL_APP_MANUAL", "SENTINEL_APP_AUTO"}:
            return None
        self._logger.info("Loaded legacy Sentinel-owned trade journal: %s", trade)
        return trade

    def load_sentinel_trade_ledger(self) -> list[SentinelOwnedTrade]:
        """Load all persisted Sentinel-created trades from the local ledger."""
        path = self.sentinel_trade_ledger_path()
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            self._logger.warning("Sentinel trade ledger load failed: %s", error)
            return []
        if not isinstance(payload, list):
            return []
        trades: list[SentinelOwnedTrade] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                trade = SentinelOwnedTrade.from_dict(item)
            except (TypeError, ValueError):
                continue
            if trade.source in {"SENTINEL_APP_MANUAL", "SENTINEL_APP_AUTO"}:
                trades.append(trade)
        self._logger.info("Loaded %s Sentinel trade ledger records.", len(trades))
        return trades

    def save_sentinel_owned_trade(self) -> None:
        """Save the latest Sentinel-owned trade and the full ledger."""
        if self._sentinel_owned_trade is not None:
            path = self.sentinel_trade_store_path()
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(self._sentinel_owned_trade.to_dict(), indent=2), encoding="utf-8")
            except OSError as error:
                self._logger.warning("Sentinel-owned trade journal save failed: %s", error)
        self.save_sentinel_trade_ledger()

    def save_sentinel_trade_ledger(self) -> None:
        """Save every Sentinel-created trade to the persistent ledger."""
        path = self.sentinel_trade_ledger_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = [trade.to_dict() for trade in self._sentinel_trade_ledger]
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as error:
            self._logger.warning("Sentinel trade ledger save failed: %s", error)

    @staticmethod
    def sentinel_base_path() -> Path:
        """Return the local Sentinel app-data base path."""
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / ".sentinel_ai"
        return base_path / "SentinelAI"

    def sentinel_trade_store_path(self) -> Path:
        """Return the legacy latest Sentinel-owned trade journal path."""
        return self.sentinel_base_path() / "sentinel_owned_trade.json"

    def sentinel_trade_ledger_path(self) -> Path:
        """Return the persistent Sentinel trade ledger path."""
        return self.sentinel_base_path() / "sentinel_trade_ledger.json"

    def sentinel_archived_ledger_path(self) -> Path:
        """Return the archived stale Sentinel trade ledger path."""
        return self.sentinel_base_path() / "sentinel_trade_ledger_archived_stale.json"

    def sentinel_ledger_export_dir(self) -> Path:
        """Return the local export directory for ledger maintenance files."""
        return self.sentinel_base_path() / "exports"

    @staticmethod
    def csv_escape(value: object) -> str:
        """Escape one CSV cell without adding a new dependency."""
        text = "" if value is None else str(value)
        escaped = text.replace('"', '""')
        return f'"{escaped}"'
