"""
MODULE: ANL-005
FILE: ANL-005-001
Module Name: Momentum Engine
Version: 1.0.0
Purpose: Computes EMA, MACD, stochastic, and candle-body momentum context without producing BUY/SELL predictions or trade execution.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models.market, sentinel_ai.models.momentum
Change History:
- 1.0.0: Added read-only momentum analysis foundation for Sprint 10.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import MomentumConfig
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.models.momentum import (
    CandleMomentumState,
    EmaMomentumState,
    MacdMomentumState,
    MomentumSnapshot,
    StochasticMomentumState,
)


class MomentumEngine:
    """Analyze validated candles for momentum context without generating trade predictions."""

    def __init__(self, config: MomentumConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: MomentumSnapshot | None = None

    @property
    def latest_snapshot(self) -> MomentumSnapshot | None:
        """Return the latest computed momentum snapshot."""
        return self._latest_snapshot

    def analyze(self, market_snapshot: MarketDataSnapshot) -> MomentumSnapshot:
        """Compute read-only momentum context from validated market candles."""
        candles = self._select_analysis_candles(market_snapshot)
        if not self._config.enabled:
            snapshot = self._build_disabled_snapshot(market_snapshot, len(candles))
            self._latest_snapshot = snapshot
            return snapshot

        minimum_required = self._minimum_required_candles()
        if len(candles) < minimum_required:
            snapshot = MomentumSnapshot(
                symbol=market_snapshot.symbol,
                timeframe=market_snapshot.timeframe,
                bias="INSUFFICIENT_DATA",
                ema=None,
                macd=None,
                stochastic=None,
                candle_momentum=None,
                generated_at=datetime.now(timezone.utc),
                analyzed_candle_count=len(candles),
                summary=f"Momentum: insufficient candles; required {minimum_required}, received {len(candles)}",
                confirmation_score=0,
            )
            self._latest_snapshot = snapshot
            return snapshot

        closes = [float(candle.close) for candle in candles]
        highs = [float(candle.high) for candle in candles]
        lows = [float(candle.low) for candle in candles]
        ema_state = self._analyze_ema(closes)
        macd_state = self._analyze_macd(closes)
        stochastic_state = self._analyze_stochastic(highs, lows, closes)
        candle_state = self._analyze_candle_momentum(candles)
        bias, score = self._resolve_composite_bias(ema_state, macd_state, stochastic_state, candle_state)
        summary = self._build_summary(bias, score, ema_state, macd_state, stochastic_state, candle_state)
        snapshot = MomentumSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            bias=bias,
            ema=ema_state,
            macd=macd_state,
            stochastic=stochastic_state,
            candle_momentum=candle_state,
            generated_at=datetime.now(timezone.utc),
            analyzed_candle_count=len(candles),
            summary=summary,
            confirmation_score=score,
        )
        self._latest_snapshot = snapshot
        self._logger.debug("Momentum analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, summary)
        return snapshot

    def _select_analysis_candles(self, market_snapshot: MarketDataSnapshot) -> tuple[MarketBar, ...]:
        lookback = int(self._config.lookback_candles)
        return tuple(market_snapshot.candles[-lookback:])

    def _minimum_required_candles(self) -> int:
        return max(
            int(self._config.ema_slow_period) + 3,
            int(self._config.macd_slow_period) + int(self._config.macd_signal_period) + 3,
            int(self._config.stochastic_k_period) + int(self._config.stochastic_d_period) + 3,
            int(self._config.candle_momentum_lookback) + 3,
        )

    def _analyze_ema(self, closes: list[float]) -> EmaMomentumState:
        fast_series = self._ema_series(closes, int(self._config.ema_fast_period))
        slow_series = self._ema_series(closes, int(self._config.ema_slow_period))
        fast_ema = fast_series[-1]
        slow_ema = slow_series[-1]
        previous_fast = fast_series[-2]
        spread = fast_ema - slow_ema
        slope = fast_ema - previous_fast
        if spread > 0 and slope > 0:
            bias = "BULLISH"
        elif spread < 0 and slope < 0:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
        return EmaMomentumState(
            fast_ema=fast_ema,
            slow_ema=slow_ema,
            spread=spread,
            slope=slope,
            bias=bias,
            summary=f"EMA {bias.lower()}: fast {fast_ema:.2f}, slow {slow_ema:.2f}, spread {spread:.2f}",
        )

    def _analyze_macd(self, closes: list[float]) -> MacdMomentumState:
        macd_fast = self._ema_series(closes, int(self._config.macd_fast_period))
        macd_slow = self._ema_series(closes, int(self._config.macd_slow_period))
        macd_line_series = [fast - slow for fast, slow in zip(macd_fast, macd_slow)]
        signal_series = self._ema_series(macd_line_series, int(self._config.macd_signal_period))
        histogram = macd_line_series[-1] - signal_series[-1]
        previous_histogram = macd_line_series[-2] - signal_series[-2]
        minimum_histogram = float(self._config.minimum_histogram_abs)
        if histogram > minimum_histogram and histogram >= previous_histogram:
            bias = "BULLISH"
        elif histogram < -minimum_histogram and histogram <= previous_histogram:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
        return MacdMomentumState(
            macd_line=macd_line_series[-1],
            signal_line=signal_series[-1],
            histogram=histogram,
            previous_histogram=previous_histogram,
            bias=bias,
            summary=f"MACD {bias.lower()}: histogram {histogram:.4f}",
        )

    def _analyze_stochastic(self, highs: list[float], lows: list[float], closes: list[float]) -> StochasticMomentumState:
        k_period = int(self._config.stochastic_k_period)
        d_period = int(self._config.stochastic_d_period)
        k_values: list[float] = []
        for index in range(k_period - 1, len(closes)):
            high_window = highs[index - k_period + 1 : index + 1]
            low_window = lows[index - k_period + 1 : index + 1]
            highest_high = max(high_window)
            lowest_low = min(low_window)
            denominator = highest_high - lowest_low
            percent_k = 50.0 if denominator == 0 else ((closes[index] - lowest_low) / denominator) * 100.0
            k_values.append(percent_k)

        percent_k = k_values[-1]
        percent_d = sum(k_values[-d_period:]) / min(len(k_values), d_period)
        if percent_k >= 80:
            zone = "OVERBOUGHT"
        elif percent_k <= 20:
            zone = "OVERSOLD"
        else:
            zone = "MID_RANGE"

        if percent_k > percent_d and zone != "OVERBOUGHT":
            bias = "BULLISH"
        elif percent_k < percent_d and zone != "OVERSOLD":
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return StochasticMomentumState(
            percent_k=percent_k,
            percent_d=percent_d,
            bias=bias,
            zone=zone,
            summary=f"Stochastic {bias.lower()}: K {percent_k:.2f}, D {percent_d:.2f}, {zone.lower()}",
        )

    def _analyze_candle_momentum(self, candles: tuple[MarketBar, ...]) -> CandleMomentumState:
        lookback = int(self._config.candle_momentum_lookback)
        recent_candles = candles[-lookback:]
        body_ratios: list[float] = []
        bullish_count = 0
        bearish_count = 0
        for candle in recent_candles:
            range_size = max(float(candle.high) - float(candle.low), 0.0001)
            body_size = abs(float(candle.close) - float(candle.open))
            body_ratios.append(body_size / range_size)
            if candle.close > candle.open:
                bullish_count += 1
            elif candle.close < candle.open:
                bearish_count += 1

        average_body_ratio = sum(body_ratios) / len(body_ratios)
        latest_body_ratio = body_ratios[-1]
        threshold = float(self._config.strong_body_ratio_threshold)
        if bullish_count > bearish_count and average_body_ratio >= threshold:
            bias = "BULLISH"
        elif bearish_count > bullish_count and average_body_ratio >= threshold:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        return CandleMomentumState(
            average_body_ratio=average_body_ratio,
            latest_body_ratio=latest_body_ratio,
            bullish_body_count=bullish_count,
            bearish_body_count=bearish_count,
            bias=bias,
            summary=(
                f"Candle momentum {bias.lower()}: avg body {average_body_ratio:.2f}, "
                f"bull {bullish_count}, bear {bearish_count}"
            ),
        )

    @staticmethod
    def _resolve_composite_bias(
        ema_state: EmaMomentumState,
        macd_state: MacdMomentumState,
        stochastic_state: StochasticMomentumState,
        candle_state: CandleMomentumState,
    ) -> tuple[str, int]:
        states = (ema_state.bias, macd_state.bias, stochastic_state.bias, candle_state.bias)
        bullish_score = sum(1 for state in states if state == "BULLISH")
        bearish_score = sum(1 for state in states if state == "BEARISH")
        if bullish_score >= 3 and bullish_score > bearish_score:
            return "BULLISH", bullish_score
        if bearish_score >= 3 and bearish_score > bullish_score:
            return "BEARISH", bearish_score
        if bullish_score > bearish_score:
            return "LEAN_BULLISH", bullish_score
        if bearish_score > bullish_score:
            return "LEAN_BEARISH", bearish_score
        return "NEUTRAL", max(bullish_score, bearish_score)

    @staticmethod
    def _build_summary(
        bias: str,
        score: int,
        ema_state: EmaMomentumState,
        macd_state: MacdMomentumState,
        stochastic_state: StochasticMomentumState,
        candle_state: CandleMomentumState,
    ) -> str:
        return (
            f"Momentum {bias}; score {score}/4; "
            f"{ema_state.summary}; {macd_state.summary}; "
            f"{stochastic_state.summary}; {candle_state.summary}"
        )

    @staticmethod
    def _ema_series(values: list[float], period: int) -> list[float]:
        if period <= 0:
            raise ValueError("EMA period must be greater than zero.")
        if not values:
            return []
        multiplier = 2.0 / (period + 1.0)
        ema_values = [float(values[0])]
        for value in values[1:]:
            ema_values.append((float(value) - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values

    @staticmethod
    def _build_disabled_snapshot(market_snapshot: MarketDataSnapshot, analyzed_candle_count: int) -> MomentumSnapshot:
        return MomentumSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            bias="DISABLED",
            ema=None,
            macd=None,
            stochastic=None,
            candle_momentum=None,
            generated_at=datetime.now(timezone.utc),
            analyzed_candle_count=analyzed_candle_count,
            summary="Momentum engine disabled by configuration.",
            confirmation_score=0,
        )
