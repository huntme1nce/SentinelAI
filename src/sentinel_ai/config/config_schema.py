"""
MODULE: CFG-001
FILE: CFG-001-001
Module Name: Configuration Schema
2.5.0
Purpose: Defines validated configuration models for Sentinel AI, including modular analysis-engine settings.
Dependencies: dataclasses, typing
Change History:
- 2.5.0: Added explicit Auto Trade lock configuration for stabilization baseline.
- 2.4.0: Preserved trading configuration for guarded auto-trade completion build.
- 2.3.0: Preserved configuration for completion build.
- 2.2.0: Preserved configuration for dashboard simplification and close settlement fix.
- 2.1.0: Preserved configuration for ledger maintenance tool build.
- 2.0.1: Preserved configuration for pending/backlog separation fix.
- 2.0.0: Preserved configuration for final stabilization build.
- 1.9.0.2: Preserved configuration for app helper binding hotfix.
- 1.9.0.1: Preserved configuration for MT5 resolver binding hotfix.
- 1.9.0: Preserved configuration for full stabilization audit.
- 1.8.4.1: Preserved configuration for startup binding hotfix.
- 1.8.4: Preserved configuration for lifecycle diagnostics sprint.
- 1.8.3: Preserved configuration for pending-close settlement sprint.
- 1.8.2: Preserved configuration for active-ticket close guard sprint.
- 1.8.1: Preserved configuration for trade result verification sprint.
- 1.8.0: Preserved configuration for ledger outcome persistence sprint.
- 1.7.5: Preserved configuration for persistent Sentinel trade ledger sprint.
- 1.7.4: Preserved configuration for persistent Sentinel-owned trade recovery sprint.
- 1.7.3: Preserved configuration for Sentinel-owned trade tracking sprint.
- 1.7.2: Preserved configuration for countdown removal and history fallback sprint.
- 1.7.1.3: Preserved configuration for live candle-cycle countdown hotfix.
- 1.7.1.2: Preserved configuration for countdown candle-open anchoring hotfix.
- 1.7.1.1: Preserved configuration for candle countdown timer hotfix.
- 1.7.1: Preserved configuration for countdown timer and active-header priority sprint.
- 1.7.0: Preserved configuration for closed-trade lifecycle tracking sprint.
- 1.6.2: Preserved configuration for missing SL/TP warning patch.
- 1.6.1.2: Preserved configuration for missing TP chart-scale hotfix.
- 1.6.1.1: Preserved configuration for startup lock initialization hotfix.
- 1.6.1: Preserved configuration for active-trade chart lock patch.
- 1.6.0: Preserved manual trading configuration while adding position monitoring integration.
- 0.1.0: Added application, trading, database, logging, and UI configuration models.
- 0.2.0: Added MT5 connection configuration for Sprint 2.
- 0.3.0: Added market data feed configuration for Sprint 3.
- 0.4.0: Preserved schema for Sprint 4 chart rendering without adding trading settings.
- 0.5.0: Added market-data live refresh configuration with timeframe-specific intervals.
- 0.5.1: Preserved validated refresh configuration while allowing one-second synchronization defaults.
- 0.6.0: Added symbol-management configuration for account-specific MT5 symbol resolution.
- 0.7.0: Added market structure engine configuration for Sprint 7 analysis foundation.
- 0.8.0: Added support/resistance engine configuration for Sprint 8 analysis foundation.
- 0.9.0: Added liquidity engine configuration for Sprint 9 analysis foundation.
- 0.9.1: Preserved schema while default configuration now reduces overlay noise and bounds chart segments.
- 1.0.0: Added Momentum Engine configuration for Sprint 10 analysis foundation.
- 1.1.1: Preserved confidence configuration for live refresh pipeline patch.
- 1.2.3: Preserved entry validation configuration for neutral-momentum setup patch.
- 1.4.1: Preserved configuration for polished manual review-modal patch.
- 1.5.1: Preserved manual trading configuration for adaptive filling-mode fallback patch.
- 1.5.0: Added manual MT5 order placement configuration for Sprint 15.
- 1.4.0: Preserved Risk Reward configuration for trade plan overlay and manual review gate sprint.
- 1.3.3: Preserved Risk Reward configuration for extended TP target discovery patch.
- 1.3.2: Preserved Risk Reward configuration for rejected-plan display and directional TP guard patch.
- 1.3.1: Preserved Risk Reward configuration for smart TP target selection patch.
- 1.3.0: Added Risk Reward Engine configuration for TP/SL and risk/reward validation.
- 1.2.2: Preserved entry validation configuration for pullback-aware setup patch.
- 1.2.1: Preserved entry validation configuration for setup alignment patch.
- 1.2.0: Added Entry Validation Engine configuration for setup-only validation.
- 1.1.0: Added Confidence Engine configuration for Sprint 11 context scoring foundation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApplicationConfig:
    """Represent application identity and runtime mode settings."""

    name: str
    version: str
    environment: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApplicationConfig":
        """Create an ApplicationConfig from a dictionary."""
        return cls(
            name=str(data["name"]),
            version=str(data["version"]),
            environment=str(data["environment"]),
        )


@dataclass(frozen=True)
class TradingConfig:
    """Represent conservative default trading control settings."""

    symbol: str
    default_timeframe: str
    auto_trade_enabled: bool
    one_trade_at_a_time: bool
    minimum_confidence: float
    default_risk_reward: float
    auto_trade_locked: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradingConfig":
        """Create a TradingConfig from a dictionary."""
        return cls(
            symbol=str(data["symbol"]),
            default_timeframe=str(data["default_timeframe"]),
            auto_trade_enabled=bool(data["auto_trade_enabled"]),
            one_trade_at_a_time=bool(data["one_trade_at_a_time"]),
            minimum_confidence=float(data["minimum_confidence"]),
            default_risk_reward=float(data["default_risk_reward"]),
            auto_trade_locked=bool(data.get("auto_trade_locked", True)),
        )


@dataclass(frozen=True)
class SymbolManagementConfig:
    """Represent broker/account-specific symbol management settings."""

    auto_resolve_enabled: bool
    preferred_aliases: tuple[str, ...]
    toolbar_max_symbols: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolManagementConfig":
        """Create a SymbolManagementConfig from a dictionary."""
        raw_aliases = data["preferred_aliases"]
        if not isinstance(raw_aliases, list):
            raise ValueError("symbol_management.preferred_aliases must be a JSON array.")
        aliases = tuple(str(alias).strip() for alias in raw_aliases if str(alias).strip())
        toolbar_max_symbols = int(data["toolbar_max_symbols"])
        if toolbar_max_symbols < 1:
            raise ValueError("symbol_management.toolbar_max_symbols must be greater than zero.")
        return cls(
            auto_resolve_enabled=bool(data["auto_resolve_enabled"]),
            preferred_aliases=aliases,
            toolbar_max_symbols=toolbar_max_symbols,
        )


@dataclass(frozen=True)
class Mt5Config:
    """Represent MetaTrader 5 connection and market-data settings."""

    startup_connect: bool
    terminal_path: str | None
    default_bar_count: int
    max_bars_per_request: int
    require_visible_symbol: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mt5Config":
        """Create an Mt5Config from a dictionary."""
        terminal_path = data.get("terminal_path")
        return cls(
            startup_connect=bool(data["startup_connect"]),
            terminal_path=str(terminal_path) if terminal_path else None,
            default_bar_count=int(data["default_bar_count"]),
            max_bars_per_request=int(data["max_bars_per_request"]),
            require_visible_symbol=bool(data["require_visible_symbol"]),
        )


@dataclass(frozen=True)
class MarketDataConfig:
    """Represent market data feed behavior settings."""

    startup_load: bool
    default_feed_bar_count: int
    max_chart_candles: int
    auto_refresh_enabled: bool
    refresh_intervals_seconds: dict[str, int]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketDataConfig":
        """Create a MarketDataConfig from a dictionary."""
        raw_intervals = data["refresh_intervals_seconds"]
        if not isinstance(raw_intervals, dict):
            raise ValueError("market_data.refresh_intervals_seconds must be a JSON object.")
        intervals = {str(key).upper(): int(value) for key, value in raw_intervals.items()}
        if not intervals:
            raise ValueError("market_data.refresh_intervals_seconds must define at least one timeframe interval.")
        for timeframe, interval_seconds in intervals.items():
            if not timeframe:
                raise ValueError("market_data.refresh_intervals_seconds contains an empty timeframe key.")
            if interval_seconds < 1:
                raise ValueError(f"Refresh interval for {timeframe} must be at least one second.")
        return cls(
            startup_load=bool(data["startup_load"]),
            default_feed_bar_count=int(data["default_feed_bar_count"]),
            max_chart_candles=int(data["max_chart_candles"]),
            auto_refresh_enabled=bool(data["auto_refresh_enabled"]),
            refresh_intervals_seconds=intervals,
        )

    def refresh_interval_for(self, timeframe: str) -> int:
        """Return the configured refresh interval for a timeframe."""
        normalized_timeframe = str(timeframe).strip().upper()
        if normalized_timeframe in self.refresh_intervals_seconds:
            return self.refresh_intervals_seconds[normalized_timeframe]
        return self.refresh_intervals_seconds.get("DEFAULT", 5)


@dataclass(frozen=True)
class MarketStructureConfig:
    """Represent market structure engine behavior settings."""

    enabled: bool
    lookback_candles: int
    swing_window: int
    minimum_swing_distance_price: float
    max_chart_markers: int
    max_bos_markers: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketStructureConfig":
        """Create a MarketStructureConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        swing_window = int(data["swing_window"])
        minimum_distance = float(data["minimum_swing_distance_price"])
        max_chart_markers = int(data["max_chart_markers"])
        max_bos_markers = int(data["max_bos_markers"])
        if lookback_candles < 20:
            raise ValueError("analysis.market_structure.lookback_candles must be at least 20.")
        if swing_window < 1:
            raise ValueError("analysis.market_structure.swing_window must be at least 1.")
        if lookback_candles <= swing_window * 2:
            raise ValueError("analysis.market_structure.lookback_candles must exceed twice the swing window.")
        if minimum_distance < 0:
            raise ValueError("analysis.market_structure.minimum_swing_distance_price cannot be negative.")
        if max_chart_markers < 1:
            raise ValueError("analysis.market_structure.max_chart_markers must be greater than zero.")
        if max_bos_markers < 1:
            raise ValueError("analysis.market_structure.max_bos_markers must be greater than zero.")
        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            swing_window=swing_window,
            minimum_swing_distance_price=minimum_distance,
            max_chart_markers=max_chart_markers,
            max_bos_markers=max_bos_markers,
        )


