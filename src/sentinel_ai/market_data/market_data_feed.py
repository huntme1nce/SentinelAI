"""
MODULE: MKT-003
FILE: MKT-003-001
Module Name: Market Data Feed Service
Version: 0.3.0
Purpose: Fetches, validates, normalizes, and snapshots market candles for chart and analysis consumers.
Dependencies: datetime, logging, pandas, sentinel_ai.market_data, sentinel_ai.models, sentinel_ai.services
Change History:
- 0.3.0: Added production market data feed foundation backed by replaceable gateway contract.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd

from sentinel_ai.market_data.candle_validator import CandleDataValidator
from sentinel_ai.market_data.lightweight_chart_feed import LightweightChartFeedAdapter
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.services.contracts import MarketDataServiceContract


class MarketDataFeedService:
    """Provide validated market-data snapshots without depending on GUI or trading execution."""

    def __init__(
        self,
        market_data_gateway: MarketDataServiceContract,
        validator: CandleDataValidator,
        chart_feed_adapter: LightweightChartFeedAdapter,
        logger: logging.Logger,
    ) -> None:
        """Initialize the feed service with explicit replaceable dependencies."""
        self._market_data_gateway = market_data_gateway
        self._validator = validator
        self._chart_feed_adapter = chart_feed_adapter
        self._logger = logger
        self._latest_snapshot: MarketDataSnapshot | None = None

    def load_snapshot(self, symbol: str, timeframe: str, bar_count: int) -> MarketDataSnapshot:
        """Fetch and return one validated market data snapshot."""
        raw_data = self._market_data_gateway.fetch_ohlc(symbol=symbol, timeframe=timeframe, bar_count=bar_count)
        validated_data = self._validator.validate(raw_data)
        market_bars = self._build_market_bars(validated_data)
        chart_candles = self._chart_feed_adapter.from_market_bars(market_bars)
        snapshot = MarketDataSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            candles=market_bars,
            chart_candles=chart_candles,
            source="MetaTrader5",
            loaded_at=datetime.now(timezone.utc),
        )
        self._latest_snapshot = snapshot
        self._logger.info(
            "Loaded %s validated candles for %s %s from %s.",
            snapshot.candle_count,
            snapshot.symbol,
            snapshot.timeframe,
            snapshot.source,
        )
        return snapshot

    def latest_snapshot(self) -> MarketDataSnapshot | None:
        """Return the latest validated snapshot loaded by this feed service."""
        return self._latest_snapshot

    def chart_payload(self) -> list[dict[str, float | int]]:
        """Return the latest snapshot as a JSON-serializable chart payload."""
        if self._latest_snapshot is None:
            return []
        return self._chart_feed_adapter.to_serializable_payload(self._latest_snapshot.chart_candles)

    def _build_market_bars(self, data_frame: pd.DataFrame) -> tuple[MarketBar, ...]:
        """Convert validated DataFrame rows into immutable MarketBar models."""
        candles: list[MarketBar] = []
        for row in data_frame.itertuples(index=False):
            candle_time = row.time.to_pydatetime()
            candles.append(
                MarketBar(
                    time=candle_time,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.close),
                    tick_volume=int(row.tick_volume),
                    spread=int(row.spread),
                    real_volume=int(row.real_volume),
                )
            )
        return tuple(candles)
