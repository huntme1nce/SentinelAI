"""
MODULE: MKT-004
FILE: MKT-004-001
Module Name: Market Refresh Service
Version: 0.5.1
Purpose: Runs a safe timed market-data refresh loop and emits validated snapshots to application consumers.
Dependencies: logging, PySide6.QtCore, sentinel_ai.market_data, sentinel_ai.models.market
Change History:
- 0.5.0: Added live market refresh service for periodic validated candle updates without trading logic.
- 0.5.1: Supported one-second configuration defaults without changing service boundaries.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, QTimer, Qt, Signal

from sentinel_ai.market_data.candle_validator import CandleDataValidationError
from sentinel_ai.market_data.market_data_feed import MarketDataFeedService
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.mt5.exceptions import Mt5ServiceError


class MarketRefreshService(QObject):
    """Refresh validated market-data snapshots on a controlled timer."""

    snapshot_refreshed = Signal(object)
    refresh_failed = Signal(str)
    refresh_status_changed = Signal(str)

    def __init__(self, market_data_feed_service: MarketDataFeedService, logger: logging.Logger) -> None:
        """Initialize the refresh service with explicit service dependencies."""
        super().__init__()
        self._market_data_feed_service = market_data_feed_service
        self._logger = logger
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self.refresh_once)
        self._symbol: str | None = None
        self._timeframe: str | None = None
        self._bar_count = 0
        self._interval_seconds = 0
        self._refresh_in_progress = False

    @property
    def is_running(self) -> bool:
        """Return True when the live refresh timer is active."""
        return self._timer.isActive()

    @property
    def active_timeframe(self) -> str | None:
        """Return the currently refreshed timeframe, when configured."""
        return self._timeframe

    def start(self, symbol: str, timeframe: str, bar_count: int, interval_seconds: int) -> None:
        """Start live market refresh for the requested symbol and timeframe."""
        clean_symbol = str(symbol).strip()
        clean_timeframe = str(timeframe).strip().upper()
        clean_bar_count = int(bar_count)
        clean_interval_seconds = int(interval_seconds)
        if not clean_symbol:
            raise ValueError("Market refresh requires a non-empty symbol.")
        if not clean_timeframe:
            raise ValueError("Market refresh requires a non-empty timeframe.")
        if clean_bar_count < 1:
            raise ValueError("Market refresh bar count must be greater than zero.")
        if clean_interval_seconds < 1:
            raise ValueError("Market refresh interval must be at least one second.")

        self.stop()
        self._symbol = clean_symbol
        self._timeframe = clean_timeframe
        self._bar_count = clean_bar_count
        self._interval_seconds = clean_interval_seconds
        self._timer.start(clean_interval_seconds * 1000)
        message = f"Live market refresh started for {clean_symbol} {clean_timeframe} every {clean_interval_seconds}s."
        self._logger.info(message)
        self.refresh_status_changed.emit(message)
        self.refresh_once()

    def stop(self) -> None:
        """Stop the live market refresh timer if it is active."""
        if self._timer.isActive():
            self._timer.stop()
            self._logger.info("Live market refresh stopped.")
            self.refresh_status_changed.emit("Live market refresh stopped.")

    def refresh_once(self) -> None:
        """Fetch one validated market snapshot and emit it to application consumers."""
        if self._refresh_in_progress:
            return
        if self._symbol is None or self._timeframe is None or self._bar_count < 1:
            return

        self._refresh_in_progress = True
        try:
            snapshot = self._market_data_feed_service.load_snapshot(
                symbol=self._symbol,
                timeframe=self._timeframe,
                bar_count=self._bar_count,
            )
            self.snapshot_refreshed.emit(snapshot)
            self._emit_success_status(snapshot)
        except (Mt5ServiceError, CandleDataValidationError, ValueError) as error:
            message = f"Live market refresh failed for {self._symbol} {self._timeframe}: {error}"
            self._logger.warning(message)
            self.refresh_failed.emit(message)
        finally:
            self._refresh_in_progress = False

    def _emit_success_status(self, snapshot: MarketDataSnapshot) -> None:
        """Emit a concise success status for the latest validated snapshot."""
        latest = snapshot.latest_candle
        if latest is None:
            message = f"Live market refresh updated {snapshot.symbol} {snapshot.timeframe}: no candles returned."
        else:
            message = (
                f"Live market refresh updated {snapshot.symbol} {snapshot.timeframe}: "
                f"{snapshot.candle_count} candles, latest close {latest.close:.2f}."
            )
        self.refresh_status_changed.emit(message)
