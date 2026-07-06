/*
MODULE: RES-004
FILE: RES-004-002
Module Name: Sentinel Chart Runtime
Version: 0.4.0
Purpose: Renders validated OHLC candles inside the embedded chart web view using a standalone HTML5 canvas runtime.
Dependencies: Browser Canvas API
Change History:
- 0.4.0: Added offline-safe candlestick renderer for the Sprint 4 embedded chart panel.
*/

(function () {
  "use strict";

  const canvas = document.getElementById("chart-canvas");
  const overlay = document.getElementById("status-overlay");
  const context = canvas.getContext("2d");

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
    state.candles = normalizedCandles.filter(isValidCandle);
    state.metadata = Object.assign({}, state.metadata, metadata || {}, { candleCount: state.candles.length });
    renderChart();
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
    const visibleCandles = state.candles.slice(-layout.visibleCapacity);
    const priceRange = resolvePriceRange(visibleCandles);
    drawGrid(layout, priceRange);
    drawCandles(layout, visibleCandles, priceRange);
    drawAxes(layout, visibleCandles, priceRange);
    drawLatestPriceLine(layout, visibleCandles, priceRange);
    drawCrosshair(layout, visibleCandles, priceRange);
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
    const candleWidth = 7;
    const candleGap = 3;
    const slotWidth = candleWidth + candleGap;
    const visibleCapacity = Math.max(Math.floor(plotWidth / slotWidth), 20);

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

  function drawAxes(layout, candles) {
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
    const latest = candles[candles.length - 1];
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

  function drawCrosshair(layout, candles, priceRange) {
    if (state.crosshair === null) {
      return;
    }

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
      const text = `${formatTime(Number(candle.time))}  O:${formatPrice(candle.open)} H:${formatPrice(candle.high)} L:${formatPrice(candle.low)} C:${formatPrice(candle.close)}`;
      context.fillStyle = "rgba(2, 12, 16, 0.90)";
      context.fillRect(layout.plotLeft + 8, layout.plotTop + 8, Math.min(460, text.length * 7.1), 24);
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

  function updateOverlay(candles) {
    const latest = candles[candles.length - 1];
    const latestClose = latest ? formatPrice(latest.close) : "-";
    const latestTime = latest ? formatDateTime(Number(latest.time)) : "-";
    const symbol = state.metadata.symbol || "-";
    const timeframe = state.metadata.timeframe || "-";
    setStatus(`${symbol} ${timeframe} | Candles: ${state.candles.length} | Latest: ${latestClose} | ${latestTime}`);
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

  canvas.addEventListener("mousemove", function (event) {
    const rect = canvas.getBoundingClientRect();
    state.crosshair = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
    renderChart();
  });

  canvas.addEventListener("mouseleave", function () {
    state.crosshair = null;
    renderChart();
  });

  window.addEventListener("resize", resizeCanvas);

  window.SentinelChart = {
    setCandles: setCandles,
    setStatus: setStatus,
    render: renderChart,
  };

  resizeCanvas();
}());
