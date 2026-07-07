"""
MODULE: MT5-002
FILE: MT5-002-001
Module Name: MetaTrader 5 Service
2.0.1
Purpose: Provides isolated, read-only MT5 connection and market-data access for Sentinel AI.
Dependencies: datetime, logging, pandas, sentinel_ai.config, sentinel_ai.models.market, sentinel_ai.mt5
Change History:
- 2.4.0: Preserved manual/auto order placement backend for guarded auto-trade completion build.
- 2.3.0: Preserved lenient TP close resolver for pending history repair tool.
- 2.2.0: Added lenient Sentinel close resolution using OUT/INOUT/OUT_BY, profit-bearing, and TP/SL reason fallbacks.
- 2.1.0: Preserved robust close resolver for ledger maintenance tool build.
- 2.0.1: Preserved robust close resolver for pending/backlog separation fix.
- 2.0.0: Preserved robust close resolver for final stabilization build.
- 1.9.0.2: Preserved robust close resolver for app helper binding hotfix.
- 1.9.0.1: Bound robust close resolver method inside MetaTrader5Service class and added runtime-safe validation.
- 1.9.0: Added robust Sentinel close-history resolver using multi-day ticket, magic, comment, and opened-time matching.
- 1.8.4.1: Preserved strict close-deal filtering for startup binding hotfix.
- 1.8.4: Preserved strict close-deal filtering for lifecycle diagnostics sprint.
- 1.8.3: Preserved strict close-deal filtering for pending-close settlement sprint.
- 1.8.2: Fixed MT5 deal-entry filtering so entry deals are never misread as closed trades.
- 1.8.1: Preserved Sentinel ledger statistics service for trade result verification dashboard.
- 1.8.0: Preserved multi-ticket Sentinel statistics while app persists closed ledger outcomes.
- 1.7.5: Added multi-ticket Sentinel ledger statistics so all app-created trades can be counted.
- 1.7.4: Added Sentinel magic/comment recovery for app-created trades that were not persisted before restart.
- 1.7.3: Restricted accuracy statistics to Sentinel-owned ticket/position tracking.
- 1.7.2: Added MT5 history fallback matching by symbol/24h and readable close type detection.
- 1.7.1.3: Preserved MT5 monitoring and history extraction for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved MT5 monitoring and history extraction for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved MT5 monitoring and history extraction for candle countdown timer hotfix.
- 1.7.1: Preserved MT5 monitoring and history extraction for countdown timer sprint.
- 1.7.0: Added last closed trade result extraction for lifecycle tracking.
- 1.6.2: Added active-position missing SL/TP protection status warnings.
- 1.6.1.2: Normalized zero SL/TP values to None to prevent invalid chart scaling.
- 1.6.1.1: Preserved MT5 monitoring service for startup lock initialization hotfix.
- 1.6.1: Preserved MT5 position monitoring service for active-trade chart lock patch.
- 0.2.0: Added connection status, account snapshot, symbol validation, and OHLC data fetching without trade execution.
- 0.3.0: Improved MT5 import diagnostics and preserved normalized candle output for market feed service.
- 0.6.0: Added account-specific symbol catalog listing and symbol search support.
- 1.5.0: Added user-confirmed manual market order placement support.
- 1.5.1: Added adaptive filling-mode fallback when broker rejects unsupported filling mode.
- 1.6.0: Added open-position monitoring and same-day closed-deal statistics.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from sentinel_ai.config.config_schema import Mt5Config
from sentinel_ai.models.market import Mt5AccountSnapshot, Mt5ConnectionStatus, SymbolValidationResult
from sentinel_ai.models.symbol import SymbolCatalogItem
from sentinel_ai.models.trade_execution import ManualTradeOrderRequest, ManualTradeOrderResult
from sentinel_ai.models.position_monitoring import DailyTradeStatisticsSnapshot, PositionMonitorSnapshot
from sentinel_ai.mt5.exceptions import Mt5NotConnectedError, Mt5ServiceError
from sentinel_ai.mt5.timeframe_mapper import Mt5TimeframeMapper


class MetaTrader5Service:
    """Isolate all read-only MetaTrader 5 API operations behind one service."""

    def __init__(self, config: Mt5Config, logger: logging.Logger) -> None:
        """Initialize the MT5 service without connecting automatically."""
        self._config = config
        self._logger = logger
        self._mt5: Any | None = None
        self._connected = False
        self._last_status = Mt5ConnectionStatus(False, "MT5 service not initialized.")
        self._last_import_error: str | None = None

    def connect(self) -> Mt5ConnectionStatus:
        """Connect to the local MT5 terminal and return a safe status object."""
        mt5_module = self._load_mt5_module()
        if mt5_module is None:
            message = self._last_import_error or "MetaTrader5 Python package is not installed."
            return self._set_status(False, message)

        initialized = self._initialize_terminal(mt5_module)
        if not initialized:
            error = mt5_module.last_error()
            message = f"MT5 initialization failed: {error}"
            self._logger.warning(message)
            return self._set_status(False, message)

        self._mt5 = mt5_module
        self._connected = True
        status = self._read_status("MT5 connected successfully.")
        self._last_status = status
        self._logger.info(status.message)
        return status

    def disconnect(self) -> None:
        """Shut down the MT5 connection if it was initialized by this service."""
        if self._mt5 is not None and self._connected:
            self._mt5.shutdown()
        self._connected = False
        self._last_status = Mt5ConnectionStatus(False, "MT5 disconnected.")
        self._logger.info("MT5 service disconnected.")

    def connection_status(self) -> Mt5ConnectionStatus:
        """Return the latest known MT5 connection status."""
        if not self._connected or self._mt5 is None:
            return self._last_status
        self._last_status = self._read_status("MT5 connection active.")
        return self._last_status

    def account_snapshot(self) -> Mt5AccountSnapshot | None:
        """Return current account details when connected, otherwise None."""
        self._require_connection()
        account = self._mt5.account_info()
        if account is None:
            self._logger.warning("MT5 account_info returned no account data.")
            return None
        return Mt5AccountSnapshot(
            login=int(account.login),
            server=str(account.server),
            name=str(account.name),
            company=str(account.company),
            currency=str(account.currency),
            balance=float(account.balance),
            equity=float(account.equity),
            margin=float(account.margin),
            free_margin=float(account.margin_free),
            leverage=int(account.leverage),
        )

    def validate_symbol(self, symbol: str) -> SymbolValidationResult:
        """Validate a symbol and select it in Market Watch when broker permits it."""
        self._require_connection()
        normalized_symbol = symbol.strip()
        if not normalized_symbol:
            return SymbolValidationResult(symbol=symbol, valid=False, visible=False, selected=False, message="Symbol is empty.")

        symbol_info = self._mt5.symbol_info(normalized_symbol)
        if symbol_info is None:
            return SymbolValidationResult(
                symbol=normalized_symbol,
                valid=False,
                visible=False,
                selected=False,
                message="Symbol not found in MT5 terminal.",
            )

        selected = bool(symbol_info.visible)
        if self._config.require_visible_symbol and not selected:
            selected = bool(self._mt5.symbol_select(normalized_symbol, True))

        visible = bool(self._mt5.symbol_info(normalized_symbol).visible) if selected else bool(symbol_info.visible)
        message = "Symbol validated." if visible else "Symbol exists but is not visible in Market Watch."
        return SymbolValidationResult(
            symbol=normalized_symbol,
            valid=True,
            visible=visible,
            selected=selected,
            message=message,
            digits=int(symbol_info.digits),
            point=float(symbol_info.point),
            spread=int(symbol_info.spread),
        )


    def list_symbols(self) -> tuple[SymbolCatalogItem, ...]:
        """Return all broker symbols available from the active MT5 account."""
        self._require_connection()
        raw_symbols = self._mt5.symbols_get()
        if raw_symbols is None:
            raise Mt5ServiceError(f"MT5 returned no symbol catalog: {self._mt5.last_error()}")
        catalog = tuple(self._to_symbol_catalog_item(raw_symbol) for raw_symbol in raw_symbols)
        return tuple(sorted(catalog, key=lambda item: item.symbol.upper()))

    def search_symbols(self, query: str, limit: int) -> tuple[SymbolCatalogItem, ...]:
        """Return broker symbols whose name, description, or path contains the query."""
        clean_query = str(query).strip().upper()
        clean_limit = max(0, int(limit))
        if clean_limit == 0:
            return ()
        catalog = self.list_symbols()
        if not clean_query:
            return catalog[:clean_limit]
        matches = []
        for item in catalog:
            searchable = f"{item.symbol} {item.description} {item.path}".upper()
            if clean_query in searchable:
                matches.append(item)
        return tuple(matches[:clean_limit])

    def place_manual_market_order(self, request: ManualTradeOrderRequest, one_position_per_symbol: bool) -> ManualTradeOrderResult:
        """Place one user-confirmed manual market order through MT5."""
        self._require_connection()
        normalized_symbol = request.symbol.strip()
        validation = self.validate_symbol(normalized_symbol)
        if not validation.valid or not validation.visible:
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=None,
                filled_price=None,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                message=validation.message,
            )

        if one_position_per_symbol and self._has_open_position(normalized_symbol):
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=None,
                filled_price=None,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                message=f"Manual order blocked: existing open position found for {normalized_symbol}.",
            )

        tick = self._mt5.symbol_info_tick(normalized_symbol)
        symbol_info = self._mt5.symbol_info(normalized_symbol)
        if tick is None or symbol_info is None:
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=None,
                filled_price=None,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                message=f"Manual order blocked: no current tick or symbol info for {normalized_symbol}.",
            )

        direction = request.direction.strip().upper()
        if direction not in {"BUY", "SELL"}:
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=None,
                filled_price=None,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                message=f"Manual order blocked: unsupported direction {request.direction}.",
            )

        order_type = self._mt5.ORDER_TYPE_BUY if direction == "BUY" else self._mt5.ORDER_TYPE_SELL
        price = float(tick.ask if direction == "BUY" else tick.bid)
        base_payload = {
            "action": self._mt5.TRADE_ACTION_DEAL,
            "symbol": normalized_symbol,
            "volume": float(request.volume),
            "type": order_type,
            "price": price,
            "sl": float(request.stop_loss),
            "tp": float(request.take_profit),
            "deviation": int(request.deviation_points),
            "magic": int(request.magic_number),
            "comment": request.comment,
            "type_time": self._mt5.ORDER_TIME_GTC,
        }

        payload = None
        check_result = None
        check_messages: list[str] = []
        for filling_label, filling_mode in self._candidate_filling_modes(request.order_filling, symbol_info):
            candidate_payload = dict(base_payload)
            candidate_payload["type_filling"] = filling_mode
            check_result = self._mt5.order_check(candidate_payload)
            if check_result is None:
                check_messages.append(f"{filling_label}: order_check failed {self._mt5.last_error()}")
                continue

            check_retcode = int(getattr(check_result, "retcode", -1))
            check_comment = str(getattr(check_result, "comment", "") or check_retcode)
            if self._is_check_success(check_retcode):
                payload = candidate_payload
                break
            check_messages.append(f"{filling_label}: {check_comment}")

        if payload is None:
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=price,
                filled_price=None,
                retcode=int(getattr(check_result, "retcode", -1)) if check_result is not None else None,
                order_ticket=None,
                deal_ticket=None,
                message=f"Manual order check rejected after filling fallback: {' | '.join(check_messages)}",
            )

        send_result = self._mt5.order_send(payload)
        if send_result is None:
            error = self._mt5.last_error()
            return self._manual_order_result(
                accepted=False,
                request=request,
                requested_price=price,
                filled_price=None,
                retcode=None,
                order_ticket=None,
                deal_ticket=None,
                message=f"Manual order send failed: {error}",
            )

        retcode = int(getattr(send_result, "retcode", -1))
        accepted = self._is_send_success(retcode)
        message = "Manual MT5 order placed." if accepted else f"Manual order rejected: {getattr(send_result, 'comment', '') or retcode}"
        return self._manual_order_result(
            accepted=accepted,
            request=request,
            requested_price=price,
            filled_price=float(getattr(send_result, "price", price) or price),
            retcode=retcode,
            order_ticket=int(getattr(send_result, "order", 0) or 0) or None,
            deal_ticket=int(getattr(send_result, "deal", 0) or 0) or None,
            message=message,
        )

    def monitor_symbol_position(self, symbol: str, magic_number: int | None = None) -> PositionMonitorSnapshot:
        """Return the current open-position state for one symbol."""
        self._require_connection()
        normalized_symbol = symbol.strip()
        positions = self._mt5.positions_get(symbol=normalized_symbol)
        monitored_at = datetime.now(timezone.utc)
        if positions is None:
            return PositionMonitorSnapshot(
                symbol=normalized_symbol,
                has_open_position=False,
                ticket=None,
                direction="NONE",
                volume=0.0,
                open_price=None,
                current_price=None,
                stop_loss=None,
                take_profit=None,
                profit=0.0,
                swap=0.0,
                commission=0.0,
                magic_number=None,
                comment="",
                opened_at=None,
                monitored_at=monitored_at,
                message=f"No open position data returned for {normalized_symbol}.",
            )

        filtered_positions = list(positions)
        if magic_number is not None:
            magic_filtered = [position for position in filtered_positions if int(getattr(position, "magic", 0) or 0) == int(magic_number)]
            if magic_filtered:
                filtered_positions = magic_filtered

        if not filtered_positions:
            return PositionMonitorSnapshot(
                symbol=normalized_symbol,
                has_open_position=False,
                ticket=None,
                direction="NONE",
                volume=0.0,
                open_price=None,
                current_price=None,
                stop_loss=None,
                take_profit=None,
                profit=0.0,
                swap=0.0,
                commission=0.0,
                magic_number=magic_number,
                comment="",
                opened_at=None,
                monitored_at=monitored_at,
                message=f"No active Sentinel AI position for {normalized_symbol}.",
            )

        position = filtered_positions[0]
        position_type = int(getattr(position, "type", -1))
        direction = "BUY" if position_type == int(getattr(self._mt5, "POSITION_TYPE_BUY", 0)) else "SELL"
        opened_at = None
        raw_time = getattr(position, "time", None)
        if raw_time is not None:
            try:
                opened_at = datetime.fromtimestamp(int(raw_time), tz=timezone.utc)
            except (TypeError, ValueError, OSError):
                opened_at = None
        ticket = int(getattr(position, "ticket", 0) or 0) or None
        profit = float(getattr(position, "profit", 0.0) or 0.0)
        raw_open_price = float(getattr(position, "price_open", 0.0) or 0.0)
        raw_current_price = float(getattr(position, "price_current", 0.0) or 0.0)
        raw_stop_loss = float(getattr(position, "sl", 0.0) or 0.0)
        raw_take_profit = float(getattr(position, "tp", 0.0) or 0.0)
        stop_loss = raw_stop_loss if raw_stop_loss > 0 else None
        take_profit = raw_take_profit if raw_take_profit > 0 else None
        missing_stop_loss = stop_loss is None
        missing_take_profit = take_profit is None
        protection_status = self._position_protection_status(missing_stop_loss, missing_take_profit)
        return PositionMonitorSnapshot(
            symbol=normalized_symbol,
            has_open_position=True,
            ticket=ticket,
            direction=direction,
            volume=float(getattr(position, "volume", 0.0) or 0.0),
            open_price=raw_open_price if raw_open_price > 0 else None,
            current_price=raw_current_price if raw_current_price > 0 else None,
            stop_loss=stop_loss,
            take_profit=take_profit,
            profit=profit,
            swap=float(getattr(position, "swap", 0.0) or 0.0),
            commission=float(getattr(position, "commission", 0.0) or 0.0),
            magic_number=int(getattr(position, "magic", 0) or 0),
            comment=str(getattr(position, "comment", "") or ""),
            opened_at=opened_at,
            monitored_at=monitored_at,
            message=(
                f"Active {direction} position {ticket or '-'} | "
                f"P/L {profit:.2f} | SL {self._format_optional_price(stop_loss)} | "
                f"TP {self._format_optional_price(take_profit)} | {protection_status}"
            ),
            missing_stop_loss=missing_stop_loss,
            missing_take_profit=missing_take_profit,
            protection_status=protection_status,
        )

    def daily_trade_statistics(
        self,
        symbol: str,
        magic_number: int | None = None,
        owned_position_ticket: int | None = None,
        owned_position_tickets: tuple[int, ...] | None = None,
        sentinel_owned_only: bool = True,
        sentinel_comment: str | None = None,
        owned_trade_opened_at: datetime | None = None,
        settlement_search_hours: int = 168,
    ) -> DailyTradeStatisticsSnapshot:
        """Return closed-deal statistics for Sentinel-owned tickets only by default."""
        self._require_connection()
        normalized_symbol = symbol.strip()
        now = datetime.now(timezone.utc)
        lookback_hours = max(24, int(settlement_search_hours or 168))
        opened_floor = self._normalize_datetime(owned_trade_opened_at)
        if opened_floor is not None:
            history_start = min(now - timedelta(hours=lookback_hours), opened_floor - timedelta(minutes=15))
        else:
            history_start = now - timedelta(hours=lookback_hours)

        deals = self._mt5.history_deals_get(history_start, now)
        owned_ticket_set = self._normalize_owned_tickets(owned_position_ticket, owned_position_tickets)
        if sentinel_owned_only and not owned_ticket_set:
            filtered = self._filter_sentinel_recovery_deals(
                deals=deals,
                symbol=normalized_symbol,
                magic_number=magic_number,
                sentinel_comment=sentinel_comment,
            )
            match_mode = "SENTINEL_MAGIC_COMMENT_RECOVERY" if filtered else "SENTINEL_ONLY_NO_TICKET"
            if not filtered:
                return DailyTradeStatisticsSnapshot(
                    symbol=normalized_symbol,
                    total_closed_trades=0,
                    wins=0,
                    losses=0,
                    breakeven=0,
                    win_rate=0.0,
                    loss_rate=0.0,
                    net_profit=0.0,
                    generated_at=now,
                    message="No Sentinel app trade closed yet.",
                    history_match_mode=match_mode,
                    sentinel_owned_only=True,
                )
        elif sentinel_owned_only:
            filtered = self._filter_closed_deals(
                deals,
                normalized_symbol,
                magic_number,
                require_magic=False,
                owned_position_ticket=owned_position_ticket,
                owned_position_tickets=owned_ticket_set,
            )
            match_mode = "SENTINEL_TICKET_MATCH" if filtered else "SENTINEL_TICKET_NOT_CLOSED"
            if not filtered:
                filtered = self._filter_magic_after_open_close_deals(
                    deals=deals,
                    symbol=normalized_symbol,
                    magic_number=magic_number,
                    opened_at=opened_floor,
                    sentinel_comment=sentinel_comment,
                )
                match_mode = "SENTINEL_MAGIC_AFTER_OPEN_RESOLUTION" if filtered else match_mode
        else:
            day_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            today_deals = self._mt5.history_deals_get(day_start, now)
            filtered = self._filter_closed_deals(today_deals, normalized_symbol, magic_number, require_magic=True)
            match_mode = "MAGIC_TODAY"
            if not filtered:
                filtered = self._filter_closed_deals(today_deals, normalized_symbol, magic_number, require_magic=False)
                match_mode = "SYMBOL_TODAY_FALLBACK" if filtered else match_mode
            if not filtered:
                filtered = self._filter_closed_deals(deals, normalized_symbol, magic_number, require_magic=True)
                match_mode = "MAGIC_24H_FALLBACK" if filtered else match_mode
            if not filtered:
                filtered = self._filter_closed_deals(deals, normalized_symbol, magic_number, require_magic=False)
                match_mode = "SYMBOL_24H_FALLBACK" if filtered else "NONE"

        if deals is None and not filtered:
            return DailyTradeStatisticsSnapshot(
                symbol=normalized_symbol,
                total_closed_trades=0,
                wins=0,
                losses=0,
                breakeven=0,
                win_rate=0.0,
                loss_rate=0.0,
                net_profit=0.0,
                generated_at=now,
                message=f"No deal history returned for {normalized_symbol}.",
                history_match_mode="NONE",
                sentinel_owned_only=sentinel_owned_only,
            )

        profits = [float(getattr(deal, "profit", 0.0) or 0.0) for deal in filtered]
        wins = len([profit for profit in profits if profit > 0])
        losses = len([profit for profit in profits if profit < 0])
        breakeven = len([profit for profit in profits if profit == 0])
        total = len(profits)
        win_rate = (wins / total * 100.0) if total else 0.0
        loss_rate = (losses / total * 100.0) if total else 0.0
        net_profit = sum(profits)

        last_closed_deal = self._latest_closed_deal(filtered)
        last_closed_ticket = None
        last_closed_profit = None
        last_closed_result = "NONE"
        last_closed_at = None
        last_close_reason = ""
        last_close_type = ""
        if last_closed_deal is not None:
            last_closed_ticket = int(getattr(last_closed_deal, "position_id", 0) or getattr(last_closed_deal, "ticket", 0) or 0) or None
            last_closed_profit = float(getattr(last_closed_deal, "profit", 0.0) or 0.0)
            last_closed_result = self._closed_trade_result(last_closed_profit)
            raw_close_time = getattr(last_closed_deal, "time", None)
            if raw_close_time is not None:
                try:
                    last_closed_at = datetime.fromtimestamp(int(raw_close_time), tz=timezone.utc)
                except (TypeError, ValueError, OSError):
                    last_closed_at = None
            last_close_type = self._deal_close_type(getattr(last_closed_deal, "reason", None), last_closed_profit)
            last_close_reason = self._deal_reason_label(getattr(last_closed_deal, "reason", None), last_close_type)

        if sentinel_owned_only and not filtered:
            message = "Sentinel app trade is still open or waiting for MT5 close history."
        else:
            last_result_text = (
                f" | Last {last_closed_result} {last_closed_profit:.2f} | {last_close_type}"
                if last_closed_profit is not None
                else ""
            )
            mode_text = f" | Match {match_mode}" if match_mode != "NONE" else ""
            message = f"Closed: {total} | Wins {wins} | Losses {losses} | Net P/L {net_profit:.2f}{last_result_text}{mode_text}"

        return DailyTradeStatisticsSnapshot(
            symbol=normalized_symbol,
            total_closed_trades=total,
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate=win_rate,
            loss_rate=loss_rate,
            net_profit=net_profit,
            generated_at=now,
            message=message,
            last_closed_ticket=last_closed_ticket,
            last_closed_profit=last_closed_profit,
            last_closed_result=last_closed_result,
            last_closed_at=last_closed_at,
            last_close_reason=last_close_reason,
            last_close_type=last_close_type,
            history_match_mode=match_mode,
            sentinel_owned_only=sentinel_owned_only,
        )

    def _filter_magic_after_open_close_deals(
        self,
        deals: Any,
        symbol: str,
        magic_number: int | None,
        opened_at: datetime | None,
        sentinel_comment: str | None,
    ) -> list[Any]:
        """Resolve a Sentinel close deal when broker history does not expose the original position ticket."""
        if deals is None or magic_number is None:
            return []
        opened_floor = self._normalize_datetime(opened_at)
        expected_comment = str(sentinel_comment or "").strip()
        resolved: list[Any] = []
        for deal in deals:
            if str(getattr(deal, "symbol", "") or "") != symbol:
                continue
            if int(getattr(deal, "magic", 0) or 0) != int(magic_number):
                continue
            if not self._is_close_or_profit_resolution_deal(deal):
                continue
            deal_time = self._deal_datetime(deal)
            if opened_floor is not None and deal_time is not None and deal_time < opened_floor - timedelta(hours=12):
                continue
            deal_comment = str(getattr(deal, "comment", "") or "").strip()
            if expected_comment and deal_comment and expected_comment not in deal_comment:
                continue
            resolved.append(deal)
        return resolved

    def _filter_sentinel_recovery_deals(
        self,
        deals: Any,
        symbol: str,
        magic_number: int | None,
        sentinel_comment: str | None,
    ) -> list[Any]:
        """Recover app-created closed trades by strict Sentinel magic/comment matching."""
        if deals is None or magic_number is None:
            return []
        expected_comment = str(sentinel_comment or "").strip()
        recovered: list[Any] = []
        for deal in deals:
            if str(getattr(deal, "symbol", "") or "") != symbol:
                continue
            if int(getattr(deal, "magic", 0) or 0) != int(magic_number):
                continue
            if not self._is_close_or_profit_resolution_deal(deal):
                continue
            deal_comment = str(getattr(deal, "comment", "") or "").strip()
            if expected_comment and deal_comment and expected_comment not in deal_comment:
                continue
            recovered.append(deal)
        return recovered

    def _filter_closed_deals(
        self,
        deals: Any,
        symbol: str,
        magic_number: int | None,
        require_magic: bool,
        owned_position_ticket: int | None = None,
        owned_position_tickets: tuple[int, ...] | None = None,
    ) -> list[Any]:
        """Filter MT5 history deals for closed trades, optionally requiring Sentinel-owned tickets."""
        if deals is None:
            return []
        owned_ticket_set = self._normalize_owned_tickets(owned_position_ticket, owned_position_tickets)
        filtered: list[Any] = []
        for deal in deals:
            if str(getattr(deal, "symbol", "") or "") != symbol:
                continue
            ticket_matches_owner = False
            if owned_ticket_set:
                position_id = int(getattr(deal, "position_id", 0) or 0)
                deal_ticket = int(getattr(deal, "ticket", 0) or 0)
                order_ticket = int(getattr(deal, "order", 0) or 0)
                ticket_matches_owner = bool({position_id, deal_ticket, order_ticket} & set(owned_ticket_set))
                if not ticket_matches_owner:
                    continue
            if require_magic and magic_number is not None and int(getattr(deal, "magic", 0) or 0) != int(magic_number):
                continue
            if not self._is_strict_close_entry_deal(deal):
                if not (ticket_matches_owner and self._is_close_or_profit_resolution_deal(deal)):
                    continue
            filtered.append(deal)
        return filtered

    def _is_strict_close_entry_deal(self, deal: Any) -> bool:
        """Return True when an MT5 deal entry is a close-style entry."""
        deal_entry = getattr(deal, "entry", None)
        if deal_entry is None:
            return False
        try:
            return int(deal_entry) in self._close_entry_values()
        except (TypeError, ValueError):
            return False

    def _close_entry_values(self) -> set[int]:
        """Return MT5 entry constants that represent closing or settlement deals."""
        values = {
            int(getattr(self._mt5, "DEAL_ENTRY_OUT", 1)),
            int(getattr(self._mt5, "DEAL_ENTRY_INOUT", 2)),
            int(getattr(self._mt5, "DEAL_ENTRY_OUT_BY", 3)),
        }
        return {value for value in values if value >= 0}

    def _is_close_or_profit_resolution_deal(self, deal: Any) -> bool:
        """Return True for close-style, TP/SL reason, or profit-bearing settlement deals."""
        if self._is_strict_close_entry_deal(deal):
            return True
        reason = getattr(deal, "reason", None)
        try:
            reason_code = int(reason) if reason is not None else None
        except (TypeError, ValueError):
            reason_code = None
        if reason_code in {
            int(getattr(self._mt5, "DEAL_REASON_TP", -10001)),
            int(getattr(self._mt5, "DEAL_REASON_SL", -10002)),
            int(getattr(self._mt5, "DEAL_REASON_SO", -10007)),
        }:
            return True
        return self._is_profit_bearing_deal(deal)

    @staticmethod
    def _is_profit_bearing_deal(deal: Any) -> bool:
        """Return True when a deal carries realized P/L, commission, swap, or fee."""
        realized_values = (
            getattr(deal, "profit", 0.0),
            getattr(deal, "commission", 0.0),
            getattr(deal, "swap", 0.0),
            getattr(deal, "fee", 0.0),
        )
        for value in realized_values:
            try:
                if abs(float(value or 0.0)) > 0.0000001:
                    return True
            except (TypeError, ValueError):
                continue
        return False

    @staticmethod
    def _normalize_owned_tickets(
        owned_position_ticket: int | None,
        owned_position_tickets: tuple[int, ...] | None,
    ) -> tuple[int, ...]:
        """Normalize one or many Sentinel-owned ticket references."""
        values: list[int] = []
        if owned_position_ticket is not None:
            values.append(int(owned_position_ticket))
        if owned_position_tickets is not None:
            values.extend(int(ticket) for ticket in owned_position_tickets if ticket is not None)
        return tuple(sorted({ticket for ticket in values if ticket > 0}))

    @staticmethod
    def _normalize_datetime(value: datetime | None) -> datetime | None:
        """Normalize optional datetime values to UTC-aware datetimes."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _deal_datetime(deal: Any) -> datetime | None:
        """Return a UTC close datetime from an MT5 deal object."""
        raw_time = getattr(deal, "time", None)
        if raw_time is None:
            return None
        try:
            return datetime.fromtimestamp(int(raw_time), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def _latest_closed_deal(deals: list[Any]) -> Any | None:
        """Return the latest closed deal by broker close time."""
        if not deals:
            return None
        return sorted(deals, key=lambda deal: int(getattr(deal, "time", 0) or 0))[-1]

    @staticmethod
    def _closed_trade_result(profit: float) -> str:
        """Convert a closed deal profit into a clear result label."""
        if profit > 0:
            return "WIN"
        if profit < 0:
            return "LOSS"
        return "BREAKEVEN"

    def _deal_close_type(self, reason: Any, profit: float | None) -> str:
        """Return a readable close type from MT5 reason constants when available."""
        if reason is not None:
            try:
                reason_code = int(reason)
            except (TypeError, ValueError):
                reason_code = None
            if reason_code is not None:
                if reason_code == int(getattr(self._mt5, "DEAL_REASON_TP", -10001)):
                    return "TP HIT"
                if reason_code == int(getattr(self._mt5, "DEAL_REASON_SL", -10002)):
                    return "SL HIT"
                if reason_code in {
                    int(getattr(self._mt5, "DEAL_REASON_CLIENT", -10003)),
                    int(getattr(self._mt5, "DEAL_REASON_MOBILE", -10004)),
                    int(getattr(self._mt5, "DEAL_REASON_WEB", -10005)),
                }:
                    return "MANUAL CLOSE"
                if reason_code == int(getattr(self._mt5, "DEAL_REASON_EXPERT", -10006)):
                    return "EA CLOSE"
                if reason_code == int(getattr(self._mt5, "DEAL_REASON_SO", -10007)):
                    return "STOP OUT"
        if profit is None:
            return "CLOSED"
        if profit > 0:
            return "MANUAL/OTHER PROFIT CLOSE"
        if profit < 0:
            return "MANUAL/OTHER LOSS CLOSE"
        return "MANUAL/OTHER BREAKEVEN CLOSE"

    @staticmethod
    def _deal_reason_label(reason: Any, close_type: str) -> str:
        """Return a readable broker close reason when available."""
        if reason is None:
            return close_type
        try:
            return f"{close_type} | Broker reason {int(reason)}"
        except (TypeError, ValueError):
            return f"{close_type} | Broker reason {reason}"

    def fetch_ohlc(self, symbol: str, timeframe: str, bar_count: int | None = None) -> pd.DataFrame:
        """Fetch OHLCV bars from MT5 as a normalized pandas DataFrame."""
        self._require_connection()
        requested_count = self._resolve_bar_count(bar_count)
        validation = self.validate_symbol(symbol)
        if not validation.valid or not validation.visible:
            raise Mt5ServiceError(validation.message)

        timeframe_constant = Mt5TimeframeMapper.to_mt5_constant(timeframe, self._mt5)
        rates = self._mt5.copy_rates_from_pos(validation.symbol, timeframe_constant, 0, requested_count)
        if rates is None:
            raise Mt5ServiceError(f"MT5 returned no rates for {validation.symbol} {timeframe}: {self._mt5.last_error()}")

        data_frame = pd.DataFrame(rates)
        if data_frame.empty:
            return self._empty_ohlc_frame()
        data_frame["time"] = pd.to_datetime(data_frame["time"], unit="s", utc=True)
        ordered_columns = ["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]
        return data_frame.loc[:, ordered_columns]


    @staticmethod
    def _to_symbol_catalog_item(raw_symbol: Any) -> SymbolCatalogItem:
        """Convert an MT5 symbol_info tuple into an immutable catalog item."""
        point_value = getattr(raw_symbol, "point", None)
        return SymbolCatalogItem(
            symbol=str(getattr(raw_symbol, "name", "")),
            description=str(getattr(raw_symbol, "description", "") or ""),
            path=str(getattr(raw_symbol, "path", "") or ""),
            visible=bool(getattr(raw_symbol, "visible", False)),
            digits=int(getattr(raw_symbol, "digits", 0)) if getattr(raw_symbol, "digits", None) is not None else None,
            point=float(point_value) if point_value is not None else None,
            currency_base=str(getattr(raw_symbol, "currency_base", "") or "") or None,
            currency_profit=str(getattr(raw_symbol, "currency_profit", "") or "") or None,
            trade_mode=int(getattr(raw_symbol, "trade_mode", 0)) if getattr(raw_symbol, "trade_mode", None) is not None else None,
        )

    @staticmethod
    def _position_protection_status(missing_stop_loss: bool, missing_take_profit: bool) -> str:
        """Return a clear active-position protection warning."""
        if missing_stop_loss and missing_take_profit:
            return "WARNING: Missing SL and TP"
        if missing_stop_loss:
            return "WARNING: Missing SL"
        if missing_take_profit:
            return "WARNING: Missing TP"
        return "Protected: SL and TP attached"

    @staticmethod
    def _format_optional_price(price: float | None) -> str:
        """Format optional broker position levels without turning missing TP/SL into zero."""
        return "-" if price is None else f"{price:.2f}"

    def _has_open_position(self, symbol: str) -> bool:
        """Return True when the active MT5 account already has an open position for a symbol."""
        positions = self._mt5.positions_get(symbol=symbol)
        if positions is None:
            return False
        return len(positions) > 0

    def _candidate_filling_modes(self, order_filling: str, symbol_info: Any) -> tuple[tuple[str, int], ...]:
        """Return broker-safe filling mode candidates for adaptive order_check fallback."""
        configured = str(order_filling).strip().upper()
        known_modes = (
            ("FOK", self._mt5.ORDER_FILLING_FOK),
            ("IOC", self._mt5.ORDER_FILLING_IOC),
            ("RETURN", self._mt5.ORDER_FILLING_RETURN),
        )
        if configured in {"FOK", "IOC", "RETURN"}:
            preferred = next((item for item in known_modes if item[0] == configured), None)
            remaining = tuple(item for item in known_modes if item[0] != configured)
            return tuple(item for item in (preferred, *remaining) if item is not None)

        candidates: list[tuple[str, int]] = []
        raw_filling = getattr(symbol_info, "filling_mode", None)
        if isinstance(raw_filling, int):
            for label, mode in known_modes:
                if raw_filling == mode:
                    candidates.append((f"AUTO:{label}", mode))
                elif raw_filling & mode:
                    candidates.append((f"AUTO:{label}", mode))

        for label, mode in known_modes:
            if all(existing_mode != mode for _, existing_mode in candidates):
                candidates.append((label, mode))
        return tuple(candidates)

    def _is_check_success(self, retcode: int) -> bool:
        """Return True when MT5 order_check allows order_send to continue."""
        allowed = {
            0,
            int(getattr(self._mt5, "TRADE_RETCODE_DONE", 10009)),
            int(getattr(self._mt5, "TRADE_RETCODE_PLACED", 10008)),
            int(getattr(self._mt5, "TRADE_RETCODE_DONE_PARTIAL", 10010)),
        }
        return int(retcode) in allowed

    def _is_send_success(self, retcode: int) -> bool:
        """Return True when MT5 reports an accepted order send result."""
        allowed = {
            int(getattr(self._mt5, "TRADE_RETCODE_DONE", 10009)),
            int(getattr(self._mt5, "TRADE_RETCODE_PLACED", 10008)),
            int(getattr(self._mt5, "TRADE_RETCODE_DONE_PARTIAL", 10010)),
        }
        return int(retcode) in allowed

    @staticmethod
    def _manual_order_result(
        accepted: bool,
        request: ManualTradeOrderRequest,
        requested_price: float | None,
        filled_price: float | None,
        retcode: int | None,
        order_ticket: int | None,
        deal_ticket: int | None,
        message: str,
    ) -> ManualTradeOrderResult:
        """Build an immutable manual order result."""
        return ManualTradeOrderResult(
            accepted=accepted,
            symbol=request.symbol,
            direction=request.direction,
            volume=float(request.volume),
            requested_price=requested_price,
            filled_price=filled_price,
            stop_loss=float(request.stop_loss),
            take_profit=float(request.take_profit),
            retcode=retcode,
            order_ticket=order_ticket,
            deal_ticket=deal_ticket,
            comment=request.comment,
            message=message,
            sent_at=datetime.now(timezone.utc),
        )

    def _initialize_terminal(self, mt5_module: Any) -> bool:
        """Initialize MT5 using configured terminal path when provided."""
        if self._config.terminal_path:
            return bool(mt5_module.initialize(path=self._config.terminal_path))
        return bool(mt5_module.initialize())

    def _load_mt5_module(self) -> Any | None:
        """Import MetaTrader5 lazily so non-MT5 validation can still compile."""
        try:
            import MetaTrader5 as mt5_module
        except ImportError as error:
            self._last_import_error = (
                "MetaTrader5 Python package could not be imported. "
                "Verify package installation and NumPy 1.x compatibility. "
                f"Import error: {error}"
            )
            self._logger.exception("MetaTrader5 package import failed.")
            return None
        self._last_import_error = None
        return mt5_module

    def _read_status(self, message: str) -> Mt5ConnectionStatus:
        """Read MT5 terminal/account state into a safe connection status object."""
        terminal = self._mt5.terminal_info() if self._mt5 is not None else None
        account = self._mt5.account_info() if self._mt5 is not None else None
        return Mt5ConnectionStatus(
            connected=True,
            message=message,
            terminal_name=str(terminal.name) if terminal is not None else None,
            company=str(account.company) if account is not None else None,
            server=str(account.server) if account is not None else None,
            login=int(account.login) if account is not None else None,
        )

    def _set_status(self, connected: bool, message: str) -> Mt5ConnectionStatus:
        """Persist and return the latest connection status."""
        self._connected = connected
        self._last_status = Mt5ConnectionStatus(connected=connected, message=message)
        return self._last_status

    def _require_connection(self) -> None:
        """Raise a service error when MT5 has not been connected successfully."""
        if not self._connected or self._mt5 is None:
            raise Mt5NotConnectedError(self._last_status.message)

    def _resolve_bar_count(self, bar_count: int | None) -> int:
        """Validate and return the requested number of OHLC bars."""
        requested_count = int(bar_count or self._config.default_bar_count)
        if requested_count < 1:
            raise ValueError("MT5 bar count must be greater than zero.")
        if requested_count > self._config.max_bars_per_request:
            raise ValueError(f"MT5 bar count exceeds max_bars_per_request: {self._config.max_bars_per_request}")
        return requested_count

    @staticmethod
    def _empty_ohlc_frame() -> pd.DataFrame:
        """Return an empty OHLC DataFrame with the expected production schema."""
        return pd.DataFrame(
            columns=["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"]
        )
