"""
MODULE: ANL-004
FILE: ANL-004-001
Module Name: Imbalance Engine
Version: 0.9.2
Purpose: Detects fair value gap and order block zones from validated candles and market structure events.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models.imbalance, sentinel_ai.models.market, sentinel_ai.models.market_structure
Change History:
- 0.9.2: Added read-only fair value gap and order block detection with boxed overlay support.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import ImbalanceConfig
from sentinel_ai.models.imbalance import FairValueGapZone, ImbalanceSnapshot, OrderBlockZone
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot, StructureBreak


class ImbalanceEngine:
    """Analyze validated candles for fair value gaps and order blocks."""

    def __init__(self, config: ImbalanceConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: ImbalanceSnapshot | None = None

    @property
    def latest_snapshot(self) -> ImbalanceSnapshot | None:
        return self._latest_snapshot

    def analyze(self, market_snapshot: MarketDataSnapshot, structure_snapshot: MarketStructureSnapshot) -> ImbalanceSnapshot:
        candles = self._select_analysis_candles(market_snapshot)
        if not self._config.enabled:
            snapshot = self._build_disabled_snapshot(market_snapshot, len(candles))
            self._latest_snapshot = snapshot
            return snapshot

        fair_value_gaps = self._detect_fair_value_gaps(candles)
        order_blocks = self._detect_order_blocks(candles, structure_snapshot)
        latest_bullish_fvg = next((zone for zone in reversed(fair_value_gaps) if zone.is_bullish), None)
        latest_bearish_fvg = next((zone for zone in reversed(fair_value_gaps) if zone.is_bearish), None)
        latest_bullish_order_block = next((zone for zone in reversed(order_blocks) if zone.is_bullish), None)
        latest_bearish_order_block = next((zone for zone in reversed(order_blocks) if zone.is_bearish), None)
        summary = self._build_summary(fair_value_gaps, order_blocks)
        snapshot = ImbalanceSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            fair_value_gaps=fair_value_gaps,
            order_blocks=order_blocks,
            latest_bullish_fvg=latest_bullish_fvg,
            latest_bearish_fvg=latest_bearish_fvg,
            latest_bullish_order_block=latest_bullish_order_block,
            latest_bearish_order_block=latest_bearish_order_block,
            generated_at=datetime.now(timezone.utc),
            analyzed_candle_count=len(candles),
            summary=summary,
        )
        self._latest_snapshot = snapshot
        self._logger.debug("Imbalance analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, summary)
        return snapshot

    def _select_analysis_candles(self, market_snapshot: MarketDataSnapshot) -> tuple[MarketBar, ...]:
        lookback = int(self._config.lookback_candles)
        return tuple(market_snapshot.candles[-lookback:])

    def _detect_fair_value_gaps(self, candles: tuple[MarketBar, ...]) -> tuple[FairValueGapZone, ...]:
        if len(candles) < 3:
            return ()
        minimum_gap = float(self._config.minimum_gap_price)
        zones: list[FairValueGapZone] = []
        for index in range(2, len(candles)):
            left = candles[index - 2]
            middle = candles[index - 1]
            right = candles[index]
            del middle  # clear intent that the pattern is three-candle based even if only outer candles define the zone.

            if right.low > left.high and (right.low - left.high) >= minimum_gap:
                end_time, filled, partial = self._resolve_bullish_fvg_state(candles, index, left.high, right.low)
                zones.append(
                    FairValueGapZone(
                        direction="BULLISH",
                        lower_price=float(left.high),
                        upper_price=float(right.low),
                        created_at=right.time,
                        start_time=left.time,
                        end_time=end_time,
                        filled=filled,
                        partially_mitigated=partial,
                        source_candle_index=index,
                    )
                )
            if right.high < left.low and (left.low - right.high) >= minimum_gap:
                end_time, filled, partial = self._resolve_bearish_fvg_state(candles, index, right.high, left.low)
                zones.append(
                    FairValueGapZone(
                        direction="BEARISH",
                        lower_price=float(right.high),
                        upper_price=float(left.low),
                        created_at=right.time,
                        start_time=left.time,
                        end_time=end_time,
                        filled=filled,
                        partially_mitigated=partial,
                        source_candle_index=index,
                    )
                )
        zones.sort(key=lambda item: item.created_at)
        limited = zones[-int(self._config.max_chart_fvg_zones):]
        return tuple(limited)

    @staticmethod
    def _resolve_bullish_fvg_state(candles: tuple[MarketBar, ...], start_index: int, lower_price: float, upper_price: float) -> tuple[datetime, bool, bool]:
        end_time = candles[-1].time
        partially_mitigated = False
        filled = False
        for candle in candles[start_index + 1 :]:
            if candle.low <= upper_price:
                partially_mitigated = True
                end_time = candle.time
            if candle.low <= lower_price:
                filled = True
                end_time = candle.time
                break
        return end_time, filled, partially_mitigated and not filled

    @staticmethod
    def _resolve_bearish_fvg_state(candles: tuple[MarketBar, ...], start_index: int, lower_price: float, upper_price: float) -> tuple[datetime, bool, bool]:
        end_time = candles[-1].time
        partially_mitigated = False
        filled = False
        for candle in candles[start_index + 1 :]:
            if candle.high >= lower_price:
                partially_mitigated = True
                end_time = candle.time
            if candle.high >= upper_price:
                filled = True
                end_time = candle.time
                break
        return end_time, filled, partially_mitigated and not filled

    def _detect_order_blocks(self, candles: tuple[MarketBar, ...], structure_snapshot: MarketStructureSnapshot) -> tuple[OrderBlockZone, ...]:
        if len(candles) < 3 or not structure_snapshot.historical_breaks:
            return ()

        candle_lookup = {candle.time: index for index, candle in enumerate(candles)}
        zones: list[OrderBlockZone] = []
        for event in structure_snapshot.historical_breaks:
            break_index = candle_lookup.get(event.broken_at)
            if break_index is None:
                continue
            source_index = self._find_order_block_source_index(candles, break_index, event)
            if source_index is None:
                continue
            source_candle = candles[source_index]
            if event.is_bullish:
                lower_price = float(source_candle.low)
                upper_price = float(max(source_candle.open, source_candle.close))
                end_time, mitigated, invalidated = self._resolve_bullish_order_block_state(candles, source_index, lower_price, upper_price)
            else:
                lower_price = float(min(source_candle.open, source_candle.close))
                upper_price = float(source_candle.high)
                end_time, mitigated, invalidated = self._resolve_bearish_order_block_state(candles, source_index, lower_price, upper_price)
            zones.append(
                OrderBlockZone(
                    direction=event.direction,
                    lower_price=lower_price,
                    upper_price=upper_price,
                    created_at=event.broken_at,
                    start_time=source_candle.time,
                    end_time=end_time,
                    mitigated=mitigated,
                    invalidated=invalidated,
                    source_candle_index=source_index,
                    source_break_time=event.broken_at,
                )
            )
        zones.sort(key=lambda item: item.created_at)
        limited = zones[-int(self._config.max_chart_order_blocks):]
        return tuple(limited)

    def _find_order_block_source_index(self, candles: tuple[MarketBar, ...], break_index: int, event: StructureBreak) -> int | None:
        lookup = int(self._config.order_block_lookup_candles)
        start_index = max(0, break_index - lookup)
        for index in range(break_index - 1, start_index - 1, -1):
            candle = candles[index]
            is_bearish_candle = candle.close < candle.open
            is_bullish_candle = candle.close > candle.open
            if event.is_bullish and is_bearish_candle:
                return index
            if event.is_bearish and is_bullish_candle:
                return index
        return None

    @staticmethod
    def _resolve_bullish_order_block_state(candles: tuple[MarketBar, ...], source_index: int, lower_price: float, upper_price: float) -> tuple[datetime, bool, bool]:
        end_time = candles[-1].time
        mitigated = False
        invalidated = False
        for candle in candles[source_index + 1 :]:
            if candle.low <= upper_price:
                mitigated = True
                end_time = candle.time
            if candle.close < lower_price:
                invalidated = True
                end_time = candle.time
                break
        return end_time, mitigated, invalidated

    @staticmethod
    def _resolve_bearish_order_block_state(candles: tuple[MarketBar, ...], source_index: int, lower_price: float, upper_price: float) -> tuple[datetime, bool, bool]:
        end_time = candles[-1].time
        mitigated = False
        invalidated = False
        for candle in candles[source_index + 1 :]:
            if candle.high >= lower_price:
                mitigated = True
                end_time = candle.time
            if candle.close > upper_price:
                invalidated = True
                end_time = candle.time
                break
        return end_time, mitigated, invalidated

    @staticmethod
    def _build_summary(fair_value_gaps: tuple[FairValueGapZone, ...], order_blocks: tuple[OrderBlockZone, ...]) -> str:
        active_fvg = sum(1 for zone in fair_value_gaps if not zone.filled)
        active_order_blocks = sum(1 for zone in order_blocks if not zone.invalidated)
        total_mitigated_fvg = sum(1 for zone in fair_value_gaps if zone.partially_mitigated or zone.filled)
        total_mitigated_ob = sum(1 for zone in order_blocks if zone.mitigated)
        return (
            f"Imbalance: FVG {len(fair_value_gaps)} total, {active_fvg} active, {total_mitigated_fvg} mitigated; "
            f"OB {len(order_blocks)} total, {active_order_blocks} active, {total_mitigated_ob} mitigated"
        )

    @staticmethod
    def _build_disabled_snapshot(market_snapshot: MarketDataSnapshot, analyzed_candle_count: int) -> ImbalanceSnapshot:
        return ImbalanceSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            fair_value_gaps=(),
            order_blocks=(),
            latest_bullish_fvg=None,
            latest_bearish_fvg=None,
            latest_bullish_order_block=None,
            latest_bearish_order_block=None,
            generated_at=datetime.now(timezone.utc),
            analyzed_candle_count=analyzed_candle_count,
            summary="Imbalance engine disabled by configuration.",
        )
