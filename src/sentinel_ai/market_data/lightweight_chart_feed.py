"""
MODULE: MKT-002
FILE: MKT-002-001
Module Name: Lightweight Chart Feed Adapter
Version: 0.4.0
Purpose: Converts validated internal candles into TradingView Lightweight Charts-compatible payloads.
Dependencies: datetime, sentinel_ai.models.market
Change History:
- 0.3.0: Added chart feed conversion layer for future embedded TradingView integration.
- 0.4.0: Confirmed JSON payload shape for embedded live chart rendering.
"""

from __future__ import annotations

from sentinel_ai.models.market import ChartCandle, MarketBar


class LightweightChartFeedAdapter:
    """Convert internal candle models into chart-ready candle payloads."""

    def from_market_bars(self, candles: tuple[MarketBar, ...]) -> tuple[ChartCandle, ...]:
        """Return candles with UNIX-second timestamps required by Lightweight Charts."""
        return tuple(
            ChartCandle(
                time=int(candle.time.timestamp()),
                open=float(candle.open),
                high=float(candle.high),
                low=float(candle.low),
                close=float(candle.close),
            )
            for candle in candles
        )

    def to_serializable_payload(self, candles: tuple[ChartCandle, ...]) -> list[dict[str, float | int]]:
        """Return a JSON-serializable chart candle payload."""
        return [
            {
                "time": candle.time,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
            }
            for candle in candles
        ]
