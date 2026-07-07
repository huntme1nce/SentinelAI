"""
MODULE: ANL-006
FILE: ANL-006-001
Module Name: Confidence Engine
Version: 1.1.0
Purpose: Scores agreement between structure, S/R, liquidity, imbalance, and momentum as read-only context without producing BUY/SELL entries.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models
Change History:
- 1.1.0: Added context-only confidence scoring foundation for Sprint 11.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import ConfidenceConfig
from sentinel_ai.models.confidence import ConfidenceContribution, ConfidenceSnapshot
from sentinel_ai.models.imbalance import ImbalanceSnapshot
from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.momentum import MomentumSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot


class ConfidenceEngine:
    """Compute a conservative context-confidence score without generating trade entries."""

    def __init__(self, config: ConfidenceConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: ConfidenceSnapshot | None = None

    @property
    def latest_snapshot(self) -> ConfidenceSnapshot | None:
        """Return the latest confidence snapshot."""
        return self._latest_snapshot

    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        structure_snapshot: MarketStructureSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
        momentum_snapshot: MomentumSnapshot | None,
    ) -> ConfidenceSnapshot:
        """Score current analysis context without producing BUY/SELL predictions."""
        if not self._config.enabled:
            snapshot = self._build_disabled_snapshot(market_snapshot)
            self._latest_snapshot = snapshot
            return snapshot

        contributions = (
            self._score_structure(structure_snapshot),
            self._score_support_resistance(support_resistance_snapshot),
            self._score_liquidity(liquidity_snapshot),
            self._score_imbalance(imbalance_snapshot),
            self._score_momentum(momentum_snapshot),
        )
        max_score = sum(item.max_score for item in contributions)
        raw_score = sum(item.score for item in contributions)
        score_percentage = 0.0 if max_score <= 0 else max(0.0, min(100.0, (raw_score / max_score) * 100.0))
        bias = self._resolve_bias(structure_snapshot, momentum_snapshot)
        readiness = self._resolve_readiness(score_percentage)
        reason = self._build_reason(bias, score_percentage, readiness, contributions)
        snapshot = ConfidenceSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction="WAIT",
            bias=bias,
            score_percentage=score_percentage,
            readiness=readiness,
            contributions=contributions,
            generated_at=datetime.now(timezone.utc),
            summary=f"Confidence {score_percentage:.2f}% | {bias} | {readiness}",
            reason=reason,
        )
        self._latest_snapshot = snapshot
        self._logger.debug("Confidence analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, snapshot.summary)
        return snapshot

    def _score_structure(self, snapshot: MarketStructureSnapshot) -> ConfidenceContribution:
        weight = float(self._config.structure_weight)
        if snapshot.bias in {"BULLISH", "BEARISH"}:
            return ConfidenceContribution("STRUCTURE", weight, weight, snapshot.bias, f"Structure bias {snapshot.bias.lower()}")
        if snapshot.bias == "RANGING":
            return ConfidenceContribution("STRUCTURE", weight * 0.45, weight, "RANGING", "Structure ranging")
        return ConfidenceContribution("STRUCTURE", 0.0, weight, snapshot.bias, "Structure insufficient")

    def _score_support_resistance(self, snapshot: SupportResistanceSnapshot | None) -> ConfidenceContribution:
        weight = float(self._config.support_resistance_weight)
        if snapshot is None:
            return ConfidenceContribution("S/R", 0.0, weight, "NONE", "S/R unavailable")
        has_support = snapshot.nearest_support is not None
        has_resistance = snapshot.nearest_resistance is not None
        if has_support and has_resistance:
            return ConfidenceContribution("S/R", weight, weight, "BALANCED", "Nearest support and resistance mapped")
        if has_support or has_resistance:
            return ConfidenceContribution("S/R", weight * 0.55, weight, "PARTIAL", "One active S/R boundary mapped")
        return ConfidenceContribution("S/R", 0.0, weight, "NONE", "No active S/R boundary")

    def _score_liquidity(self, snapshot: LiquiditySnapshot | None) -> ConfidenceContribution:
        weight = float(self._config.liquidity_weight)
        if snapshot is None:
            return ConfidenceContribution("LIQUIDITY", 0.0, weight, "NONE", "Liquidity unavailable")
        has_sweep = snapshot.latest_bullish_sweep is not None or snapshot.latest_bearish_sweep is not None
        has_active_pool = bool(snapshot.active_pools)
        if has_sweep and has_active_pool:
            return ConfidenceContribution("LIQUIDITY", weight, weight, "ACTIVE", "Liquidity sweep and active pool present")
        if has_sweep or has_active_pool:
            return ConfidenceContribution("LIQUIDITY", weight * 0.60, weight, "PARTIAL", "Liquidity context present")
        return ConfidenceContribution("LIQUIDITY", 0.0, weight, "NONE", "No liquidity context")

    def _score_imbalance(self, snapshot: ImbalanceSnapshot | None) -> ConfidenceContribution:
        weight = float(self._config.imbalance_weight)
        if snapshot is None:
            return ConfidenceContribution("IMBALANCE", 0.0, weight, "NONE", "FVG/OB unavailable")
        active_fvg = any(not zone.filled for zone in snapshot.fair_value_gaps)
        active_ob = any(not zone.invalidated and not zone.mitigated for zone in snapshot.order_blocks)
        if active_fvg and active_ob:
            return ConfidenceContribution("IMBALANCE", weight, weight, "ACTIVE", "Active FVG and OB present")
        if active_fvg or active_ob:
            return ConfidenceContribution("IMBALANCE", weight * 0.65, weight, "PARTIAL", "Active FVG/OB context present")
        return ConfidenceContribution("IMBALANCE", 0.0, weight, "NONE", "No active FVG/OB")

    def _score_momentum(self, snapshot: MomentumSnapshot | None) -> ConfidenceContribution:
        weight = float(self._config.momentum_weight)
        if snapshot is None:
            return ConfidenceContribution("MOMENTUM", 0.0, weight, "NONE", "Momentum unavailable")
        if snapshot.bias in {"BULLISH", "BEARISH"}:
            component_score = weight * min(1.0, max(0.0, snapshot.confirmation_score / 4.0))
            return ConfidenceContribution("MOMENTUM", component_score, weight, snapshot.bias, f"Momentum {snapshot.bias.lower()}")
        if snapshot.bias in {"LEAN_BULLISH", "LEAN_BEARISH"}:
            return ConfidenceContribution("MOMENTUM", weight * 0.55, weight, snapshot.bias, f"Momentum {snapshot.bias.lower()}")
        return ConfidenceContribution("MOMENTUM", weight * 0.20, weight, snapshot.bias, "Momentum neutral")

    @staticmethod
    def _resolve_bias(structure_snapshot: MarketStructureSnapshot, momentum_snapshot: MomentumSnapshot | None) -> str:
        structure_bias = structure_snapshot.bias
        momentum_bias = momentum_snapshot.bias if momentum_snapshot is not None else "NEUTRAL"
        if structure_bias == "BULLISH" and momentum_bias in {"BULLISH", "LEAN_BULLISH"}:
            return "BULLISH_CONTEXT"
        if structure_bias == "BEARISH" and momentum_bias in {"BEARISH", "LEAN_BEARISH"}:
            return "BEARISH_CONTEXT"
        if structure_bias in {"BULLISH", "BEARISH"}:
            return f"{structure_bias}_STRUCTURE"
        if momentum_bias in {"BULLISH", "LEAN_BULLISH"}:
            return "LEAN_BULLISH_CONTEXT"
        if momentum_bias in {"BEARISH", "LEAN_BEARISH"}:
            return "LEAN_BEARISH_CONTEXT"
        return "NEUTRAL_CONTEXT"

    def _resolve_readiness(self, score_percentage: float) -> str:
        if score_percentage >= float(self._config.high_context_threshold):
            return "HIGH_CONTEXT"
        if score_percentage >= float(self._config.medium_context_threshold):
            return "MEDIUM_CONTEXT"
        return "LOW_CONTEXT"

    @staticmethod
    def _build_reason(
        bias: str,
        score_percentage: float,
        readiness: str,
        contributions: tuple[ConfidenceContribution, ...],
    ) -> str:
        strongest = sorted(contributions, key=lambda item: item.normalized_score, reverse=True)[:2]
        strongest_text = " + ".join(item.component for item in strongest if item.score > 0)
        if not strongest_text:
            strongest_text = "Context pending"
        return f"{bias} | Confidence {score_percentage:.0f}% | {readiness} | {strongest_text} | WAIT"

    @staticmethod
    def _build_disabled_snapshot(market_snapshot: MarketDataSnapshot) -> ConfidenceSnapshot:
        return ConfidenceSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction="WAIT",
            bias="DISABLED",
            score_percentage=0.0,
            readiness="DISABLED",
            contributions=(),
            generated_at=datetime.now(timezone.utc),
            summary="Confidence engine disabled by configuration.",
            reason="Confidence disabled | WAIT",
        )
