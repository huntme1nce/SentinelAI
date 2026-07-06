"""
MODULE: MT5-002
FILE: MT5-002-001
Module Name: MetaTrader 5 Service
Version: 0.3.0
Purpose: Provides isolated, read-only MT5 connection and market-data access for Sentinel AI.
Dependencies: datetime, logging, pandas, sentinel_ai.config, sentinel_ai.models.market, sentinel_ai.mt5
Change History:
- 0.2.0: Added connection status, account snapshot, symbol validation, and OHLC data fetching without trade execution.
- 0.3.0: Improved MT5 import diagnostics and preserved normalized candle output for market feed service.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from sentinel_ai.config.config_schema import Mt5Config
from sentinel_ai.models.market import Mt5AccountSnapshot, Mt5ConnectionStatus, SymbolValidationResult
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