@dataclass(frozen=True)
class SupportResistanceConfig:
    """Represent support/resistance engine behavior settings."""

    enabled: bool
    lookback_candles: int
    atr_period: int
    zone_atr_multiplier: float
    minimum_zone_width_price: float
    min_touch_count: int
    max_chart_zones: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupportResistanceConfig":
        """Create a SupportResistanceConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        atr_period = int(data["atr_period"])
        zone_atr_multiplier = float(data["zone_atr_multiplier"])
        minimum_zone_width_price = float(data["minimum_zone_width_price"])
        min_touch_count = int(data["min_touch_count"])
        max_chart_zones = int(data["max_chart_zones"])
        if lookback_candles < 20:
            raise ValueError("analysis.support_resistance.lookback_candles must be at least 20.")
        if atr_period < 2:
            raise ValueError("analysis.support_resistance.atr_period must be at least 2.")
        if zone_atr_multiplier <= 0:
            raise ValueError("analysis.support_resistance.zone_atr_multiplier must be greater than zero.")
        if minimum_zone_width_price < 0:
            raise ValueError("analysis.support_resistance.minimum_zone_width_price cannot be negative.")
        if min_touch_count < 1:
            raise ValueError("analysis.support_resistance.min_touch_count must be at least 1.")
        if max_chart_zones < 1:
            raise ValueError("analysis.support_resistance.max_chart_zones must be greater than zero.")
        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            atr_period=atr_period,
            zone_atr_multiplier=zone_atr_multiplier,
            minimum_zone_width_price=minimum_zone_width_price,
            min_touch_count=min_touch_count,
            max_chart_zones=max_chart_zones,
        )


@dataclass(frozen=True)
class LiquidityConfig:
    """Represent liquidity engine behavior settings."""

    enabled: bool
    lookback_candles: int
    sweep_buffer_price: float
    max_chart_pools: int
    max_chart_sweeps: int
    inducement_distance_price: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LiquidityConfig":
        """Create a LiquidityConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        sweep_buffer_price = float(data["sweep_buffer_price"])
        max_chart_pools = int(data["max_chart_pools"])
        max_chart_sweeps = int(data["max_chart_sweeps"])
        inducement_distance_price = float(data["inducement_distance_price"])
        if lookback_candles < 20:
            raise ValueError("analysis.liquidity.lookback_candles must be at least 20.")
        if sweep_buffer_price < 0:
            raise ValueError("analysis.liquidity.sweep_buffer_price cannot be negative.")
        if max_chart_pools < 1:
            raise ValueError("analysis.liquidity.max_chart_pools must be greater than zero.")
        if max_chart_sweeps < 1:
            raise ValueError("analysis.liquidity.max_chart_sweeps must be greater than zero.")
        if inducement_distance_price < 0:
            raise ValueError("analysis.liquidity.inducement_distance_price cannot be negative.")
        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            sweep_buffer_price=sweep_buffer_price,
            max_chart_pools=max_chart_pools,
            max_chart_sweeps=max_chart_sweeps,
            inducement_distance_price=inducement_distance_price,
        )


