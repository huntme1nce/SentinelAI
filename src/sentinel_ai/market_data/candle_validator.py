"""
MODULE: MKT-001
FILE: MKT-001-001
Module Name: Candle Data Validator
Version: 0.3.0
Purpose: Validates normalized OHLCV candle data before it reaches chart or analysis services.
Dependencies: pandas
Change History:
- 0.3.0: Added production validation for MT5 OHLCV DataFrame output.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


class CandleDataValidationError(ValueError):
    """Raised when market candle data is malformed or unsafe to consume."""


class CandleDataValidator:
    """Validate normalized OHLCV candle data returned by market data gateways."""

    REQUIRED_COLUMNS: Sequence[str] = (
        "time",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "spread",
        "real_volume",
    )

    PRICE_COLUMNS: Sequence[str] = ("open", "high", "low", "close")
    INTEGER_COLUMNS: Sequence[str] = ("tick_volume", "spread", "real_volume")

    def validate(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        """Return a validated, time-ordered copy of normalized candle data."""
        if data_frame is None:
            raise CandleDataValidationError("Market data frame is missing.")
        if data_frame.empty:
            return self._empty_valid_frame()

        missing_columns = [column for column in self.REQUIRED_COLUMNS if column not in data_frame.columns]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise CandleDataValidationError(f"Market data is missing required columns: {missing}")

        normalized = data_frame.loc[:, self.REQUIRED_COLUMNS].copy()
        normalized["time"] = pd.to_datetime(normalized["time"], utc=True, errors="coerce")
        for column in self.PRICE_COLUMNS + self.INTEGER_COLUMNS:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

        if normalized.isna().any().any():
            raise CandleDataValidationError("Market data contains invalid or missing candle values.")

        self._validate_price_relationships(normalized)
        normalized = normalized.sort_values("time").drop_duplicates(subset="time", keep="last").reset_index(drop=True)
        return normalized

    def _validate_price_relationships(self, data_frame: pd.DataFrame) -> None:
        """Verify each candle has coherent OHLC price relationships."""
        invalid_high = (data_frame["high"] < data_frame[["open", "close", "low"]].max(axis=1)).any()
        invalid_low = (data_frame["low"] > data_frame[["open", "close", "high"]].min(axis=1)).any()
        if bool(invalid_high or invalid_low):
            raise CandleDataValidationError("Market data contains invalid OHLC price relationships.")

    def _empty_valid_frame(self) -> pd.DataFrame:
        """Return an empty candle DataFrame using the canonical schema."""
        return pd.DataFrame(columns=list(self.REQUIRED_COLUMNS))
