"""
MODULE: GUI-003
FILE: GUI-003-001
Module Name: Chart Panel
2.0.1
Purpose: Provides the central embedded live candlestick chart container without trading or domain analysis logic.
Dependencies: json, PySide6.QtCore, PySide6.QtWidgets, PySide6.QtWebEngineWidgets, sentinel_ai.models, sentinel_ai.utils.paths
Change History:
- 2.4.0: Preserved chart routing for guarded auto-trade completion build.
- 2.3.0: Preserved chart routing for completion build.
- 2.2.0: Preserved chart routing for dashboard simplification and close settlement fix.
- 2.1.0: Preserved chart routing for ledger maintenance tool build.
- 2.0.1: Preserved chart routing for pending/backlog separation fix.
- 2.0.0: Preserved chart routing for final stabilization build.
- 1.9.0.2: Preserved chart routing for app helper binding hotfix.
- 1.9.0.1: Preserved chart routing for MT5 resolver binding hotfix.
- 1.9.0: Preserved chart routing while stabilization diagnostics are added.
- 1.8.4.1: Preserved chart routing for startup binding hotfix.
- 1.8.4: Preserved chart routing while lifecycle diagnostics dashboard is added.
- 1.8.3: Preserved chart routing while pending-close settlement dashboard is added.
- 1.8.2: Preserved chart routing while active-ticket close guard is added.
- 1.8.1: Preserved chart routing while result verification dashboard is added.
- 1.8.0: Preserved chart routing for ledger outcome persistence sprint.
- 1.7.5: Preserved chart routing while persistent Sentinel ledger statistics are added.
- 1.7.4: Preserved chart routing while persistent Sentinel-owned recovery is added.
- 1.7.3: Preserved chart routing while Sentinel-owned statistics suppress outside MT5 trades.
- 1.7.2: Preserved chart routing while removing unreliable candle countdown timer.
- 1.7.1.3: Preserved chart routing while fixing live candle-cycle countdown synchronization.
- 1.7.1.2: Preserved chart routing while fixing countdown candle-open anchoring.
- 1.7.1.1: Preserved chart routing while fixing candle countdown timer.
- 1.7.1: Preserved chart routing while chart runtime adds timeframe countdown display.
- 1.7.0: Preserved active-position chart lock for closed-trade lifecycle tracking sprint.
- 1.6.2: Routed active-position protection status and missing SL/TP warning flags to chart runtime.
- 1.6.1.2: Routed missing active-position TP/SL as null to avoid zero-price chart scaling.
- 1.6.1.1: Preserved active-position chart routing for startup lock initialization hotfix.
- 1.6.1: Added active-position chart overlay routing and active-trade lock behavior.
- 0.1.0: Added chart panel shell with strict GUI-only responsibility.
- 0.3.0: Added market snapshot status rendering without analysis or trading logic.
- 0.4.0: Added embedded web chart rendering from validated chart-feed payloads.
- 0.5.0: Reused snapshot rendering path for live refresh updates without GUI market logic.
- 0.5.1: Preserved GUI-only chart bridge for runtime pan, zoom, and review-state behavior.
- 0.7.0: Added GUI-only market structure marker payload routing to chart runtime.
- 0.8.0: Added GUI-only support/resistance zone payload routing to chart runtime.
- 0.9.0: Added GUI-only historical BOS and liquidity payload routing to chart runtime.
- 0.9.1: Added bounded overlay segment payloads for support/resistance and liquidity.
- 0.9.2: Added GUI-only FVG and order block boxed-overlay routing and preserved BOS/COC event metadata.
- 0.9.3: Reduced overlay noise by routing active overlays only and added combined support/resistance range boxing.
- 0.9.3.1: Added swing-based fallback support/resistance range boundaries when only one formal S/R zone is available.
- 0.9.3.2: Preserved active-only overlay routing for chart runtime right-scroll and flicker-reduction patch.
- 0.9.3.3: Preserved GUI-only routing for consolidation-only S/R box and overlay cache runtime patch.
- 0.9.3.8: Preserved active overlay routing for single-canvas repaint artifact patch.
- 1.5.0: Preserved trade plan overlay routing for Sprint 15 manual execution.
- 1.4.1: Preserved trade plan overlay routing for polished review-modal patch.
- 1.4.0: Added GUI-only trade plan overlay routing for BUY_READY / SELL_READY review states.
- 0.9.3.7: Preserved active overlay routing for physical-pixel buffer swap patch.
- 0.9.3.6: Preserved active overlay routing for rendered-range status accuracy and render debounce patch.
- 0.9.3.5: Preserved active overlay routing for true-consolidation and double-buffer chart runtime patch.
- 0.9.3.4: Preserved active-only routing while runtime removes invalidated S/R boxes.
"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QFrame, QLabel, QStackedLayout, QVBoxLayout, QWidget

from sentinel_ai.models.imbalance import FairValueGapZone, ImbalanceSnapshot, OrderBlockZone
from sentinel_ai.models.liquidity import LiquidityPool, LiquiditySnapshot, LiquiditySweep
from sentinel_ai.models.risk_reward import RiskRewardSnapshot
from sentinel_ai.models.position_monitoring import PositionMonitorSnapshot
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot, StructureBreak
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot, SupportResistanceZone
from sentinel_ai.utils.paths import resource_path

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover
    QWebEngineView = None  # type: ignore[assignment]


class ChartPanel(QFrame):
    """Render the central chart area without embedding trading or analysis logic."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ChartPanel")
        self.setMinimumHeight(520)
        self._status_label = QLabel("Chart Area")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._chart_view: QWebEngineView | None = None
        self._chart_ready = False
        self._pending_snapshot: MarketDataSnapshot | None = None
        self._build_ui()
        self._initialize_chart_view()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)
        self._stacked_layout = QStackedLayout()
        self._fallback_container = QWidget()
        fallback_layout = QVBoxLayout(self._fallback_container)
        fallback_layout.setContentsMargins(0, 0, 0, 0)
        fallback_layout.addWidget(self._status_label)
        self._stacked_layout.addWidget(self._fallback_container)
        outer_layout.addLayout(self._stacked_layout)

    def _initialize_chart_view(self) -> None:
        if QWebEngineView is None:
            self.set_chart_status("PySide6 QtWebEngine is unavailable. Chart web view cannot be initialized.")
            return
        chart_resource = resource_path("chart/chart_view.html")
        if not chart_resource.exists():
            self.set_chart_status(f"Chart resource missing: {chart_resource}")
            return
        self._chart_view = QWebEngineView()
        self._chart_view.setContextMenuPolicy(Qt.NoContextMenu)
        self._chart_view.loadFinished.connect(self._handle_chart_load_finished)
        self._stacked_layout.addWidget(self._chart_view)
        self._stacked_layout.setCurrentWidget(self._chart_view)
        self._chart_view.setUrl(QUrl.fromLocalFile(str(chart_resource)))

    def _handle_chart_load_finished(self, loaded: bool) -> None:
        self._chart_ready = bool(loaded)
        if not loaded:
            self._stacked_layout.setCurrentWidget(self._fallback_container)
            self.set_chart_status("Embedded chart failed to load. Check packaged chart resources.")
            return
        if self._pending_snapshot is not None:
            self._render_market_snapshot(self._pending_snapshot)

    def set_chart_status(self, message: str) -> None:
        self._status_label.setText(message)
        if self._chart_view is not None and self._chart_ready:
            script = f"window.SentinelChart && window.SentinelChart.setStatus({json.dumps(message)});"
            self._chart_view.page().runJavaScript(script)

    def set_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        self._pending_snapshot = snapshot
        latest = snapshot.latest_candle
        if latest is None:
            self.set_chart_status(f"Market feed active for {snapshot.symbol} {snapshot.timeframe}. No candles returned.")
            return
        if self._chart_view is None or not self._chart_ready:
            message = (
                f"Market feed active: {snapshot.symbol} {snapshot.timeframe}\n"
                f"Candles loaded: {snapshot.candle_count}\n"
                f"Latest close: {latest.close:.2f}\n"
                f"Latest candle time: {latest.time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                "Embedded chart is waiting for the web runtime."
            )
            self.set_chart_status(message)
            return
        self._render_market_snapshot(snapshot)

    def set_market_structure_snapshot(self, structure_snapshot: MarketStructureSnapshot, max_markers: int, max_bos_markers: int) -> None:
        del max_markers, max_bos_markers
        if self._chart_view is None or not self._chart_ready:
            return
        marker_points = self._select_latest_swings(structure_snapshot)
        markers = [
            {
                "time": int(point.time.timestamp()),
                "price": point.price,
                "kind": point.kind,
                "label": "SH" if point.is_high else "SL",
            }
            for point in marker_points
        ]
        latest_break = structure_snapshot.latest_break
        break_payload = [self._structure_break_to_payload(latest_break)] if latest_break is not None else []
        metadata = {
            "symbol": structure_snapshot.symbol,
            "timeframe": structure_snapshot.timeframe,
            "bias": structure_snapshot.bias,
            "summary": structure_snapshot.summary,
            "breaks": break_payload,
            "latestBreak": break_payload[-1] if break_payload else None,
        }
        script = "window.SentinelChart && " + f"window.SentinelChart.setMarketStructure({json.dumps(markers)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    def set_support_resistance_snapshot(
        self,
        support_resistance_snapshot: SupportResistanceSnapshot,
        max_zones: int,
        structure_snapshot: MarketStructureSnapshot | None = None,
    ) -> None:
        del max_zones
        if self._chart_view is None or not self._chart_ready:
            return
        active_zones = self._select_active_support_resistance_zones(support_resistance_snapshot)
        zones = [payload for zone in active_zones if (payload := self._zone_to_payload(zone)) is not None]
        active_range = self._build_active_range_payload(support_resistance_snapshot, structure_snapshot)
        metadata = {
            "symbol": support_resistance_snapshot.symbol,
            "timeframe": support_resistance_snapshot.timeframe,
            "summary": support_resistance_snapshot.summary,
            "nearestSupport": self._zone_to_payload(support_resistance_snapshot.nearest_support),
            "nearestResistance": self._zone_to_payload(support_resistance_snapshot.nearest_resistance),
            "activeRange": active_range,
        }
        script = "window.SentinelChart && " + f"window.SentinelChart.setSupportResistance({json.dumps(zones)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    def set_liquidity_snapshot(self, liquidity_snapshot: LiquiditySnapshot, max_pools: int, max_sweeps: int) -> None:
        del max_pools, max_sweeps
        if self._chart_view is None or not self._chart_ready:
            return
        pools = [
            {
                "side": pool.side,
                "price": pool.price,
                "time": int(pool.reference_time.timestamp()),
                "endTime": int(pool.segment_end_time.timestamp()),
                "swept": pool.swept,
                "inducementCandidate": pool.inducement_candidate,
                "distanceFromPrice": pool.distance_from_price,
                "label": pool.label,
            }
            for pool in self._select_active_liquidity_pools(liquidity_snapshot)
        ]
        sweeps = [
            {
                "direction": sweep.direction,
                "sweptSide": sweep.swept_side,
                "referencePrice": sweep.reference_price,
                "referenceTime": int(sweep.reference_time.timestamp()),
                "time": int(sweep.swept_at.timestamp()),
                "wickPrice": sweep.wick_price,
                "closePrice": sweep.close_price,
                "label": sweep.label,
            }
            for sweep in self._select_latest_liquidity_sweeps(liquidity_snapshot)
        ]
        metadata = {"symbol": liquidity_snapshot.symbol, "timeframe": liquidity_snapshot.timeframe, "summary": liquidity_snapshot.summary}
        script = "window.SentinelChart && " + f"window.SentinelChart.setLiquidity({json.dumps(pools)}, {json.dumps(sweeps)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    def set_imbalance_snapshot(self, imbalance_snapshot: ImbalanceSnapshot, max_fvg_zones: int, max_order_blocks: int) -> None:
        del max_fvg_zones, max_order_blocks
        if self._chart_view is None or not self._chart_ready:
            return
        fair_value_gaps = [
            {
                "direction": zone.direction,
                "lowerPrice": zone.lower_price,
                "upperPrice": zone.upper_price,
                "startTime": int(zone.start_time.timestamp()),
                "endTime": int(zone.end_time.timestamp()),
                "filled": zone.filled,
                "partiallyMitigated": zone.partially_mitigated,
                "label": zone.label,
            }
            for zone in self._select_active_fair_value_gaps(imbalance_snapshot)
        ]
        order_blocks = [
            {
                "direction": zone.direction,
                "lowerPrice": zone.lower_price,
                "upperPrice": zone.upper_price,
                "startTime": int(zone.start_time.timestamp()),
                "endTime": int(zone.end_time.timestamp()),
                "mitigated": zone.mitigated,
                "invalidated": zone.invalidated,
                "label": zone.label,
            }
            for zone in self._select_active_order_blocks(imbalance_snapshot)
        ]
        metadata = {"symbol": imbalance_snapshot.symbol, "timeframe": imbalance_snapshot.timeframe, "summary": imbalance_snapshot.summary}
        script = "window.SentinelChart && " + f"window.SentinelChart.setImbalance({json.dumps(fair_value_gaps)}, {json.dumps(order_blocks)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    def set_trade_plan_snapshot(self, risk_reward_snapshot: RiskRewardSnapshot) -> None:
        """Route a validated ready trade plan to the chart overlay without placing trades."""
        if self._chart_view is None or not self._chart_ready:
            return
        plan = risk_reward_snapshot.plan
        if risk_reward_snapshot.direction not in {"BUY_READY", "SELL_READY"} or plan is None or not plan.valid:
            payload = None
        else:
            payload = {
                "direction": risk_reward_snapshot.direction,
                "entryPrice": plan.entry_price,
                "stopLoss": plan.stop_loss,
                "takeProfit": plan.take_profit,
                "riskRewardRatio": plan.risk_reward_ratio,
                "confidence": risk_reward_snapshot.confidence_percentage,
                "timeframe": risk_reward_snapshot.timeframe,
                "label": "BUY" if risk_reward_snapshot.direction == "BUY_READY" else "SELL",
            }
        metadata = {
            "symbol": risk_reward_snapshot.symbol,
            "timeframe": risk_reward_snapshot.timeframe,
            "direction": risk_reward_snapshot.direction,
            "summary": risk_reward_snapshot.summary,
        }
        script = "window.SentinelChart && " + f"window.SentinelChart.setTradePlan({json.dumps(payload)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    def set_active_position_snapshot(self, position_snapshot: PositionMonitorSnapshot) -> None:
        """Route the active MT5 position to the chart and lock markings to the real trade."""
        if self._chart_view is None or not self._chart_ready:
            return
        if not position_snapshot.has_open_position:
            payload = None
        else:
            payload = {
                "direction": position_snapshot.direction,
                "entryPrice": position_snapshot.open_price,
                "currentPrice": position_snapshot.current_price,
                "stopLoss": position_snapshot.stop_loss if position_snapshot.stop_loss is not None else None,
                "takeProfit": position_snapshot.take_profit if position_snapshot.take_profit is not None else None,
                "profit": position_snapshot.profit,
                "volume": position_snapshot.volume,
                "ticket": position_snapshot.ticket,
                "comment": position_snapshot.comment,
                "missingStopLoss": position_snapshot.missing_stop_loss,
                "missingTakeProfit": position_snapshot.missing_take_profit,
                "protectionStatus": position_snapshot.protection_status,
            }
        metadata = {
            "symbol": position_snapshot.symbol,
            "direction": position_snapshot.direction,
            "summary": position_snapshot.message,
            "locked": bool(position_snapshot.has_open_position),
        }
        script = "window.SentinelChart && " + f"window.SentinelChart.setActivePosition({json.dumps(payload)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)

    @staticmethod
    def _select_latest_swings(structure_snapshot: MarketStructureSnapshot) -> tuple[object, ...]:
        latest_high = structure_snapshot.swing_highs[-1] if structure_snapshot.swing_highs else None
        latest_low = structure_snapshot.swing_lows[-1] if structure_snapshot.swing_lows else None
        selected = [point for point in (latest_high, latest_low) if point is not None]
        selected.sort(key=lambda item: item.time)
        return tuple(selected)

    @staticmethod
    def _structure_break_to_payload(structure_break: StructureBreak) -> dict[str, object]:
        return {
            "time": int(structure_break.broken_at.timestamp()),
            "price": structure_break.close_price,
            "referencePrice": structure_break.reference_price,
            "direction": structure_break.direction,
            "eventType": structure_break.event_type,
            "label": structure_break.label,
        }

    @staticmethod
    def _select_active_support_resistance_zones(snapshot: SupportResistanceSnapshot) -> tuple[SupportResistanceZone, ...]:
        zones: list[SupportResistanceZone] = []
        if snapshot.nearest_support is not None:
            zones.append(snapshot.nearest_support)
        if snapshot.nearest_resistance is not None:
            zones.append(snapshot.nearest_resistance)
        return tuple(zones)

    @staticmethod
    def _build_active_range_payload(
        snapshot: SupportResistanceSnapshot,
        structure_snapshot: MarketStructureSnapshot | None,
    ) -> dict[str, object] | None:
        support = snapshot.nearest_support
        resistance = snapshot.nearest_resistance
        fallback_support = None if structure_snapshot is None else structure_snapshot.latest_swing_low
        fallback_resistance = None if structure_snapshot is None else structure_snapshot.latest_swing_high

        lower_price = support.lower_price if support is not None else (fallback_support.price if fallback_support is not None else None)
        upper_price = resistance.upper_price if resistance is not None else (fallback_resistance.price if fallback_resistance is not None else None)
        support_price = support.midpoint if support is not None else lower_price
        resistance_price = resistance.midpoint if resistance is not None else upper_price

        if lower_price is None or upper_price is None or float(upper_price) <= float(lower_price):
            return None

        start_candidates = []
        end_candidates = []
        if support is not None:
            start_candidates.append(support.segment_start_time)
            end_candidates.append(support.segment_end_time)
        if resistance is not None:
            start_candidates.append(resistance.segment_start_time)
            end_candidates.append(resistance.segment_end_time)
        if fallback_support is not None:
            start_candidates.append(fallback_support.time)
            end_candidates.append(fallback_support.time)
        if fallback_resistance is not None:
            start_candidates.append(fallback_resistance.time)
            end_candidates.append(fallback_resistance.time)
        if not start_candidates or not end_candidates:
            return None

        return {
            "lowerPrice": float(lower_price),
            "upperPrice": float(upper_price),
            "supportPrice": float(support_price),
            "resistancePrice": float(resistance_price),
            "startTime": int(min(start_candidates).timestamp()),
            "endTime": int(max(end_candidates).timestamp()),
            "supportLabel": "S",
            "resistanceLabel": "R",
            "supportTouches": support.touch_count if support is not None else 1,
            "resistanceTouches": resistance.touch_count if resistance is not None else 1,
            "supportSource": "ZONE" if support is not None else "SWING",
            "resistanceSource": "ZONE" if resistance is not None else "SWING",
        }

    @staticmethod
    def _select_active_liquidity_pools(snapshot: LiquiditySnapshot) -> tuple[LiquidityPool, ...]:
        buy_side = [pool for pool in snapshot.active_pools if pool.is_buy_side]
        sell_side = [pool for pool in snapshot.active_pools if pool.is_sell_side]
        selected: list[LiquidityPool] = []
        if buy_side:
            selected.append(sorted(buy_side, key=lambda item: (item.distance_from_price, item.reference_time), reverse=False)[0])
        if sell_side:
            selected.append(sorted(sell_side, key=lambda item: (item.distance_from_price, item.reference_time), reverse=False)[0])
        selected.sort(key=lambda item: item.reference_time)
        return tuple(selected)

    @staticmethod
    def _select_latest_liquidity_sweeps(snapshot: LiquiditySnapshot) -> tuple[LiquiditySweep, ...]:
        latest_sweep = snapshot.sweeps[-1] if snapshot.sweeps else None
        return (latest_sweep,) if latest_sweep is not None else ()

    @staticmethod
    def _select_active_fair_value_gaps(snapshot: ImbalanceSnapshot) -> tuple[FairValueGapZone, ...]:
        selected: list[FairValueGapZone] = []
        bullish = [zone for zone in snapshot.fair_value_gaps if zone.is_bullish and not zone.filled]
        bearish = [zone for zone in snapshot.fair_value_gaps if zone.is_bearish and not zone.filled]
        if bullish:
            selected.append(bullish[-1])
        if bearish:
            selected.append(bearish[-1])
        selected.sort(key=lambda item: item.created_at)
        return tuple(selected)

    @staticmethod
    def _select_active_order_blocks(snapshot: ImbalanceSnapshot) -> tuple[OrderBlockZone, ...]:
        selected: list[OrderBlockZone] = []
        bullish = [zone for zone in snapshot.order_blocks if zone.is_bullish and not zone.invalidated and not zone.mitigated]
        bearish = [zone for zone in snapshot.order_blocks if zone.is_bearish and not zone.invalidated and not zone.mitigated]
        if bullish:
            selected.append(bullish[-1])
        if bearish:
            selected.append(bearish[-1])
        selected.sort(key=lambda item: item.created_at)
        return tuple(selected)

    @staticmethod
    def _zone_to_payload(zone: SupportResistanceZone | None) -> dict[str, object] | None:
        if zone is None:
            return None
        return {
            "kind": zone.kind,
            "lowerPrice": zone.lower_price,
            "upperPrice": zone.upper_price,
            "midpoint": zone.midpoint,
            "touchCount": zone.touch_count,
            "rank": zone.rank,
            "label": zone.label,
            "startTime": int(zone.segment_start_time.timestamp()),
            "endTime": int(zone.segment_end_time.timestamp()),
        }

    def _render_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        if self._chart_view is None or not self._chart_ready:
            return
        payload = [
            {"time": candle.time, "open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close}
            for candle in snapshot.chart_candles
        ]
        latest = snapshot.latest_candle
        metadata = {
            "symbol": snapshot.symbol,
            "timeframe": snapshot.timeframe,
            "source": snapshot.source,
            "candleCount": snapshot.candle_count,
            "latestClose": latest.close if latest is not None else None,
            "latestTime": latest.time.isoformat() if latest is not None else None,
        }
        script = "window.SentinelChart && " + f"window.SentinelChart.setCandles({json.dumps(payload)}, {json.dumps(metadata)});"
        self._chart_view.page().runJavaScript(script)
