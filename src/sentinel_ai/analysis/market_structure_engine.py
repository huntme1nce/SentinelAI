"""
MODULE: ANL-001
FILE: ANL-001-001
Module Name: Market Structure Engine
Version: 0.9.2
Purpose: Detects confirmed swing highs, swing lows, structural bias, and persistent close-based BOS and COC events from validated candles.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models.market, sentinel_ai.models.market_structure
Change History:
- 0.7.0: Added read-only market structure engine foundation without prediction or trading execution.
- 0.9.0: Added historical BOS detection and summary visibility without changing prediction behavior.
- 0.9.1: Preserved historical BOS output while companion overlays changed to bounded segments.
- 0.9.2: Added change-of-character classification while preserving persistent event history for review.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import MarketStructureConfig
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot, StructureBreak, SwingPoint


class MarketStructureEngine:
    """Analyze validated candles for confirmed market structure without creating trade predictions."""

    def __init__(self, config: MarketStructureConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: MarketStructureSnapshot | None = None

    @property
    def latest_snapshot(self) -> MarketStructureSnapshot | None:
        return self._latest_snapshot

    def analyze(self, market_snapshot: MarketDataSnapshot) -> MarketStructureSnapshot:
        candles = self._select_analysis_candles(market_snapshot)
        if not self._config.enabled:
            structure_snapshot = self._build_disabled_snapshot(market_snapshot, len(candles))
            self._latest_snapshot = structure_snapshot
            return structure_snapshot

        swing_highs, swing_lows = self._detect_swing_points(candles)
        historical_breaks = self._detect_structure_breaks(candles, swing_highs, swing_lows)
        latest_break = historical_breaks[-1] if historical_breaks else None
        bias = self._determine_bias(swing_highs, swing_lows, latest_break)
        summary = self._build_summary(bias, swing_highs, swing_lows, latest_break, historical_breaks, len(candles))
        structure_snapshot = MarketStructureSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            bias=bias,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
            latest_break=latest_break,
            historical_breaks=historical_breaks,
            analyzed_candle_count=len(candles),
            generated_at=datetime.now(timezone.utc),
            summary=summary,
        )
        self._latest_snapshot = structure_snapshot
        self._logger.debug("Market structure analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, summary)
        return structure_snapshot

    def _select_analysis_candles(self, market_snapshot: MarketDataSnapshot) -> tuple[MarketBar, ...]:
        lookback = int(self._config.lookback_candles)
        return tuple(market_snapshot.candles[-lookback:])

    def _detect_swing_points(self, candles: tuple[MarketBar, ...]) -> tuple[tuple[SwingPoint, ...], tuple[SwingPoint, ...]]:
        window = int(self._config.swing_window)
        if len(candles) < window * 2 + 1:
            return (), ()

        swing_highs: list[SwingPoint] = []
        swing_lows: list[SwingPoint] = []
        for index in range(window, len(candles) - window):
            candle = candles[index]
            left_side = candles[index - window : index]
            right_side = candles[index + 1 : index + window + 1]
            surrounding = (*left_side, *right_side)
            if self._is_swing_high(candle, surrounding):
                candidate = SwingPoint(kind="HIGH", time=candle.time, price=candle.high, candle_index=index)
                if self._is_far_enough_from_previous(candidate, swing_highs):
                    swing_highs.append(candidate)
            if self._is_swing_low(candle, surrounding):
                candidate = SwingPoint(kind="LOW", time=candle.time, price=candle.low, candle_index=index)
                if self._is_far_enough_from_previous(candidate, swing_lows):
                    swing_lows.append(candidate)

        return tuple(swing_highs), tuple(swing_lows)

    @staticmethod
    def _is_swing_high(candle: MarketBar, surrounding: tuple[MarketBar, ...]) -> bool:
        return all(candle.high > other.high for other in surrounding)

    @staticmethod
    def _is_swing_low(candle: MarketBar, surrounding: tuple[MarketBar, ...]) -> bool:
        return all(candle.low < other.low for other in surrounding)

    def _is_far_enough_from_previous(self, candidate: SwingPoint, previous_swings: list[SwingPoint]) -> bool:
        minimum_distance = float(self._config.minimum_swing_distance_price)
        if minimum_distance <= 0 or not previous_swings:
            return True
        return abs(candidate.price - previous_swings[-1].price) >= minimum_distance

    @staticmethod
    def _detect_structure_breaks(
        candles: tuple[MarketBar, ...],
        swing_highs: tuple[SwingPoint, ...],
        swing_lows: tuple[SwingPoint, ...],
    ) -> tuple[StructureBreak, ...]:
        if not candles:
            return ()

        events: list[StructureBreak] = []
        broken_references: set[tuple[str, datetime, float]] = set()
        for candle in candles:
            high_reference = MarketStructureEngine._latest_prior_swing(swing_highs, candle.time)
            low_reference = MarketStructureEngine._latest_prior_swing(swing_lows, candle.time)
            if high_reference is not None and candle.close > high_reference.price:
                reference_key = ("BULLISH", high_reference.time, float(high_reference.price))
                if reference_key not in broken_references:
                    events.append(
                        StructureBreak(
                            direction="BULLISH",
                            reference_price=high_reference.price,
                            reference_time=high_reference.time,
                            broken_at=candle.time,
                            close_price=candle.close,
                            event_type=MarketStructureEngine._resolve_event_type(events, "BULLISH"),
                        )
                    )
                    broken_references.add(reference_key)
            if low_reference is not None and candle.close < low_reference.price:
                reference_key = ("BEARISH", low_reference.time, float(low_reference.price))
                if reference_key not in broken_references:
                    events.append(
                        StructureBreak(
                            direction="BEARISH",
                            reference_price=low_reference.price,
                            reference_time=low_reference.time,
                            broken_at=candle.time,
                            close_price=candle.close,
                            event_type=MarketStructureEngine._resolve_event_type(events, "BEARISH"),
                        )
                    )
                    broken_references.add(reference_key)
        return tuple(sorted(events, key=lambda item: item.broken_at))

    @staticmethod
    def _resolve_event_type(existing_events: list[StructureBreak], direction: str) -> str:
        if not existing_events:
            return "BOS"
        latest_same_direction = next((event for event in reversed(existing_events) if event.direction == direction), None)
        latest_opposite_direction = next((event for event in reversed(existing_events) if event.direction != direction), None)
        if latest_opposite_direction is None:
            return "BOS"
        if latest_same_direction is None:
            return "COC"
        return "COC" if latest_opposite_direction.broken_at > latest_same_direction.broken_at else "BOS"

    @staticmethod
    def _latest_prior_swing(swings: tuple[SwingPoint, ...], candle_time: datetime) -> SwingPoint | None:
        prior_swings = tuple(swing for swing in swings if swing.time < candle_time)
        if not prior_swings:
            return None
        return prior_swings[-1]

    @staticmethod
    def _determine_bias(
        swing_highs: tuple[SwingPoint, ...],
        swing_lows: tuple[SwingPoint, ...],
        latest_break: StructureBreak | None,
    ) -> str:
        if latest_break is not None:
            return latest_break.direction
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return "INSUFFICIENT_STRUCTURE"

        previous_high, latest_high = swing_highs[-2], swing_highs[-1]
        previous_low, latest_low = swing_lows[-2], swing_lows[-1]
        higher_high = latest_high.price > previous_high.price
        higher_low = latest_low.price > previous_low.price
        lower_high = latest_high.price < previous_high.price
        lower_low = latest_low.price < previous_low.price

        if higher_high and higher_low:
            return "BULLISH"
        if lower_high and lower_low:
            return "BEARISH"
        return "RANGING"

    @staticmethod
    def _build_summary(
        bias: str,
        swing_highs: tuple[SwingPoint, ...],
        swing_lows: tuple[SwingPoint, ...],
        latest_break: StructureBreak | None,
        historical_breaks: tuple[StructureBreak, ...],
        analyzed_candle_count: int,
    ) -> str:
        latest_high = swing_highs[-1].price if swing_highs else None
        latest_low = swing_lows[-1].price if swing_lows else None
        high_text = f"last swing high {latest_high:.2f}" if latest_high is not None else "no confirmed swing high"
        low_text = f"last swing low {latest_low:.2f}" if latest_low is not None else "no confirmed swing low"
        latest_break_text = "latest structure event unavailable"
        if latest_break is not None:
            level_word = "above" if latest_break.is_bullish else "below"
            event_name = "COC" if latest_break.is_change_of_character else "BOS"
            latest_break_text = f"latest {latest_break.direction.lower()} {event_name} {level_word} {latest_break.reference_price:.2f}"
        bullish_break = next((item for item in reversed(historical_breaks) if item.is_bullish and item.is_break_of_structure), None)
        bearish_break = next((item for item in reversed(historical_breaks) if item.is_bearish and item.is_break_of_structure), None)
        bullish_coc = next((item for item in reversed(historical_breaks) if item.is_bullish and item.is_change_of_character), None)
        bearish_coc = next((item for item in reversed(historical_breaks) if item.is_bearish and item.is_change_of_character), None)
        bullish_text = f"last bullish BOS {bullish_break.reference_price:.2f}" if bullish_break is not None else "no bullish BOS"
        bearish_text = f"last bearish BOS {bearish_break.reference_price:.2f}" if bearish_break is not None else "no bearish BOS"
        bullish_coc_text = f"last bullish COC {bullish_coc.reference_price:.2f}" if bullish_coc is not None else "no bullish COC"
        bearish_coc_text = f"last bearish COC {bearish_coc.reference_price:.2f}" if bearish_coc is not None else "no bearish COC"
        return (
            f"{bias}; {high_text}; {low_text}; {latest_break_text}; "
            f"{bullish_text}; {bearish_text}; {bullish_coc_text}; {bearish_coc_text}; analyzed {analyzed_candle_count} candles"
        )

    @staticmethod
    def _build_disabled_snapshot(market_snapshot: MarketDataSnapshot, analyzed_candle_count: int) -> MarketStructureSnapshot:
        return MarketStructureSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            bias="DISABLED",
            swing_highs=(),
            swing_lows=(),
            latest_break=None,
            historical_breaks=(),
            analyzed_candle_count=analyzed_candle_count,
            generated_at=datetime.now(timezone.utc),
            summary="Market structure engine disabled by configuration.",
        )
