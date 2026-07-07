"""
MODULE: ANL-007
FILE: ANL-007-001
Module Name: Entry Validation Engine
Version: 1.2.3
Purpose: Validates whether current context forms a BUY_SETUP, SELL_SETUP, or WAIT state without creating trade orders, TP, or SL.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models
Change History:
- 1.2.0: Added setup-only entry validation foundation for Sprint 12.
- 1.2.1: Refined setup alignment and WAIT reasons for high-confidence structure-only contexts.
- 1.2.2: Added pullback-aware setup validation so counter-leaning momentum can be allowed inside valid entry zones.
- 1.2.3: Added neutral-momentum entry-zone allowance for bullish/bearish setup preparation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import EntryValidationConfig
from sentinel_ai.models.confidence import ConfidenceSnapshot
from sentinel_ai.models.entry_validation import EntryValidationSnapshot, EntryZone
from sentinel_ai.models.imbalance import FairValueGapZone, ImbalanceSnapshot, OrderBlockZone
from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.momentum import MomentumSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot, SupportResistanceZone


class EntryValidationEngine:
    """Validate setup-level entry context without generating executable BUY/SELL signals."""

    def __init__(self, config: EntryValidationConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: EntryValidationSnapshot | None = None

    @property
    def latest_snapshot(self) -> EntryValidationSnapshot | None:
        """Return the latest entry validation snapshot."""
        return self._latest_snapshot

    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
        momentum_snapshot: MomentumSnapshot | None,
        confidence_snapshot: ConfidenceSnapshot | None,
    ) -> EntryValidationSnapshot:
        """Return BUY_SETUP, SELL_SETUP, or WAIT without TP/SL or trade execution."""
        latest_candle = market_snapshot.latest_candle
        if latest_candle is None:
            snapshot = self._wait_snapshot(market_snapshot, 0.0, "No latest candle available.")
            self._latest_snapshot = snapshot
            return snapshot
        if not self._config.enabled:
            snapshot = self._wait_snapshot(market_snapshot, self._confidence_value(confidence_snapshot), "Entry Validation Engine disabled.")
            self._latest_snapshot = snapshot
            return snapshot

        confidence_value = self._confidence_value(confidence_snapshot)
        if confidence_value < float(self._config.minimum_setup_confidence):
            snapshot = self._wait_snapshot(
                market_snapshot,
                confidence_value,
                f"Confidence {confidence_value:.2f}% below setup threshold {float(self._config.minimum_setup_confidence):.2f}%.",
            )
            self._latest_snapshot = snapshot
            return snapshot

        context_direction = self._resolve_context_direction(structure_snapshot, momentum_snapshot, confidence_snapshot)
        if context_direction not in {"BUY_SETUP", "SELL_SETUP"}:
            reason = self._build_no_context_reason(structure_snapshot, momentum_snapshot, confidence_snapshot)
            snapshot = self._wait_snapshot(market_snapshot, confidence_value, reason)
            self._latest_snapshot = snapshot
            return snapshot

        tolerance = self._resolve_zone_tolerance(market_snapshot)
        latest_price = float(latest_candle.close)
        entry_zone = self._select_entry_zone(
            setup_direction=context_direction,
            latest_price=latest_price,
            tolerance=tolerance,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        nearest_zone = entry_zone or self._select_nearest_entry_zone(
            setup_direction=context_direction,
            latest_price=latest_price,
            tolerance=tolerance,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )

        if entry_zone is None:
            reason = self._build_no_zone_reason(context_direction, nearest_zone, tolerance)
            snapshot = self._wait_snapshot(market_snapshot, confidence_value, reason)
            self._latest_snapshot = snapshot
            return snapshot

        momentum_aligned = self._momentum_aligned(context_direction, momentum_snapshot)
        pullback_allowed = self._pullback_momentum_allowed(
            setup_direction=context_direction,
            momentum_snapshot=momentum_snapshot,
            entry_zone=entry_zone,
            confidence_snapshot=confidence_snapshot,
            structure_snapshot=structure_snapshot,
        )
        neutral_allowed = self._neutral_momentum_allowed(
            setup_direction=context_direction,
            momentum_snapshot=momentum_snapshot,
            entry_zone=entry_zone,
            confidence_snapshot=confidence_snapshot,
            structure_snapshot=structure_snapshot,
        )
        if self._config.require_momentum_alignment and not momentum_aligned and not pullback_allowed and not neutral_allowed:
            reason = self._build_momentum_misalignment_reason(context_direction, momentum_snapshot)
            snapshot = self._wait_snapshot(market_snapshot, confidence_value, reason)
            self._latest_snapshot = snapshot
            return snapshot

        readiness = "SETUP_READY"
        if pullback_allowed and not momentum_aligned:
            reason = self._build_pullback_setup_reason(context_direction, confidence_value, entry_zone)
        elif neutral_allowed and not momentum_aligned:
            reason = self._build_neutral_setup_reason(context_direction, confidence_value, entry_zone)
        else:
            reason = (
                f"{context_direction} | Confidence {confidence_value:.0f}% | "
                f"{entry_zone.source} entry zone valid | Waiting TP/SL validation"
            )
        snapshot = EntryValidationSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction=context_direction,
            confidence_percentage=confidence_value,
            readiness=readiness,
            entry_zone=entry_zone,
            generated_at=datetime.now(timezone.utc),
            summary=f"{context_direction} | {entry_zone.source} | confidence {confidence_value:.2f}%",
            reason=reason,
        )
        self._latest_snapshot = snapshot
        self._logger.debug("Entry validation analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, snapshot.summary)
        return snapshot

    @staticmethod
    def _confidence_value(confidence_snapshot: ConfidenceSnapshot | None) -> float:
        if confidence_snapshot is None:
            return 0.0
        return float(confidence_snapshot.score_percentage)

    @staticmethod
    def _resolve_context_direction(
        structure_snapshot: MarketStructureSnapshot,
        momentum_snapshot: MomentumSnapshot | None,
        confidence_snapshot: ConfidenceSnapshot | None,
    ) -> str:
        confidence_bias = confidence_snapshot.bias if confidence_snapshot is not None else ""
        momentum_bias = momentum_snapshot.bias if momentum_snapshot is not None else ""
        if confidence_bias in {"BULLISH_CONTEXT", "LEAN_BULLISH_CONTEXT", "BULLISH_STRUCTURE"}:
            return "BUY_SETUP"
        if confidence_bias in {"BEARISH_CONTEXT", "LEAN_BEARISH_CONTEXT", "BEARISH_STRUCTURE"}:
            return "SELL_SETUP"
        if structure_snapshot.bias == "BULLISH":
            return "BUY_SETUP"
        if structure_snapshot.bias == "BEARISH":
            return "SELL_SETUP"
        if momentum_bias in {"BULLISH", "LEAN_BULLISH"}:
            return "BUY_SETUP"
        if momentum_bias in {"BEARISH", "LEAN_BEARISH"}:
            return "SELL_SETUP"
        return "WAIT"

    @staticmethod
    def _momentum_aligned(setup_direction: str, momentum_snapshot: MomentumSnapshot | None) -> bool:
        if momentum_snapshot is None:
            return False
        if setup_direction == "BUY_SETUP":
            return momentum_snapshot.bias in {"BULLISH", "LEAN_BULLISH"}
        if setup_direction == "SELL_SETUP":
            return momentum_snapshot.bias in {"BEARISH", "LEAN_BEARISH"}
        return False

    @staticmethod
    def _pullback_momentum_allowed(
        setup_direction: str,
        momentum_snapshot: MomentumSnapshot | None,
        entry_zone: EntryZone,
        confidence_snapshot: ConfidenceSnapshot | None,
        structure_snapshot: MarketStructureSnapshot,
    ) -> bool:
        """Return True when counter-leaning momentum is acceptable as a pullback into a valid zone."""
        if momentum_snapshot is None or entry_zone is None or not entry_zone.valid:
            return False
        confidence_bias = confidence_snapshot.bias if confidence_snapshot is not None else ""
        momentum_bias = momentum_snapshot.bias
        bullish_context = confidence_bias in {"BULLISH_CONTEXT", "BULLISH_STRUCTURE", "LEAN_BULLISH_CONTEXT"} or structure_snapshot.bias == "BULLISH"
        bearish_context = confidence_bias in {"BEARISH_CONTEXT", "BEARISH_STRUCTURE", "LEAN_BEARISH_CONTEXT"} or structure_snapshot.bias == "BEARISH"
        if setup_direction == "BUY_SETUP":
            return bullish_context and momentum_bias == "LEAN_BEARISH" and entry_zone.source in {"S/R", "FVG", "OB", "LIQUIDITY_SWEEP"}
        if setup_direction == "SELL_SETUP":
            return bearish_context and momentum_bias == "LEAN_BULLISH" and entry_zone.source in {"S/R", "FVG", "OB", "LIQUIDITY_SWEEP"}
        return False

    @staticmethod
    def _neutral_momentum_allowed(
        setup_direction: str,
        momentum_snapshot: MomentumSnapshot | None,
        entry_zone: EntryZone,
        confidence_snapshot: ConfidenceSnapshot | None,
        structure_snapshot: MarketStructureSnapshot,
    ) -> bool:
        """Return True when neutral momentum is acceptable inside a valid entry zone."""
        if momentum_snapshot is None or entry_zone is None or not entry_zone.valid:
            return False
        if momentum_snapshot.bias != "NEUTRAL":
            return False
        confidence_bias = confidence_snapshot.bias if confidence_snapshot is not None else ""
        bullish_context = confidence_bias in {"BULLISH_CONTEXT", "BULLISH_STRUCTURE", "LEAN_BULLISH_CONTEXT"} or structure_snapshot.bias == "BULLISH"
        bearish_context = confidence_bias in {"BEARISH_CONTEXT", "BEARISH_STRUCTURE", "LEAN_BEARISH_CONTEXT"} or structure_snapshot.bias == "BEARISH"
        if setup_direction == "BUY_SETUP":
            return bullish_context and entry_zone.source in {"S/R", "FVG", "OB", "LIQUIDITY_SWEEP"}
        if setup_direction == "SELL_SETUP":
            return bearish_context and entry_zone.source in {"S/R", "FVG", "OB", "LIQUIDITY_SWEEP"}
        return False

    @staticmethod
    def _build_neutral_setup_reason(setup_direction: str, confidence_value: float, entry_zone: EntryZone) -> str:
        """Return a setup reason when neutral momentum is accepted inside a valid entry zone."""
        if setup_direction == "BUY_SETUP":
            return (
                f"BUY_SETUP | Confidence {confidence_value:.0f}% | "
                f"Bullish setup inside {entry_zone.source} with neutral momentum | Waiting TP/SL validation"
            )
        if setup_direction == "SELL_SETUP":
            return (
                f"SELL_SETUP | Confidence {confidence_value:.0f}% | "
                f"Bearish setup inside {entry_zone.source} with neutral momentum | Waiting TP/SL validation"
            )
        return f"WAIT | Confidence {confidence_value:.0f}% | Neutral setup context unavailable."

    @staticmethod
    def _build_pullback_setup_reason(setup_direction: str, confidence_value: float, entry_zone: EntryZone) -> str:
        """Return a setup reason when temporary counter-momentum is accepted as a pullback."""
        if setup_direction == "BUY_SETUP":
            return (
                f"BUY_SETUP | Confidence {confidence_value:.0f}% | "
                f"Bullish pullback into {entry_zone.source} | Waiting TP/SL validation"
            )
        if setup_direction == "SELL_SETUP":
            return (
                f"SELL_SETUP | Confidence {confidence_value:.0f}% | "
                f"Bearish pullback into {entry_zone.source} | Waiting TP/SL validation"
            )
        return f"WAIT | Confidence {confidence_value:.0f}% | Pullback context unavailable."

    @staticmethod
    def _build_no_context_reason(
        structure_snapshot: MarketStructureSnapshot,
        momentum_snapshot: MomentumSnapshot | None,
        confidence_snapshot: ConfidenceSnapshot | None,
    ) -> str:
        """Return a specific WAIT reason when no setup side can be selected."""
        confidence_bias = confidence_snapshot.bias if confidence_snapshot is not None else "NO_CONFIDENCE"
        momentum_bias = momentum_snapshot.bias if momentum_snapshot is not None else "NO_MOMENTUM"
        if structure_snapshot.bias == "RANGING":
            return f"Structure is ranging; waiting for bullish or bearish setup alignment. Momentum: {momentum_bias}."
        return f"No setup side selected. Structure: {structure_snapshot.bias}; confidence: {confidence_bias}; momentum: {momentum_bias}."

    @staticmethod
    def _build_momentum_misalignment_reason(setup_direction: str, momentum_snapshot: MomentumSnapshot | None) -> str:
        """Return a precise momentum-alignment WAIT reason."""
        momentum_bias = momentum_snapshot.bias if momentum_snapshot is not None else "NO_MOMENTUM"
        if setup_direction == "BUY_SETUP":
            return f"Bullish context present but momentum is not aligned. Momentum: {momentum_bias}."
        if setup_direction == "SELL_SETUP":
            return f"Bearish context present but momentum is not aligned. Momentum: {momentum_bias}."
        return f"Setup context present but momentum is not aligned. Momentum: {momentum_bias}."

    def _resolve_zone_tolerance(self, market_snapshot: MarketDataSnapshot) -> float:
        recent_candles = market_snapshot.candles[-int(self._config.atr_lookback_candles) :]
        average_range = self._average_range(recent_candles)
        return max(
            float(self._config.minimum_zone_tolerance_price),
            average_range * float(self._config.proximity_atr_multiplier),
        )

    @staticmethod
    def _average_range(candles: tuple[MarketBar, ...]) -> float:
        if not candles:
            return 0.0001
        ranges = [max(float(candle.high) - float(candle.low), 0.0001) for candle in candles]
        return sum(ranges) / len(ranges)

    def _select_entry_zone(
        self,
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> EntryZone | None:
        nearest_zone = self._select_nearest_entry_zone(
            setup_direction=setup_direction,
            latest_price=latest_price,
            tolerance=tolerance,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        if nearest_zone is None or not nearest_zone.valid:
            return None
        return nearest_zone

    def _select_nearest_entry_zone(
        self,
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> EntryZone | None:
        """Return nearest active entry zone even when price is outside valid proximity."""
        candidates: list[EntryZone] = []
        candidates.extend(self._support_resistance_candidates(setup_direction, latest_price, tolerance, support_resistance_snapshot))
        candidates.extend(self._imbalance_candidates(setup_direction, latest_price, tolerance, imbalance_snapshot))
        candidates.extend(self._liquidity_candidates(setup_direction, latest_price, tolerance, liquidity_snapshot))
        if not candidates:
            return None
        return sorted(candidates, key=lambda candidate: candidate.distance_from_price)[0]

    @staticmethod
    def _build_no_zone_reason(setup_direction: str, nearest_zone: EntryZone | None, tolerance: float) -> str:
        """Return a precise WAIT reason when setup context exists but entry zone is not valid."""
        readable_direction = "Bullish" if setup_direction == "BUY_SETUP" else "Bearish"
        if nearest_zone is None:
            return f"{readable_direction} context present but no active entry zone is available."
        return (
            f"{readable_direction} context present but price is not in valid entry zone. "
            f"Nearest {nearest_zone.source} distance {nearest_zone.distance_from_price:.2f}; tolerance {tolerance:.2f}."
        )

    def _support_resistance_candidates(
        self,
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        snapshot: SupportResistanceSnapshot | None,
    ) -> list[EntryZone]:
        if snapshot is None:
            return []
        zone = snapshot.nearest_support if setup_direction == "BUY_SETUP" else snapshot.nearest_resistance
        if zone is None:
            return []
        return [self._zone_from_support_resistance(setup_direction, latest_price, tolerance, zone)]

    @staticmethod
    def _zone_from_support_resistance(
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        zone: SupportResistanceZone,
    ) -> EntryZone:
        distance = EntryValidationEngine._distance_to_range(latest_price, zone.lower_price, zone.upper_price)
        valid = distance <= tolerance
        return EntryZone(
            source="S/R",
            direction=setup_direction,
            lower_price=zone.lower_price,
            upper_price=zone.upper_price,
            distance_from_price=distance,
            valid=valid,
            reason="Price is near support." if setup_direction == "BUY_SETUP" else "Price is near resistance.",
        )

    def _imbalance_candidates(
        self,
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        snapshot: ImbalanceSnapshot | None,
    ) -> list[EntryZone]:
        if snapshot is None:
            return []
        zones: list[FairValueGapZone | OrderBlockZone] = []
        if setup_direction == "BUY_SETUP":
            zones.extend(zone for zone in snapshot.fair_value_gaps if zone.is_bullish and not zone.filled)
            zones.extend(zone for zone in snapshot.order_blocks if zone.is_bullish and not zone.mitigated and not zone.invalidated)
        elif setup_direction == "SELL_SETUP":
            zones.extend(zone for zone in snapshot.fair_value_gaps if zone.is_bearish and not zone.filled)
            zones.extend(zone for zone in snapshot.order_blocks if zone.is_bearish and not zone.mitigated and not zone.invalidated)
        return [self._zone_from_imbalance(setup_direction, latest_price, tolerance, zone) for zone in zones[-4:]]

    @staticmethod
    def _zone_from_imbalance(
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        zone: FairValueGapZone | OrderBlockZone,
    ) -> EntryZone:
        distance = EntryValidationEngine._distance_to_range(latest_price, zone.lower_price, zone.upper_price)
        source = "FVG" if hasattr(zone, "filled") else "OB"
        return EntryZone(
            source=source,
            direction=setup_direction,
            lower_price=zone.lower_price,
            upper_price=zone.upper_price,
            distance_from_price=distance,
            valid=distance <= tolerance,
            reason=f"Price is near active {source}.",
        )

    def _liquidity_candidates(
        self,
        setup_direction: str,
        latest_price: float,
        tolerance: float,
        snapshot: LiquiditySnapshot | None,
    ) -> list[EntryZone]:
        if snapshot is None:
            return []
        sweep = snapshot.latest_bullish_sweep if setup_direction == "BUY_SETUP" else snapshot.latest_bearish_sweep
        if sweep is None:
            return []
        lower_price = min(float(sweep.reference_price), float(sweep.close_price))
        upper_price = max(float(sweep.reference_price), float(sweep.close_price))
        distance = self._distance_to_range(latest_price, lower_price, upper_price)
        return [
            EntryZone(
                source="LIQUIDITY_SWEEP",
                direction=setup_direction,
                lower_price=lower_price,
                upper_price=upper_price,
                distance_from_price=distance,
                valid=distance <= tolerance,
                reason="Price is near a confirmed liquidity sweep zone.",
            )
        ]

    @staticmethod
    def _distance_to_range(price: float, lower_price: float, upper_price: float) -> float:
        if lower_price <= price <= upper_price:
            return 0.0
        if price < lower_price:
            return lower_price - price
        return price - upper_price

    @staticmethod
    def _wait_snapshot(market_snapshot: MarketDataSnapshot, confidence_percentage: float, reason: str) -> EntryValidationSnapshot:
        return EntryValidationSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction="WAIT",
            confidence_percentage=confidence_percentage,
            readiness="WAITING",
            entry_zone=None,
            generated_at=datetime.now(timezone.utc),
            summary=f"WAIT | confidence {confidence_percentage:.2f}% | {reason}",
            reason=f"WAIT | Confidence {confidence_percentage:.0f}% | {reason}",
        )
