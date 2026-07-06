"""
MODULE: GUI-003
FILE: GUI-003-001
Module Name: Chart Panel
Version: 0.9.1
Purpose: Provides the central embedded live candlestick chart container without trading or domain analysis logic.
Dependencies: json, PySide6.QtCore, PySide6.QtWidgets, PySide6.QtWebEngineWidgets, sentinel_ai.models.market, sentinel_ai.models.market_structure, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added chart panel shell with strict GUI-only responsibility.
- 0.3.0: Added market snapshot status rendering without analysis or trading logic.
- 0.4.0: Added embedded web chart rendering from validated chart-feed payloads.
- 0.5.0: Reused snapshot rendering path for live refresh updates without GUI market logic.
- 0.5.1: Preserved GUI-only chart bridge for runtime pan, zoom, and review-state behavior.
- 0.7.0: Added GUI-only market structure marker payload routing to chart runtime.
- 0.8.0: Added GUI-only support/resistance zone payload routing to chart runtime.
- 0.9.0: Added GUI-only historical BOS and liquidity payload routing to chart runtime.
- 0.9.1: Added bounded overlay segment payloads for support/resistance and liquidity.
"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QFrame, QLabel, QStackedLayout, QVBoxLayout, QWidget

from sentinel_ai.models.liquidity import LiquiditySnapshot
from sentinel_ai.models.market import MarketDataSnapshot
from sentinel_ai.models.market_structure import MarketStructureSnapshot
from sentinel_ai.models.support_resistance import SupportResistanceSnapshot
from sentinel_ai.utils.paths import resource_path

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - depends on local PySide6 installation package components.
    QWebEngineView = None  # type: ignore[assignment]


class ChartPanel(QFrame):
    """Render the central chart area without embedding trading or analysis logic."""

    def __init__(self) -> None:
        """Initialize the chart panel UI."""
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
        """Build the chart panel layout."""
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
        """Initialize the embedded web chart when Qt WebEngine is available."""
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
        """Render queued candle data after the embedded chart runtime finishes loading."""
        self._chart_ready = bool(loaded)
        if not loaded:
            self._stacked_layout.setCurrentWidget(self._fallback_container)
            self.set_chart_status("Embedded chart failed to load. Check packaged chart resources.")
            return
        if self._pending_snapshot is not None:
            self._render_market_snapshot(self._pending_snapshot)

    def set_chart_status(self, message: str) -> None:
        """Set a chart status message supplied by a non-GUI service."""
        self._status_label.setText(message)
        if self._chart_view is not None and self._chart_ready:
            script = f"window.SentinelChart && window.SentinelChart.setStatus({json.dumps(message)});"
            self._chart_view.page().runJavaScript(script)

    def set_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        """Render a validated market data snapshot on the embedded chart."""
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
        """Route precomputed market structure markers to the embedded chart runtime."""
        if self._chart_view is None or not self._chart_ready:
            return

        marker_limit = max(1, int(max_markers))
        marker_points = structure_snapshot.marker_points[-marker_limit:]
        markers = [
            {
                "time": int(point.time.timestamp()),
                "price": point.price,
                "kind": point.kind,
                "label": "SH" if point.is_high else "SL",
            }
            for point in marker_points
        ]
        break_limit = max(1, int(max_bos_markers))
        break_events = structure_snapshot.historical_breaks[-break_limit:]
        break_payload = [
            {
                "time": int(item.broken_at.timestamp()),
                "price": item.close_price,
                "referencePrice": item.reference_price,
                "direction": item.direction,
                "label": item.label,
            }
            for item in break_events
        ]
        latest_break = structure_snapshot.latest_break
        metadata = {
            "symbol": structure_snapshot.symbol,
            "timeframe": structure_snapshot.timeframe,
            "bias": structure_snapshot.bias,
            "summary": structure_snapshot.summary,
            "breaks": break_payload,
            "latestBreak": break_payload[-1] if latest_break is not None and break_payload else None,
        }
        script = (
            "window.SentinelChart && "
            f"window.SentinelChart.setMarketStructure({json.dumps(markers)}, {json.dumps(metadata)});"
        )
        self._chart_view.page().runJavaScript(script)


    def set_support_resistance_snapshot(self, support_resistance_snapshot: SupportResistanceSnapshot, max_zones: int) -> None:
        """Route precomputed support/resistance zones to the embedded chart runtime."""
        if self._chart_view is None or not self._chart_ready:
            return

        zone_limit = max(1, int(max_zones))
        zones = [
            {
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
            for zone in support_resistance_snapshot.all_zones[:zone_limit]
        ]
        metadata = {
            "symbol": support_resistance_snapshot.symbol,
            "timeframe": support_resistance_snapshot.timeframe,
            "summary": support_resistance_snapshot.summary,
            "nearestSupport": self._zone_to_payload(support_resistance_snapshot.nearest_support),
            "nearestResistance": self._zone_to_payload(support_resistance_snapshot.nearest_resistance),
        }
        script = (
            "window.SentinelChart && "
            f"window.SentinelChart.setSupportResistance({json.dumps(zones)}, {json.dumps(metadata)});"
        )
        self._chart_view.page().runJavaScript(script)

    def set_liquidity_snapshot(self, liquidity_snapshot: LiquiditySnapshot, max_pools: int, max_sweeps: int) -> None:
        """Route precomputed liquidity pools and sweeps to the embedded chart runtime."""
        if self._chart_view is None or not self._chart_ready:
            return

        pool_limit = max(1, int(max_pools))
        sweep_limit = max(1, int(max_sweeps))
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
            for pool in liquidity_snapshot.pools[:pool_limit]
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
            for sweep in liquidity_snapshot.sweeps[-sweep_limit:]
        ]
        metadata = {
            "symbol": liquidity_snapshot.symbol,
            "timeframe": liquidity_snapshot.timeframe,
            "summary": liquidity_snapshot.summary,
        }
        script = (
            "window.SentinelChart && "
            f"window.SentinelChart.setLiquidity({json.dumps(pools)}, {json.dumps(sweeps)}, {json.dumps(metadata)});"
        )
        self._chart_view.page().runJavaScript(script)


    @staticmethod
    def _zone_to_payload(zone: object) -> dict[str, object] | None:
        """Convert an optional support/resistance zone to a chart-safe payload."""
        if zone is None:
            return None
        return {
            "kind": getattr(zone, "kind"),
            "lowerPrice": getattr(zone, "lower_price"),
            "upperPrice": getattr(zone, "upper_price"),
            "midpoint": getattr(zone, "midpoint"),
            "touchCount": getattr(zone, "touch_count"),
            "rank": getattr(zone, "rank"),
            "label": getattr(zone, "label"),
            "startTime": int(getattr(zone, "segment_start_time").timestamp()),
            "endTime": int(getattr(zone, "segment_end_time").timestamp()),
        }

    def _render_market_snapshot(self, snapshot: MarketDataSnapshot) -> None:
        """Send validated chart candles to the embedded chart runtime."""
        if self._chart_view is None or not self._chart_ready:
            return

        payload = [
            {
                "time": candle.time,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
            }
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
        script = (
            "window.SentinelChart && "
            f"window.SentinelChart.setCandles({json.dumps(payload)}, {json.dumps(metadata)});"
        )
        self._chart_view.page().runJavaScript(script)
