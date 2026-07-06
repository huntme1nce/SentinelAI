/*
MODULE: CHART-002
FILE: CHART-002-001
Module Name: Sentinel Chart Runtime
Version: 0.7.0
Purpose: Renders validated candlestick data with controlled live updates, chart panning, zooming, review-state preservation, and market structure markers.
Dependencies: Browser Canvas API
Change History:
- 0.4.0: Added offline-safe candlestick renderer for the Sprint 4 embedded chart panel.
- 0.5.1: Added drag-to-pan, mouse-wheel zoom, double-click reset, and chart-position preservation during live refresh.
- 0.7.0: Added market structure marker and break-of-structure overlay rendering.
*/

(function () {
  "use strict";

  const canvas = document.getElementById("chart-canvas");
  const overlay = document.getElementById("status-overlay");
  const context = canvas.getContext("2d");

  const MIN_VISIBLE_CANDLES = 20;
  const MAX_VISIBLE_CANDLES = 500;
  const MIN_ZOOM_SCALE = 0.60;
  const MAX_ZOOM_SCALE = 3.50;

  const state = {
    candles: [],
    metadata: {
      symbol: "-",
      timeframe: "-",
      candleCount: 0,
      latestClose: null,
      latestTime: "-",
    },
    crosshair: null,
    structure: {
      markers: [],
      metadata: {
        bias: "-",
        summary: "",
        latestBreak: null,
      },
    },
    view: {
      offsetFromRight: 0,
      zoomScale: 1,
      manualNavigation: false,
    },
    drag: {
      active: false,
      startX: 0,
      startOffsetFromRight: 0,
      moved: false,
    },
  };

  function resizeCanvas() {
    const deviceRatio = Math.max(window.devicePixelRatio || 1, 1);
    const width = Math.max(Math.floor(canvas.clientWidth), 1);
    const height = Math.max(Math.floor(canvas.clientHeight), 1);
    const targetWidth = Math.floor(width * deviceRatio);
    const targetHeight = Math.floor(height * deviceRatio);

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }

    context.setTransform(deviceRatio, 0, 0, deviceRatio, 0, 0);
    renderChart();
  }

  function setStatus(message) {
    overlay.textContent = String(message || "Sentinel AI chart ready.");
  }

  function setCandles(candles, metadata) {
    const normalizedCandles = Array.isArray(candles) ? candles : [];
    const previousSymbol = state.metadata.symbol;
    const previousTimeframe = state.metadata.timeframe;
    const nextMetadata = Object.assign({}, state.metadata, metadata || {});
    const marketContextChanged = previousSymbol !== nextMetadata.symbol || previousTimeframe !== nextMetadata.timeframe;

    state.candles = normalizedCandles.filter(isValidCandle);
    state.metadata = Object.assign({}, nextMetadata, { candleCount: state.candles.length });

    if (marketContextChanged) {
      resetViewToLatest(false);
    } else {
      clampViewState(createLayout(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1)));
    }

    renderChart();
  }


  function setMarketStructure(markers, metadata) {
    const normalizedMarkers = Array.isArray(markers) ? markers : [];
    state.structure.markers = normalizedMarkers.filter(isValidStructureMarker);
    state.structure.metadata = Object.assign({}, state.structure.metadata, metadata || {});
    renderChart();
  }

  function isValidStructureMarker(marker) {
    return marker &&
      Number.isFinite(Number(marker.time)) &&
      Number.isFinite(Number(marker.price)) &&
      (marker.kind === "HIGH" || marker.kind === "LOW");
  }

  function isValidCandle(candle) {
    return candle &&
      Number.isFinite(Number(candle.time)) &&
      Number.isFinite(Number(candle.open)) &&
      Number.isFinite(Number(candle.high)) &&
      Number.isFinite(Number(candle.low)) &&
      Number.isFinite(Number(candle.close));
  }

  function renderChart() {
    const width = Math.max(canvas.clientWidth, 1);
    const height = Math.max(canvas.clientHeight, 1);
    context.clearRect(0, 0, width, height);
    drawBackground(width, height);

    if (state.candles.length === 0) {
      setStatus("No validated candles available for chart rendering.");
      drawCenteredMessage(width, height, "Waiting for validated market candles...");
      return;
    }

    const layout = createLayout(width, height);
    clampViewState(layout);
    const visibleRange = resolveVisibleRange(layout);
    const visibleCandles = visibleRange.candles;
    const priceRange = resolvePriceRange(visibleCandles);

    drawGrid(layout, priceRange);
    drawCandles(layout, visibleCandles, priceRange);
    drawStructureMarkers(layout, visibleRange, priceRange);
    drawAxes(layout, visibleRange);
    drawLatestPriceLine(layout, visibleCandles, priceRange);
    drawCrosshair(layout, visibleRange, priceRange);
    updateOverlay(visibleCandles);
  }

  function drawBackground(width, height) {
    const gradient = context.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "#071419");
    gradient.addColorStop(1, "#03090c");
    context.fillStyle = gradient;
    context.fillRect(0, 0, width, height);
  }

  function createLayout(width, height) {
    const padding = {
      left: 18,
      right: 84,
      top: 30,
      bottom: 36,
    };
    const plotWidth = Math.max(width - padding.left - padding.right, 20);
    const plotHeight = Math.max(height - padding.top - padding.bottom, 20);
    const baseSlotWidth = 10;
    const slotWidth = Math.max(4, baseSlotWidth * state.view.zoomScale);
    const candleWidth = Math.max(2.5, Math.min(slotWidth * 0.70, 14));
    const candleGap = Math.max(slotWidth - candleWidth, 1);
    const visibleCapacity = Math.max(
      MIN_VISIBLE_CANDLES,
      Math.min(MAX_VISIBLE_CANDLES, Math.floor(plotWidth / slotWidth))
    );

    return {
      width,
      height,
      padding,
      plotLeft: padding.left,
      plotRight: width - padding.right,
      plotTop: padding.top,
      plotBottom: height - padding.bottom,
      plotWidth,
      plotHeight,
      candleWidth,
      candleGap,
      slotWidth,
      visibleCapacity,
    };
  }

  function resolveVisibleRange(layout) {
    const totalCandles = state.candles.length;
    const visibleCount = Math.min(layout.visibleCapacity, totalCandles);
    const endIndexExclusive = Math.max(visibleCount, totalCandles - state.view.offsetFromRight);
    const startIndex = Math.max(0, endIndexExclusive - visibleCount);
    const resolvedEndIndex = Math.min(totalCandles, startIndex + visibleCount);

    return {
      candles: state.candles.slice(startIndex, resolvedEndIndex),
      startIndex,
      endIndexExclusive: resolvedEndIndex,
      visibleCount: resolvedEndIndex - startIndex,
    };
  }

  function clampViewState(layout) {
    state.view.zoomScale = clamp(state.view.zoomScale, MIN_ZOOM_SCALE, MAX_ZOOM_SCALE);
    const visibleCount = Math.min(layout.visibleCapacity, state.candles.length);
    const maxOffsetFromRight = Math.max(0, state.candles.length - visibleCount);
    state.view.offsetFromRight = Math.round(clamp(state.view.offsetFromRight, 0, maxOffsetFromRight));
    state.view.manualNavigation = state.view.offsetFromRight > 0;
  }

  function resolvePriceRange(candles) {
    let minPrice = Number.POSITIVE_INFINITY;
    let maxPrice = Number.NEGATIVE_INFINITY;

    candles.forEach((candle) => {
      minPrice = Math.min(minPrice, Number(candle.low));
      maxPrice = Math.max(maxPrice, Number(candle.high));
    });

    if (!Number.isFinite(minPrice) || !Number.isFinite(maxPrice)) {
      minPrice = 0;
      maxPrice = 1;
    }

    const rawRange = Math.max(maxPrice - minPrice, 0.0001);
    const padding = rawRange * 0.08;
    return {
      min: minPrice - padding,
      max: maxPrice + padding,
      range: rawRange + padding * 2,
    };
  }

  function yForPrice(layout, priceRange, price) {
    const normalized = (Number(price) - priceRange.min) / priceRange.range;
    return layout.plotBottom - normalized * layout.plotHeight;
  }

  function xForIndex(layout, index, visibleCount) {
    const startX = layout.plotRight - visibleCount * layout.slotWidth;
    return startX + index * layout.slotWidth + layout.slotWidth / 2;
  }

  function drawGrid(layout, priceRange) {
    context.save();
    context.strokeStyle = "rgba(54, 108, 126, 0.23)";
    context.lineWidth = 1;
    context.font = "11px Segoe UI, Arial";
    context.fillStyle = "rgba(180, 226, 238, 0.78)";

    const horizontalLines = 5;
    for (let i = 0; i <= horizontalLines; i += 1) {
      const ratio = i / horizontalLines;
      const y = layout.plotTop + ratio * layout.plotHeight;
      context.beginPath();
      context.moveTo(layout.plotLeft, Math.round(y) + 0.5);
      context.lineTo(layout.plotRight, Math.round(y) + 0.5);
      context.stroke();

      const price = priceRange.max - ratio * priceRange.range;
      context.fillText(formatPrice(price), layout.plotRight + 10, y + 4);
    }

    const verticalLines = 8;
    for (let i = 0; i <= verticalLines; i += 1) {
      const x = layout.plotLeft + (i / verticalLines) * layout.plotWidth;
      context.beginPath();
      context.moveTo(Math.round(x) + 0.5, layout.plotTop);
      context.lineTo(Math.round(x) + 0.5, layout.plotBottom);
      context.stroke();
    }

    context.restore();
  }

  function drawCandles(layout, candles, priceRange) {
    candles.forEach((candle, index) => {
      const open = Number(candle.open);
      const high = Number(candle.high);
      const low = Number(candle.low);
      const close = Number(candle.close);
      const x = xForIndex(layout, index, candles.length);
      const openY = yForPrice(layout, priceRange, open);
      const highY = yForPrice(layout, priceRange, high);
      const lowY = yForPrice(layout, priceRange, low);
      const closeY = yForPrice(layout, priceRange, close);
      const isBullish = close >= open;
      const wickColor = isBullish ? "#42d6a4" : "#ff5c7a";
      const bodyColor = isBullish ? "#20c997" : "#f0526b";
      const bodyTop = Math.min(openY, closeY);
      const bodyHeight = Math.max(Math.abs(closeY - openY), 1.2);
      const bodyLeft = x - layout.candleWidth / 2;

      context.strokeStyle = wickColor;
      context.lineWidth = 1.2;
      context.beginPath();
      context.moveTo(Math.round(x) + 0.5, highY);
      context.lineTo(Math.round(x) + 0.5, lowY);
      context.stroke();

      context.fillStyle = bodyColor;
      context.fillRect(bodyLeft, bodyTop, layout.candleWidth, bodyHeight);
    });
  }


  function drawStructureMarkers(layout, visibleRange, priceRange) {
    if (!state.structure.markers || state.structure.markers.length === 0) {
      return;
    }

    const visibleTimeToIndex = new Map();
    visibleRange.candles.forEach((candle, index) => {
      visibleTimeToIndex.set(Number(candle.time), index);
    });

    context.save();
    context.font = "bold 10px Segoe UI, Arial";
    context.textAlign = "center";
    state.structure.markers.forEach((marker) => {
      const visibleIndex = visibleTimeToIndex.get(Number(marker.time));
      if (visibleIndex === undefined) {
        return;
      }
      const x = xForIndex(layout, visibleIndex, visibleRange.candles.length);
      const y = yForPrice(layout, priceRange, Number(marker.price));
      const isHigh = marker.kind === "HIGH";
      const markerY = isHigh ? y - 13 : y + 13;
      const labelY = isHigh ? y - 20 : y + 29;
      const fillColor = isHigh ? "#ffce5c" : "#5ed7ff";
      context.fillStyle = fillColor;
      context.beginPath();
      if (isHigh) {
        context.moveTo(x, markerY);
        context.lineTo(x - 5, markerY - 8);
        context.lineTo(x + 5, markerY - 8);
      } else {
        context.moveTo(x, markerY);
        context.lineTo(x - 5, markerY + 8);
        context.lineTo(x + 5, markerY + 8);
      }
      context.closePath();
      context.fill();
      context.fillText(String(marker.label || (isHigh ? "SH" : "SL")), x, labelY);
    });

    const latestBreak = state.structure.metadata.latestBreak;
    if (latestBreak && Number.isFinite(Number(latestBreak.time)) && Number.isFinite(Number(latestBreak.price))) {
      const breakIndex = visibleTimeToIndex.get(Number(latestBreak.time));
      if (breakIndex !== undefined) {
        const x = xForIndex(layout, breakIndex, visibleRange.candles.length);
        const y = yForPrice(layout, priceRange, Number(latestBreak.price));
        context.fillStyle = latestBreak.direction === "BULLISH" ? "#20c997" : "#f0526b";
        context.fillRect(x - 21, y - 11, 42, 18);
        context.fillStyle = "#031014";
        context.fillText(String(latestBreak.label || "BOS"), x, y + 2);
      }
    }
    context.restore();
  }

  function drawAxes(layout, visibleRange) {
    const candles = visibleRange.candles;
    context.save();
    context.strokeStyle = "rgba(81, 155, 176, 0.55)";
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(layout.plotRight + 0.5, layout.plotTop);
    context.lineTo(layout.plotRight + 0.5, layout.plotBottom);
    context.lineTo(layout.plotLeft, layout.plotBottom + 0.5);
    context.stroke();

    context.font = "11px Segoe UI, Arial";
    context.fillStyle = "rgba(180, 226, 238, 0.78)";
    const labels = 4;
    for (let i = 0; i <= labels; i += 1) {
      const index = Math.floor((candles.length - 1) * (i / labels));
      const candle = candles[index];
      if (!candle) {
        continue;
      }
      const x = xForIndex(layout, index, candles.length) - 22;
      context.fillText(formatTime(Number(candle.time)), x, layout.plotBottom + 20);
    }
    context.restore();
  }

  function drawLatestPriceLine(layout, candles, priceRange) {
    const latest = state.candles[state.candles.length - 1];
    if (!latest) {
      return;
    }

    const latestClose = Number(latest.close);
    const y = yForPrice(layout, priceRange, latestClose);
    const bullish = latestClose >= Number(latest.open);
    const color = bullish ? "#20c997" : "#f0526b";

    context.save();
    context.setLineDash([5, 5]);
    context.strokeStyle = color;
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(layout.plotLeft, Math.round(y) + 0.5);
    context.lineTo(layout.plotRight, Math.round(y) + 0.5);
    context.stroke();
    context.setLineDash([]);
    context.fillStyle = color;
    context.fillRect(layout.plotRight + 6, y - 10, 72, 20);
    context.fillStyle = "#031014";
    context.font = "bold 11px Segoe UI, Arial";
    context.fillText(formatPrice(latestClose), layout.plotRight + 10, y + 4);
    context.restore();
  }

  function drawCrosshair(layout, visibleRange, priceRange) {
    if (state.crosshair === null || state.drag.active) {
      return;
    }

    const candles = visibleRange.candles;
    const x = state.crosshair.x;
    const y = state.crosshair.y;
    if (x < layout.plotLeft || x > layout.plotRight || y < layout.plotTop || y > layout.plotBottom) {
      return;
    }

    context.save();
    context.strokeStyle = "rgba(211, 244, 255, 0.45)";
    context.lineWidth = 1;
    context.setLineDash([4, 4]);
    context.beginPath();
    context.moveTo(x, layout.plotTop);
    context.lineTo(x, layout.plotBottom);
    context.moveTo(layout.plotLeft, y);
    context.lineTo(layout.plotRight, y);
    context.stroke();
    context.setLineDash([]);

    const rawIndex = Math.round((x - (layout.plotRight - candles.length * layout.slotWidth) - layout.slotWidth / 2) / layout.slotWidth);
    const index = Math.max(0, Math.min(candles.length - 1, rawIndex));
    const candle = candles[index];
    if (candle) {
      const absoluteIndex = visibleRange.startIndex + index;
      const text = `${formatTime(Number(candle.time))}  #${absoluteIndex + 1}  O:${formatPrice(candle.open)} H:${formatPrice(candle.high)} L:${formatPrice(candle.low)} C:${formatPrice(candle.close)}`;
      context.fillStyle = "rgba(2, 12, 16, 0.90)";
      context.fillRect(layout.plotLeft + 8, layout.plotTop + 8, Math.min(520, text.length * 7.1), 24);
      context.fillStyle = "#d9f6ff";
      context.font = "12px Segoe UI, Arial";
      context.fillText(text, layout.plotLeft + 16, layout.plotTop + 25);
    }
    context.restore();
  }

  function drawCenteredMessage(width, height, message) {
    context.save();
    context.font = "14px Segoe UI, Arial";
    context.fillStyle = "#d9f6ff";
    context.textAlign = "center";
    context.fillText(message, width / 2, height / 2);
    context.restore();
  }

  function updateOverlay(visibleCandles) {
    const latest = state.candles[state.candles.length - 1];
    const latestClose = latest ? formatPrice(latest.close) : "-";
    const latestTime = latest ? formatDateTime(Number(latest.time)) : "-";
    const symbol = state.metadata.symbol || "-";
    const timeframe = state.metadata.timeframe || "-";
    const mode = state.view.manualNavigation ? "Reviewing history | Double-click returns latest" : "Live view";
    const zoom = `Zoom ${state.view.zoomScale.toFixed(2)}x`;
    const visibleText = `${visibleCandles.length}/${state.candles.length} visible`;
    const bias = state.structure.metadata.bias && state.structure.metadata.bias !== "-" ? ` | Structure: ${state.structure.metadata.bias}` : "";
    setStatus(`${symbol} ${timeframe} | ${visibleText} | Latest: ${latestClose} | ${latestTime}${bias} | ${mode} | ${zoom}`);
  }

  function formatPrice(price) {
    const value = Number(price);
    if (!Number.isFinite(value)) {
      return "-";
    }
    return value.toFixed(2);
  }

  function formatTime(timestampSeconds) {
    const date = new Date(timestampSeconds * 1000);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
  }

  function formatDateTime(timestampSeconds) {
    const date = new Date(timestampSeconds * 1000);
    return date.toISOString().replace("T", " ").replace(".000Z", " UTC");
  }

  function clamp(value, minimum, maximum) {
    return Math.min(Math.max(Number(value), minimum), maximum);
  }

  function resetViewToLatest(resetZoom) {
    state.view.offsetFromRight = 0;
    state.view.manualNavigation = false;
    if (resetZoom) {
      state.view.zoomScale = 1;
    }
  }

  function updateCanvasCursor() {
    if (state.drag.active) {
      canvas.style.cursor = "grabbing";
    } else if (state.view.manualNavigation) {
      canvas.style.cursor = "grab";
    } else {
      canvas.style.cursor = "crosshair";
    }
  }

  canvas.addEventListener("mousedown", function (event) {
    if (event.button !== 0) {
      return;
    }
    const rect = canvas.getBoundingClientRect();
    state.drag.active = true;
    state.drag.startX = event.clientX - rect.left;
    state.drag.startOffsetFromRight = state.view.offsetFromRight;
    state.drag.moved = false;
    updateCanvasCursor();
  });

  canvas.addEventListener("mousemove", function (event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    state.crosshair = { x, y };

    if (state.drag.active) {
      const layout = createLayout(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1));
      const deltaCandles = Math.round((x - state.drag.startX) / layout.slotWidth);
      if (Math.abs(deltaCandles) > 0) {
        state.drag.moved = true;
      }
      state.view.offsetFromRight = state.drag.startOffsetFromRight + deltaCandles;
      clampViewState(layout);
    }

    updateCanvasCursor();
    renderChart();
  });

  canvas.addEventListener("mouseup", function () {
    state.drag.active = false;
    updateCanvasCursor();
    renderChart();
  });

  canvas.addEventListener("mouseleave", function () {
    state.drag.active = false;
    state.crosshair = null;
    updateCanvasCursor();
    renderChart();
  });

  canvas.addEventListener("wheel", function (event) {
    event.preventDefault();
    if (state.candles.length === 0) {
      return;
    }

    const layoutBefore = createLayout(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1));
    const visibleBefore = resolveVisibleRange(layoutBefore);
    const centerIndex = visibleBefore.startIndex + Math.floor(visibleBefore.visibleCount / 2);
    const zoomMultiplier = event.deltaY < 0 ? 1.15 : 1 / 1.15;
    state.view.zoomScale = clamp(state.view.zoomScale * zoomMultiplier, MIN_ZOOM_SCALE, MAX_ZOOM_SCALE);

    const layoutAfter = createLayout(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1));
    const visibleAfterCount = Math.min(layoutAfter.visibleCapacity, state.candles.length);
    state.view.offsetFromRight = state.candles.length - centerIndex - Math.ceil(visibleAfterCount / 2);
    clampViewState(layoutAfter);
    state.view.manualNavigation = state.view.offsetFromRight > 0;
    updateCanvasCursor();
    renderChart();
  }, { passive: false });

  canvas.addEventListener("dblclick", function () {
    resetViewToLatest(true);
    updateCanvasCursor();
    renderChart();
  });

  window.addEventListener("mouseup", function () {
    if (state.drag.active) {
      state.drag.active = false;
      updateCanvasCursor();
      renderChart();
    }
  });

  window.addEventListener("resize", resizeCanvas);

  window.SentinelChart = {
    setCandles: setCandles,
    setMarketStructure: setMarketStructure,
    setStatus: setStatus,
    render: renderChart,
    resetViewToLatest: function () {
      resetViewToLatest(true);
      renderChart();
    },
  };

  updateCanvasCursor();
  resizeCanvas();
}());
