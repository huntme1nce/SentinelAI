"""
MODULE: ANL-008
FILE: ANL-008-001
Module Name: Risk Reward Engine
1.4.0
Purpose: Validates TP, SL, and risk/reward for setup states without placing manual or automatic trades.
Dependencies: datetime, logging, sentinel_ai.config.config_schema, sentinel_ai.models
Change History:
- 1.6.0: Preserved risk/reward analysis for position monitoring sprint.
- 1.3.0: Added TP/SL and risk/reward validation foundation for Sprint 13.
- 1.3.1: Added smart TP candidate selection across TP1/TP2/TP3 targets before rejecting risk/reward.
- 1.3.2: Added rejected-plan display support and stricter directional TP guard wording.
- 1.5.0: Preserved risk/reward analysis for Sprint 15 manual execution.
- 1.4.1: Preserved risk/reward analysis for polished manual review-modal patch.
- 1.4.0: Preserved risk reward engine output for trade plan overlay and manual review gate sprint.
- 1.3.3: Added extended TP target discovery from range extremes, imbalance edges, and ATR projection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sentinel_ai.config.config_schema import RiskRewardConfig
from sentinel_ai.models.entry_validation import EntryValidationSnapshot, EntryZone
from sentinel_ai.models.imbalance import ImbalanceSnapshot
from sentinel_ai.models.liquidity import LiquidityPool, LiquiditySnapshot
from sentinel_ai.models.market import MarketBar, MarketDataSnapshot
from sentinel_ai.models.risk_reward import RiskRewardPlan, RiskRewardSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot, SupportResistanceZone


class RiskRewardEngine:
    """Validate TP/SL and risk/reward without generating executable trade orders."""

    def __init__(self, config: RiskRewardConfig, logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._latest_snapshot: RiskRewardSnapshot | None = None

    @property
    def latest_snapshot(self) -> RiskRewardSnapshot | None:
        """Return the latest risk/reward validation snapshot."""
        return self._latest_snapshot

    def analyze(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_snapshot: EntryValidationSnapshot | None,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> RiskRewardSnapshot:
        """Validate whether a setup has usable entry, SL, TP, and risk/reward."""
        latest_candle = market_snapshot.latest_candle
        confidence = 0.0 if entry_snapshot is None else float(entry_snapshot.confidence_percentage)
        if latest_candle is None:
            snapshot = self._wait_snapshot(market_snapshot, confidence, "No latest candle available for TP/SL validation.")
            self._latest_snapshot = snapshot
            return snapshot
        if not self._config.enabled:
            snapshot = self._wait_snapshot(market_snapshot, confidence, "Risk Reward Engine disabled.")
            self._latest_snapshot = snapshot
            return snapshot
        if entry_snapshot is None or entry_snapshot.direction not in {"BUY_SETUP", "SELL_SETUP"}:
            reason = "No setup available for TP/SL validation." if entry_snapshot is None else entry_snapshot.reason
            snapshot = self._wait_snapshot(market_snapshot, confidence, reason)
            self._latest_snapshot = snapshot
            return snapshot
        if entry_snapshot.entry_zone is None or not entry_snapshot.entry_zone.valid:
            snapshot = self._wait_snapshot(market_snapshot, confidence, "Setup has no valid entry zone for SL placement.")
            self._latest_snapshot = snapshot
            return snapshot

        entry_price = float(latest_candle.close)
        buffer_price = self._resolve_buffer_price(market_snapshot)
        if entry_snapshot.direction == "BUY_SETUP":
            plan = self._build_buy_plan(
                market_snapshot=market_snapshot,
                entry_price=entry_price,
                entry_zone=entry_snapshot.entry_zone,
                buffer_price=buffer_price,
                support_resistance_snapshot=support_resistance_snapshot,
                liquidity_snapshot=liquidity_snapshot,
                imbalance_snapshot=imbalance_snapshot,
            )
        else:
            plan = self._build_sell_plan(
                market_snapshot=market_snapshot,
                entry_price=entry_price,
                entry_zone=entry_snapshot.entry_zone,
                buffer_price=buffer_price,
                support_resistance_snapshot=support_resistance_snapshot,
                liquidity_snapshot=liquidity_snapshot,
                imbalance_snapshot=imbalance_snapshot,
            )

        if not plan.valid:
            snapshot = self._wait_snapshot(market_snapshot, confidence, plan.rejection_reason, plan)
            self._latest_snapshot = snapshot
            return snapshot

        ready_direction = "BUY_READY" if entry_snapshot.direction == "BUY_SETUP" else "SELL_READY"
        reason = (
            f"{ready_direction} | Confidence {confidence:.0f}% | "
            f"Entry {plan.entry_price:.2f} | SL {plan.stop_loss:.2f} | TP {plan.take_profit:.2f} | "
            f"RR {plan.risk_reward_ratio:.2f} | Ready for manual review"
        )
        snapshot = RiskRewardSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction=ready_direction,
            confidence_percentage=confidence,
            plan=plan,
            generated_at=datetime.now(timezone.utc),
            summary=f"{ready_direction} | RR {plan.risk_reward_ratio:.2f} | confidence {confidence:.2f}%",
            reason=reason,
        )
        self._latest_snapshot = snapshot
        self._logger.debug("Risk/reward analyzed for %s %s: %s", market_snapshot.symbol, market_snapshot.timeframe, snapshot.summary)
        return snapshot

    def _build_buy_plan(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_price: float,
        entry_zone: EntryZone,
        buffer_price: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> RiskRewardPlan:
        stop_loss = min(float(entry_zone.lower_price), self._nearest_support_floor(entry_price, support_resistance_snapshot)) - buffer_price
        take_profit, target_reason = self._select_buy_target(
            market_snapshot=market_snapshot,
            entry_price=entry_price,
            stop_loss=stop_loss,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        return self._build_plan(
            setup_direction="BUY_SETUP",
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            stop_reason=f"SL below {entry_zone.source} invalidation with buffer.",
            target_reason=target_reason,
        )

    def _build_sell_plan(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_price: float,
        entry_zone: EntryZone,
        buffer_price: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> RiskRewardPlan:
        stop_loss = max(float(entry_zone.upper_price), self._nearest_resistance_ceiling(entry_price, support_resistance_snapshot)) + buffer_price
        take_profit, target_reason = self._select_sell_target(
            market_snapshot=market_snapshot,
            entry_price=entry_price,
            stop_loss=stop_loss,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        return self._build_plan(
            setup_direction="SELL_SETUP",
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            stop_reason=f"SL above {entry_zone.source} invalidation with buffer.",
            target_reason=target_reason,
        )

    def _build_plan(
        self,
        setup_direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float | None,
        stop_reason: str,
        target_reason: str,
    ) -> RiskRewardPlan:
        if take_profit is None:
            return self._invalid_plan(setup_direction, entry_price, stop_loss, entry_price, stop_reason, "No valid TP target found.")
        risk_points = abs(entry_price - stop_loss)
        reward_points = 0.0
        if setup_direction == "BUY_SETUP":
            if stop_loss >= entry_price:
                return self._invalid_plan(setup_direction, entry_price, stop_loss, take_profit, stop_reason, "BUY setup SL is not below entry.")
            if take_profit <= entry_price:
                return self._invalid_plan(setup_direction, entry_price, stop_loss, take_profit, stop_reason, "BUY setup TP is not above entry.")
            reward_points = take_profit - entry_price
        elif setup_direction == "SELL_SETUP":
            if stop_loss <= entry_price:
                return self._invalid_plan(setup_direction, entry_price, stop_loss, take_profit, stop_reason, "SELL setup SL is not above entry.")
            if take_profit >= entry_price:
                return self._invalid_plan(setup_direction, entry_price, stop_loss, take_profit, stop_reason, "SELL setup TP is not below entry.")
            reward_points = entry_price - take_profit

        if risk_points < float(self._config.minimum_stop_distance_price):
            return self._invalid_plan(
                setup_direction,
                entry_price,
                stop_loss,
                take_profit,
                stop_reason,
                f"Stop distance {risk_points:.2f} below minimum {float(self._config.minimum_stop_distance_price):.2f}.",
            )
        if reward_points < float(self._config.minimum_target_distance_price):
            return self._invalid_plan(
                setup_direction,
                entry_price,
                stop_loss,
                take_profit,
                stop_reason,
                f"Target distance {reward_points:.2f} below minimum {float(self._config.minimum_target_distance_price):.2f}.",
            )

        ratio = reward_points / risk_points if risk_points > 0 else 0.0
        if ratio < float(self._config.minimum_risk_reward_ratio):
            return RiskRewardPlan(
                setup_direction=setup_direction,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_points=risk_points,
                reward_points=reward_points,
                risk_reward_ratio=ratio,
                stop_reason=stop_reason,
                target_reason=target_reason,
                valid=False,
                rejection_reason=self._risk_reward_rejection_reason(target_reason, ratio),
            )
        return RiskRewardPlan(
            setup_direction=setup_direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_points=risk_points,
            reward_points=reward_points,
            risk_reward_ratio=ratio,
            stop_reason=stop_reason,
            target_reason=target_reason,
            valid=True,
            rejection_reason="",
        )

    @staticmethod
    def _invalid_plan(
        setup_direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        stop_reason: str,
        rejection_reason: str,
    ) -> RiskRewardPlan:
        return RiskRewardPlan(
            setup_direction=setup_direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_points=abs(entry_price - stop_loss),
            reward_points=abs(take_profit - entry_price),
            risk_reward_ratio=0.0,
            stop_reason=stop_reason,
            target_reason="",
            valid=False,
            rejection_reason=rejection_reason,
        )

    def _select_buy_target(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_price: float,
        stop_loss: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> tuple[float | None, str]:
        candidates = self._buy_target_candidates(
            entry_price=entry_price,
            stop_loss=stop_loss,
            market_snapshot=market_snapshot,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        return self._select_target_from_candidates(
            setup_direction="BUY_SETUP",
            entry_price=entry_price,
            stop_loss=stop_loss,
            candidates=candidates,
            empty_reason="No valid BUY TP above entry meets RR target.",
        )

    def _select_sell_target(
        self,
        market_snapshot: MarketDataSnapshot,
        entry_price: float,
        stop_loss: float,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> tuple[float | None, str]:
        candidates = self._sell_target_candidates(
            entry_price=entry_price,
            stop_loss=stop_loss,
            market_snapshot=market_snapshot,
            support_resistance_snapshot=support_resistance_snapshot,
            liquidity_snapshot=liquidity_snapshot,
            imbalance_snapshot=imbalance_snapshot,
        )
        return self._select_target_from_candidates(
            setup_direction="SELL_SETUP",
            entry_price=entry_price,
            stop_loss=stop_loss,
            candidates=candidates,
            empty_reason="No valid SELL TP below entry meets RR target.",
        )

    def _buy_target_candidates(
        self,
        entry_price: float,
        stop_loss: float,
        market_snapshot: MarketDataSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> list[tuple[float, str]]:
        """Return ordered buy-side TP candidates above entry."""
        candidates: list[tuple[float, str]] = []
        if support_resistance_snapshot is not None:
            for zone in support_resistance_snapshot.resistance_zones:
                target = float(zone.lower_price)
                if target > entry_price:
                    candidates.append((target, f"resistance {zone.label}"))
        if liquidity_snapshot is not None:
            for pool in liquidity_snapshot.active_pools:
                if pool.is_buy_side and float(pool.price) > entry_price:
                    candidates.append((float(pool.price), f"buy-side liquidity {pool.label}"))
        candidates.extend(self._buy_imbalance_targets(entry_price, imbalance_snapshot))
        range_high = self._range_high_target(entry_price, market_snapshot)
        if range_high is not None:
            candidates.append((range_high, "current range high"))
        external_high = self._external_high_target(entry_price, market_snapshot)
        if external_high is not None:
            candidates.append((external_high, "external swing high"))
        atr_projection = self._atr_projected_target("BUY_SETUP", entry_price, stop_loss, market_snapshot)
        if atr_projection is not None:
            candidates.append((atr_projection, "ATR projected target"))
        return self._deduplicate_targets(candidates, reverse=False)

    def _sell_target_candidates(
        self,
        entry_price: float,
        stop_loss: float,
        market_snapshot: MarketDataSnapshot,
        support_resistance_snapshot: SupportResistanceSnapshot | None,
        liquidity_snapshot: LiquiditySnapshot | None,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> list[tuple[float, str]]:
        """Return ordered sell-side TP candidates below entry."""
        candidates: list[tuple[float, str]] = []
        if support_resistance_snapshot is not None:
            for zone in support_resistance_snapshot.support_zones:
                target = float(zone.upper_price)
                if target < entry_price:
                    candidates.append((target, f"support {zone.label}"))
        if liquidity_snapshot is not None:
            for pool in liquidity_snapshot.active_pools:
                if pool.is_sell_side and float(pool.price) < entry_price:
                    candidates.append((float(pool.price), f"sell-side liquidity {pool.label}"))
        candidates.extend(self._sell_imbalance_targets(entry_price, imbalance_snapshot))
        range_low = self._range_low_target(entry_price, market_snapshot)
        if range_low is not None:
            candidates.append((range_low, "current range low"))
        external_low = self._external_low_target(entry_price, market_snapshot)
        if external_low is not None:
            candidates.append((external_low, "external swing low"))
        atr_projection = self._atr_projected_target("SELL_SETUP", entry_price, stop_loss, market_snapshot)
        if atr_projection is not None:
            candidates.append((atr_projection, "ATR projected target"))
        return self._deduplicate_targets(candidates, reverse=True)

    def _select_target_from_candidates(
        self,
        setup_direction: str,
        entry_price: float,
        stop_loss: float,
        candidates: list[tuple[float, str]],
        empty_reason: str,
    ) -> tuple[float | None, str]:
        """Select the first TP candidate that satisfies minimum RR, otherwise return the nearest rejected candidate."""
        guarded_candidates = self._directional_tp_guard(setup_direction, entry_price, candidates)
        if not guarded_candidates:
            return None, self._directional_empty_reason(setup_direction)
        risk_points = abs(entry_price - stop_loss)
        if risk_points <= 0:
            return guarded_candidates[0][0], "Invalid risk distance before TP selection."
        minimum_ratio = float(self._config.minimum_risk_reward_ratio)
        rejected_notes: list[str] = []
        for index, (target_price, target_source) in enumerate(guarded_candidates, start=1):
            reward_points = self._reward_points(setup_direction, entry_price, target_price)
            ratio = reward_points / risk_points if risk_points > 0 else 0.0
            if reward_points >= float(self._config.minimum_target_distance_price) and ratio >= minimum_ratio:
                return target_price, f"TP{index} selected at {target_source}; RR {ratio:.2f} meets minimum {minimum_ratio:.2f}."
            rejected_notes.append(f"TP{index} RR {ratio:.2f} rejected")
        return guarded_candidates[0][0], (
            f"{'; '.join(rejected_notes)}; "
            f"no valid {self._directional_label(setup_direction)} TP meets RR {minimum_ratio:.2f}."
        )

    @staticmethod
    def _buy_imbalance_targets(
        entry_price: float,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> list[tuple[float, str]]:
        """Return imbalance far-edge targets above a buy entry."""
        if imbalance_snapshot is None:
            return []
        candidates: list[tuple[float, str]] = []
        for zone in imbalance_snapshot.fair_value_gaps:
            if not zone.filled and float(zone.upper_price) > entry_price:
                candidates.append((float(zone.upper_price), f"FVG far edge {zone.label}"))
        for zone in imbalance_snapshot.order_blocks:
            if not zone.invalidated and float(zone.upper_price) > entry_price:
                candidates.append((float(zone.upper_price), f"OB far edge {zone.label}"))
        return candidates

    @staticmethod
    def _sell_imbalance_targets(
        entry_price: float,
        imbalance_snapshot: ImbalanceSnapshot | None,
    ) -> list[tuple[float, str]]:
        """Return imbalance far-edge targets below a sell entry."""
        if imbalance_snapshot is None:
            return []
        candidates: list[tuple[float, str]] = []
        for zone in imbalance_snapshot.fair_value_gaps:
            if not zone.filled and float(zone.lower_price) < entry_price:
                candidates.append((float(zone.lower_price), f"FVG far edge {zone.label}"))
        for zone in imbalance_snapshot.order_blocks:
            if not zone.invalidated and float(zone.lower_price) < entry_price:
                candidates.append((float(zone.lower_price), f"OB far edge {zone.label}"))
        return candidates

    @staticmethod
    def _range_high_target(entry_price: float, market_snapshot: MarketDataSnapshot) -> float | None:
        """Return the highest visible recent range target above entry."""
        recent_candles = market_snapshot.candles[-60:]
        highs = [float(candle.high) for candle in recent_candles if float(candle.high) > entry_price]
        if not highs:
            return None
        return max(highs)

    @staticmethod
    def _range_low_target(entry_price: float, market_snapshot: MarketDataSnapshot) -> float | None:
        """Return the lowest visible recent range target below entry."""
        recent_candles = market_snapshot.candles[-60:]
        lows = [float(candle.low) for candle in recent_candles if float(candle.low) < entry_price]
        if not lows:
            return None
        return min(lows)

    def _atr_projected_target(
        self,
        setup_direction: str,
        entry_price: float,
        stop_loss: float,
        market_snapshot: MarketDataSnapshot,
    ) -> float | None:
        """Return an ATR-projected TP only when it provides minimum risk/reward distance."""
        risk_points = abs(entry_price - stop_loss)
        if risk_points <= 0:
            return None
        projected_distance = max(
            risk_points * float(self._config.minimum_risk_reward_ratio),
            self._average_range(market_snapshot.candles[-int(self._config.atr_lookback_candles) :]) * 3.0,
        )
        if setup_direction == "BUY_SETUP":
            return entry_price + projected_distance
        if setup_direction == "SELL_SETUP":
            return entry_price - projected_distance
        return None

    @staticmethod
    def _directional_tp_guard(
        setup_direction: str,
        entry_price: float,
        candidates: list[tuple[float, str]],
    ) -> list[tuple[float, str]]:
        """Ignore already-passed or wrong-side TP candidates."""
        if setup_direction == "BUY_SETUP":
            return [(price, source) for price, source in candidates if price > entry_price]
        if setup_direction == "SELL_SETUP":
            return [(price, source) for price, source in candidates if price < entry_price]
        return []

    @staticmethod
    def _directional_label(setup_direction: str) -> str:
        """Return readable direction label for TP rejection messages."""
        return "BUY" if setup_direction == "BUY_SETUP" else "SELL"

    @staticmethod
    def _directional_empty_reason(setup_direction: str) -> str:
        """Return direction-specific empty target message."""
        if setup_direction == "BUY_SETUP":
            return "No valid BUY TP above entry meets RR target."
        if setup_direction == "SELL_SETUP":
            return "No valid SELL TP below entry meets RR target."
        return "No valid directional TP candidate."

    @staticmethod
    def _reward_points(setup_direction: str, entry_price: float, target_price: float) -> float:
        """Return directional reward points for a TP candidate."""
        if setup_direction == "BUY_SETUP":
            return target_price - entry_price
        if setup_direction == "SELL_SETUP":
            return entry_price - target_price
        return 0.0

    @staticmethod
    def _deduplicate_targets(candidates: list[tuple[float, str]], reverse: bool) -> list[tuple[float, str]]:
        """Deduplicate and order target candidates by executable distance from entry side."""
        deduplicated: dict[float, str] = {}
        for price, source in candidates:
            rounded_price = round(float(price), 5)
            if rounded_price not in deduplicated:
                deduplicated[rounded_price] = source
        return sorted(((price, source) for price, source in deduplicated.items()), key=lambda item: item[0], reverse=reverse)

    @staticmethod
    def _external_high_target(entry_price: float, market_snapshot: MarketDataSnapshot) -> float | None:
        """Return the highest recent swing high above entry as a fallback external buy target."""
        recent_candles = market_snapshot.candles[-120:]
        highs = [float(candle.high) for candle in recent_candles if float(candle.high) > entry_price]
        if not highs:
            return None
        return max(highs)

    @staticmethod
    def _external_low_target(entry_price: float, market_snapshot: MarketDataSnapshot) -> float | None:
        """Return the lowest recent swing low below entry as a fallback external sell target."""
        recent_candles = market_snapshot.candles[-120:]
        lows = [float(candle.low) for candle in recent_candles if float(candle.low) < entry_price]
        if not lows:
            return None
        return min(lows)

    def _risk_reward_rejection_reason(self, target_reason: str, ratio: float) -> str:
        """Return a TP-aware risk/reward rejection reason."""
        if "no valid BUY TP" in target_reason or "no valid SELL TP" in target_reason:
            return target_reason
        return f"Risk/reward {ratio:.2f} below minimum {float(self._config.minimum_risk_reward_ratio):.2f}."

    @staticmethod
    def _nearest_support_floor(entry_price: float, snapshot: SupportResistanceSnapshot | None) -> float:
        if snapshot is None or snapshot.nearest_support is None:
            return entry_price
        nearest = snapshot.nearest_support
        return float(nearest.lower_price) if nearest.upper_price <= entry_price else entry_price

    @staticmethod
    def _nearest_resistance_ceiling(entry_price: float, snapshot: SupportResistanceSnapshot | None) -> float:
        if snapshot is None or snapshot.nearest_resistance is None:
            return entry_price
        nearest = snapshot.nearest_resistance
        return float(nearest.upper_price) if nearest.lower_price >= entry_price else entry_price

    def _resolve_buffer_price(self, market_snapshot: MarketDataSnapshot) -> float:
        recent_candles = market_snapshot.candles[-int(self._config.atr_lookback_candles) :]
        average_range = self._average_range(recent_candles)
        return max(
            float(self._config.minimum_stop_buffer_price),
            average_range * float(self._config.stop_buffer_atr_multiplier),
        )

    @staticmethod
    def _average_range(candles: tuple[MarketBar, ...]) -> float:
        if not candles:
            return 0.0001
        ranges = [max(float(candle.high) - float(candle.low), 0.0001) for candle in candles]
        return sum(ranges) / len(ranges)

    @staticmethod
    def _wait_snapshot(
        market_snapshot: MarketDataSnapshot,
        confidence_percentage: float,
        reason: str,
        plan: RiskRewardPlan | None = None,
    ) -> RiskRewardSnapshot:
        return RiskRewardSnapshot(
            symbol=market_snapshot.symbol,
            timeframe=market_snapshot.timeframe,
            direction="WAIT",
            confidence_percentage=confidence_percentage,
            plan=plan,
            generated_at=datetime.now(timezone.utc),
            summary=f"WAIT | confidence {confidence_percentage:.2f}% | {reason}",
            reason=f"WAIT | Confidence {confidence_percentage:.0f}% | {reason}",
        )
