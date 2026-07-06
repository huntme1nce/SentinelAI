"""
MODULE: GUI-003
FILE: GUI-003-001
Module Name: Chart Panel
Version: 0.4.0
Purpose: Provides the central embedded live candlestick chart container without trading or analysis logic.
Dependencies: json, PySide6.QtCore, PySide6.QtWidgets, PySide6.QtWebEngineWidgets, sentinel_ai.models.market, sentinel_ai.utils.paths
Change History:
- 0.1.0: Added chart panel shell with strict GUI-only responsibility.
- 0.3.0: Added market snapshot status rendering without analysis or trading logic.
- 0.4.0: Added embedded web chart rendering from validated chart-feed payloads.
"""

from __future__ import annotations

import json

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QFrame, QLabel, QStackedLayout, QVBoxLayout, QWidget

from sentinel_ai.models.market import MarketDataSnapshot
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