@dataclass(frozen=True)
class ImbalanceConfig:
    """Represent fair value gap and order block engine behavior settings."""

    enabled: bool
    lookback_candles: int
    max_chart_fvg_zones: int
    max_chart_order_blocks: int
    minimum_gap_price: float
    order_block_lookup_candles: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImbalanceConfig":
        """Create an ImbalanceConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        max_chart_fvg_zones = int(data["max_chart_fvg_zones"])
        max_chart_order_blocks = int(data["max_chart_order_blocks"])
        minimum_gap_price = float(data["minimum_gap_price"])
        order_block_lookup_candles = int(data["order_block_lookup_candles"])
        if lookback_candles < 20:
            raise ValueError("analysis.imbalance.lookback_candles must be at least 20.")
        if max_chart_fvg_zones < 1:
            raise ValueError("analysis.imbalance.max_chart_fvg_zones must be greater than zero.")
        if max_chart_order_blocks < 1:
            raise ValueError("analysis.imbalance.max_chart_order_blocks must be greater than zero.")
        if minimum_gap_price < 0:
            raise ValueError("analysis.imbalance.minimum_gap_price cannot be negative.")
        if order_block_lookup_candles < 1:
            raise ValueError("analysis.imbalance.order_block_lookup_candles must be at least 1.")
        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            max_chart_fvg_zones=max_chart_fvg_zones,
            max_chart_order_blocks=max_chart_order_blocks,
            minimum_gap_price=minimum_gap_price,
            order_block_lookup_candles=order_block_lookup_candles,
        )



@dataclass(frozen=True)
class MomentumConfig:
    """Represent EMA, MACD, stochastic, and candle momentum engine behavior settings."""

    enabled: bool
    lookback_candles: int
    ema_fast_period: int
    ema_slow_period: int
    macd_fast_period: int
    macd_slow_period: int
    macd_signal_period: int
    stochastic_k_period: int
    stochastic_d_period: int
    candle_momentum_lookback: int
    strong_body_ratio_threshold: float
    minimum_histogram_abs: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MomentumConfig":
        """Create a MomentumConfig from a dictionary."""
        lookback_candles = int(data["lookback_candles"])
        ema_fast_period = int(data["ema_fast_period"])
        ema_slow_period = int(data["ema_slow_period"])
        macd_fast_period = int(data["macd_fast_period"])
        macd_slow_period = int(data["macd_slow_period"])
        macd_signal_period = int(data["macd_signal_period"])
        stochastic_k_period = int(data["stochastic_k_period"])
        stochastic_d_period = int(data["stochastic_d_period"])
        candle_momentum_lookback = int(data["candle_momentum_lookback"])
        strong_body_ratio_threshold = float(data["strong_body_ratio_threshold"])
        minimum_histogram_abs = float(data["minimum_histogram_abs"])

        if lookback_candles < 50:
            raise ValueError("analysis.momentum.lookback_candles must be at least 50.")
        if ema_fast_period < 2:
            raise ValueError("analysis.momentum.ema_fast_period must be at least 2.")
        if ema_slow_period <= ema_fast_period:
            raise ValueError("analysis.momentum.ema_slow_period must be greater than ema_fast_period.")
        if macd_fast_period < 2:
            raise ValueError("analysis.momentum.macd_fast_period must be at least 2.")
        if macd_slow_period <= macd_fast_period:
            raise ValueError("analysis.momentum.macd_slow_period must be greater than macd_fast_period.")
        if macd_signal_period < 2:
            raise ValueError("analysis.momentum.macd_signal_period must be at least 2.")
        if stochastic_k_period < 3:
            raise ValueError("analysis.momentum.stochastic_k_period must be at least 3.")
        if stochastic_d_period < 2:
            raise ValueError("analysis.momentum.stochastic_d_period must be at least 2.")
        if candle_momentum_lookback < 3:
            raise ValueError("analysis.momentum.candle_momentum_lookback must be at least 3.")
        if not 0 <= strong_body_ratio_threshold <= 1:
            raise ValueError("analysis.momentum.strong_body_ratio_threshold must be between 0 and 1.")
        if minimum_histogram_abs < 0:
            raise ValueError("analysis.momentum.minimum_histogram_abs cannot be negative.")

        return cls(
            enabled=bool(data["enabled"]),
            lookback_candles=lookback_candles,
            ema_fast_period=ema_fast_period,
            ema_slow_period=ema_slow_period,
            macd_fast_period=macd_fast_period,
            macd_slow_period=macd_slow_period,
            macd_signal_period=macd_signal_period,
            stochastic_k_period=stochastic_k_period,
            stochastic_d_period=stochastic_d_period,
            candle_momentum_lookback=candle_momentum_lookback,
            strong_body_ratio_threshold=strong_body_ratio_threshold,
            minimum_histogram_abs=minimum_histogram_abs,
        )



@dataclass(frozen=True)
class ConfidenceConfig:
    """Represent context-only confidence scoring settings."""

    enabled: bool
    structure_weight: float
    support_resistance_weight: float
    liquidity_weight: float
    imbalance_weight: float
    momentum_weight: float
    medium_context_threshold: float
    high_context_threshold: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfidenceConfig":
        """Create a ConfidenceConfig from a dictionary."""
        structure_weight = float(data["structure_weight"])
        support_resistance_weight = float(data["support_resistance_weight"])
        liquidity_weight = float(data["liquidity_weight"])
        imbalance_weight = float(data["imbalance_weight"])
        momentum_weight = float(data["momentum_weight"])
        medium_context_threshold = float(data["medium_context_threshold"])
        high_context_threshold = float(data["high_context_threshold"])
        weights = (
            structure_weight,
            support_resistance_weight,
            liquidity_weight,
            imbalance_weight,
            momentum_weight,
        )
        if any(weight < 0 for weight in weights):
            raise ValueError("analysis.confidence weights cannot be negative.")
        if sum(weights) <= 0:
            raise ValueError("analysis.confidence weights must have a positive total.")
        if not 0 <= medium_context_threshold <= 100:
            raise ValueError("analysis.confidence.medium_context_threshold must be between 0 and 100.")
        if not 0 <= high_context_threshold <= 100:
            raise ValueError("analysis.confidence.high_context_threshold must be between 0 and 100.")
        if high_context_threshold < medium_context_threshold:
            raise ValueError("analysis.confidence.high_context_threshold must be greater than or equal to medium threshold.")
        return cls(
            enabled=bool(data["enabled"]),
            structure_weight=structure_weight,
            support_resistance_weight=support_resistance_weight,
            liquidity_weight=liquidity_weight,
            imbalance_weight=imbalance_weight,
            momentum_weight=momentum_weight,
            medium_context_threshold=medium_context_threshold,
            high_context_threshold=high_context_threshold,
        )



@dataclass(frozen=True)
class EntryValidationConfig:
    """Represent setup-only entry validation behavior settings."""

    enabled: bool
    minimum_setup_confidence: float
    proximity_atr_multiplier: float
    minimum_zone_tolerance_price: float
    atr_lookback_candles: int
    require_momentum_alignment: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EntryValidationConfig":
        """Create an EntryValidationConfig from a dictionary."""
        minimum_setup_confidence = float(data["minimum_setup_confidence"])
        proximity_atr_multiplier = float(data["proximity_atr_multiplier"])
        minimum_zone_tolerance_price = float(data["minimum_zone_tolerance_price"])
        atr_lookback_candles = int(data["atr_lookback_candles"])
        if not 0 <= minimum_setup_confidence <= 100:
            raise ValueError("analysis.entry_validation.minimum_setup_confidence must be between 0 and 100.")
        if proximity_atr_multiplier <= 0:
            raise ValueError("analysis.entry_validation.proximity_atr_multiplier must be greater than zero.")
        if minimum_zone_tolerance_price < 0:
            raise ValueError("analysis.entry_validation.minimum_zone_tolerance_price cannot be negative.")
        if atr_lookback_candles < 3:
            raise ValueError("analysis.entry_validation.atr_lookback_candles must be at least 3.")
        return cls(
            enabled=bool(data["enabled"]),
            minimum_setup_confidence=minimum_setup_confidence,
            proximity_atr_multiplier=proximity_atr_multiplier,
            minimum_zone_tolerance_price=minimum_zone_tolerance_price,
            atr_lookback_candles=atr_lookback_candles,
            require_momentum_alignment=bool(data["require_momentum_alignment"]),
        )



@dataclass(frozen=True)
class RiskRewardConfig:
    """Represent TP/SL and risk/reward validation behavior settings."""

    enabled: bool
    minimum_risk_reward_ratio: float
    stop_buffer_atr_multiplier: float
    minimum_stop_buffer_price: float
    minimum_stop_distance_price: float
    minimum_target_distance_price: float
    atr_lookback_candles: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskRewardConfig":
        """Create a RiskRewardConfig from a dictionary."""
        minimum_risk_reward_ratio = float(data["minimum_risk_reward_ratio"])
        stop_buffer_atr_multiplier = float(data["stop_buffer_atr_multiplier"])
        minimum_stop_buffer_price = float(data["minimum_stop_buffer_price"])
        minimum_stop_distance_price = float(data["minimum_stop_distance_price"])
        minimum_target_distance_price = float(data["minimum_target_distance_price"])
        atr_lookback_candles = int(data["atr_lookback_candles"])
        if minimum_risk_reward_ratio <= 0:
            raise ValueError("analysis.risk_reward.minimum_risk_reward_ratio must be greater than zero.")
        if stop_buffer_atr_multiplier <= 0:
            raise ValueError("analysis.risk_reward.stop_buffer_atr_multiplier must be greater than zero.")
        if minimum_stop_buffer_price < 0:
            raise ValueError("analysis.risk_reward.minimum_stop_buffer_price cannot be negative.")
        if minimum_stop_distance_price <= 0:
            raise ValueError("analysis.risk_reward.minimum_stop_distance_price must be greater than zero.")
        if minimum_target_distance_price <= 0:
            raise ValueError("analysis.risk_reward.minimum_target_distance_price must be greater than zero.")
        if atr_lookback_candles < 3:
            raise ValueError("analysis.risk_reward.atr_lookback_candles must be at least 3.")
        return cls(
            enabled=bool(data["enabled"]),
            minimum_risk_reward_ratio=minimum_risk_reward_ratio,
            stop_buffer_atr_multiplier=stop_buffer_atr_multiplier,
            minimum_stop_buffer_price=minimum_stop_buffer_price,
            minimum_stop_distance_price=minimum_stop_distance_price,
            minimum_target_distance_price=minimum_target_distance_price,
            atr_lookback_candles=atr_lookback_candles,
        )



@dataclass(frozen=True)
class ManualTradingConfig:
    """Represent user-confirmed manual MT5 order placement settings."""

    enabled: bool
    default_volume: float
    max_volume: float
    deviation_points: int
    magic_number: int
    order_comment: str
    order_filling: str
    one_position_per_symbol: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManualTradingConfig":
        """Create a ManualTradingConfig from a dictionary."""
        default_volume = float(data["default_volume"])
        max_volume = float(data["max_volume"])
        deviation_points = int(data["deviation_points"])
        magic_number = int(data["magic_number"])
        order_filling = str(data["order_filling"]).strip().upper()
        if default_volume <= 0:
            raise ValueError("manual_trading.default_volume must be greater than zero.")
        if max_volume < default_volume:
            raise ValueError("manual_trading.max_volume must be greater than or equal to default_volume.")
        if deviation_points < 0:
            raise ValueError("manual_trading.deviation_points cannot be negative.")
        if magic_number < 0:
            raise ValueError("manual_trading.magic_number cannot be negative.")
        if order_filling not in {"AUTO", "FOK", "IOC", "RETURN"}:
            raise ValueError("manual_trading.order_filling must be AUTO, FOK, IOC, or RETURN.")
        return cls(
            enabled=bool(data["enabled"]),
            default_volume=default_volume,
            max_volume=max_volume,
            deviation_points=deviation_points,
            magic_number=magic_number,
            order_comment=str(data["order_comment"]),
            order_filling=order_filling,
            one_position_per_symbol=bool(data["one_position_per_symbol"]),
        )


@dataclass(frozen=True)
class DatabaseConfig:
    """Represent database file settings."""

    filename: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DatabaseConfig":
        """Create a DatabaseConfig from a dictionary."""
        return cls(filename=str(data["filename"]))


@dataclass(frozen=True)
class LoggingConfig:
    """Represent logging output and severity settings."""

    filename: str
    level: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoggingConfig":
        """Create a LoggingConfig from a dictionary."""
        return cls(filename=str(data["filename"]), level=str(data["level"]))


@dataclass(frozen=True)
class UiConfig:
    """Represent GUI behavior settings."""

    theme: str
    welcome_required: bool
    default_width: int
    default_height: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UiConfig":
        """Create a UiConfig from a dictionary."""
        return cls(
            theme=str(data["theme"]),
            welcome_required=bool(data["welcome_required"]),
            default_width=int(data["default_width"]),
            default_height=int(data["default_height"]),
        )


@dataclass(frozen=True)
class SentinelConfig:
    """Represent the complete Sentinel AI configuration."""

    application: ApplicationConfig
    trading: TradingConfig
    mt5: Mt5Config
    symbol_management: SymbolManagementConfig
    market_data: MarketDataConfig
    market_structure: MarketStructureConfig
    support_resistance: SupportResistanceConfig
    liquidity: LiquidityConfig
    imbalance: ImbalanceConfig
    momentum: MomentumConfig
    confidence: ConfidenceConfig
    entry_validation: EntryValidationConfig
    risk_reward: RiskRewardConfig
    manual_trading: ManualTradingConfig
    database: DatabaseConfig
    logging: LoggingConfig
    ui: UiConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SentinelConfig":
        """Create a SentinelConfig from a dictionary."""
        return cls(
            application=ApplicationConfig.from_dict(data["application"]),
            trading=TradingConfig.from_dict(data["trading"]),
            mt5=Mt5Config.from_dict(data["mt5"]),
            symbol_management=SymbolManagementConfig.from_dict(data["symbol_management"]),
            market_data=MarketDataConfig.from_dict(data["market_data"]),
            market_structure=MarketStructureConfig.from_dict(data["analysis"]["market_structure"]),
            support_resistance=SupportResistanceConfig.from_dict(data["analysis"]["support_resistance"]),
            liquidity=LiquidityConfig.from_dict(data["analysis"]["liquidity"]),
            imbalance=ImbalanceConfig.from_dict(data["analysis"]["imbalance"]),
            momentum=MomentumConfig.from_dict(data["analysis"]["momentum"]),
            confidence=ConfidenceConfig.from_dict(data["analysis"]["confidence"]),
            entry_validation=EntryValidationConfig.from_dict(data["analysis"]["entry_validation"]),
            risk_reward=RiskRewardConfig.from_dict(data["analysis"]["risk_reward"]),
            manual_trading=ManualTradingConfig.from_dict(data["manual_trading"]),
            database=DatabaseConfig.from_dict(data["database"]),
            logging=LoggingConfig.from_dict(data["logging"]),
            ui=UiConfig.from_dict(data["ui"]),
        )
