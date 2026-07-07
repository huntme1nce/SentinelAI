/*
MODULE: CHART-002
FILE: CHART-002-001
Module Name: Sentinel Chart Runtime
2.0.1
Purpose: Renders validated candlestick data with controlled live updates, chart panning, zooming, market structure, support/resistance, liquidity, fair value gap, and order block overlays.
Dependencies: Browser Canvas API
Change History:
- 2.4.0: Preserved chart runtime for guarded auto-trade completion build.
- 2.3.0: Preserved chart runtime for completion build.
- 2.2.0: Preserved chart runtime for dashboard simplification and close settlement fix.
- 2.1.0: Preserved chart runtime for ledger maintenance tool build.
- 2.0.1: Preserved chart runtime for pending/backlog separation fix.
- 2.0.0: Preserved chart runtime for final stabilization build.
- 1.9.0.2: Preserved chart runtime for app helper binding hotfix.
- 1.9.0.1: Preserved chart runtime for MT5 resolver binding hotfix.
- 1.9.0: Preserved chart runtime while stabilization diagnostics are added.
- 1.8.4.1: Preserved active-trade chart rendering for startup binding hotfix.
- 1.8.4: Preserved active-trade chart rendering while lifecycle diagnostics dashboard is added.
- 1.8.3: Preserved active-trade chart rendering while pending-close settlement is added.
- 1.8.2: Preserved active-trade chart rendering while active-ticket close guard is added.
- 1.8.1: Preserved active-trade chart rendering while result verification dashboard is added.
- 1.8.0: Preserved active-trade chart behavior for ledger outcome persistence sprint.
- 1.7.5: Preserved countdown removal and active-trade header while persistent Sentinel ledger statistics are added.
- 1.7.4: Preserved countdown removal and active-trade header while persistent Sentinel-owned recovery is added.
- 1.7.3: Preserved countdown removal and active-trade header while Sentinel-owned statistics are added.
- 1.7.2: Removed unreliable candle countdown timer and preserved active-trade header priority.
- 1.7.1.3: Fixed countdown stuck at full duration by normalizing candle timestamp units and using live candle-cycle modulo countdown.
- 1.7.1.2: Anchored countdown to latest broker candle open so the timer resets only when a new candle is received.
- 1.7.1.1: Fixed countdown timer stuck at full timeframe by repainting every second and using wall-clock timeframe alignment.
- 1.7.1: Added timeframe-based candle countdown timer below current price and active-trade header priority.
- 1.7.0: Preserved active-position chart lock for closed-trade lifecycle tracking sprint.
- 1.6.2: Rendered active-position protection warnings for missing SL/TP without modifying trades.
- 1.6.1.2: Ignored missing active-position TP/SL in chart scaling and overlay rendering.
- 1.6.1.1: Preserved active-position chart overlay for startup lock initialization hotfix.
- 1.6.1: Added active MT5 position overlay and chart marking lock.
- 0.4.0: Added offline-safe candlestick renderer for the Sprint 4 embedded chart panel.
- 0.5.1: Added drag-to-pan, mouse-wheel zoom, double-click reset, and chart-position preservation during live refresh.
- 0.7.0: Added market structure marker and break-of-structure overlay rendering.
- 0.8.0: Added support/resistance zone overlay rendering.
- 0.9.0: Added persistent BOS rendering and liquidity overlay rendering with marker priority.
- 0.9.1: Rendered support/resistance and liquidity as candle-bounded segments instead of full-chart lines.
- 0.9.2: Added boxed fair value gap and order block rendering and simplified support/resistance labels to boxes only without price text.
- 0.9.3: Reduced overlay history to active items only and added combined support/resistance range boxing.
- 0.9.3.2: Added right-side future scrolling, coalesced chart redraws to reduce flicker, and tightened active S/R range box placement.
- 0.9.3.3: Added consolidation-only S/R box validation, overlay payload caching, and stronger unchanged-refresh flicker suppression.
- 0.9.3.4: Added close-based active range invalidation so broken S/R boxes are removed immediately.
- 0.9.3.5: Added true consolidation range filtering and double-buffer canvas rendering to reduce flicker.
- 0.9.3.6: Added rendered-range status accuracy, render debounce, and mouse/scroll redraw coalescing.
- 0.9.3.7: Fixed double-buffer copy artifacts by swapping buffers in physical pixels with an identity screen transform.
- 0.9.3.8: Removed buffer-copy rendering and restored direct single-canvas atomic painting to eliminate rectangular repaint artifacts.
- 1.5.0: Preserved trade plan overlay rendering for Sprint 15 manual execution.
- 1.4.1: Preserved trade plan overlay rendering for polished review-modal patch.
- 1.4.0: Added BUY_READY / SELL_READY trade plan overlay lines for Entry, SL, TP, and RR.
*/

(function () {
  "use strict";

  const canvas = document.getElementById("chart-canvas");
  const overlay = document.getElementById("status-overlay");
  const context = canvas.getContext("2d", { alpha: false });

  const MIN_VISIBLE_CANDLES = 20;
  const MAX_VISIBLE_CANDLES = 500;
  const MIN_ZOOM_SCALE = 0.60;
  const MAX_ZOOM_SCALE = 3.50;
  const MAX_FUTURE_EMPTY_SLOTS = 120;
  const ACTIVE_RANGE_MAX_CANDLES = 28;
  const ACTIVE_RANGE_MIN_CANDLES = 10;
  const ACTIVE_RANGE_MIN_TOUCHES = 2;

  const state = {
    candles: [],
    metadata: { symbol: "-", timeframe: "-", candleCount: 0, latestClose: null, latestTime: "-" },
    crosshair: null,
    structure: {
      markers: [],
      breaks: [],
      metadata: { bias: "-", summary: "", latestBreak: null },
    },
    supportResistance: {
      zones: [],
      metadata: { summary: "", nearestSupport: null, nearestResistance: null },
      renderedActiveRange: false,
      renderedRangeRejected: false,
    },
    liquidity: {
      pools: [],
      sweeps: [],
      metadata: { summary: "" },
    },
    imbalance: {
      fairValueGaps: [],
      orderBlocks: [],
      metadata: { summary: "" },
    },
    tradePlan: {
      plan: null,
      metadata: { direction: "WAIT", summary: "" },
    },
    activePosition: {
      position: null,
      metadata: { direction: "NONE", summary: "", locked: false },
    },
    view: { offsetFromRight: 0, zoomScale: 1, manualNavigation: false },
    drag: { active: false, startX: 0, startOffsetFromRight: 0, moved: false },
  };

  let renderPending = false;
  let renderDebounceTimer = null;
  let latestStatusText = "";
  let lastCandleSignature = "";
  let lastStructureSignature = "";
  let lastSupportResistanceSignature = "";
  let lastLiquiditySignature = "";
  let lastImbalanceSignature = "";
  let lastTradePlanSignature = "";
  let lastActivePositionSignature = "";
  let lastRenderTimestamp = 0;

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
    requestRender();
  }

  function setStatus(message) {
    const nextStatus = String(message || "Sentinel AI chart ready.");
    if (nextStatus === latestStatusText) {
      return;
    }
    latestStatusText = nextStatus;
    overlay.textContent = nextStatus;
  }

  function setCandles(candles, metadata) {
    const normalizedCandles = Array.isArray(candles) ? candles : [];
    const previousSymbol = state.metadata.symbol;
    const previousTimeframe = state.metadata.timeframe;
    const nextMetadata = Object.assign({}, state.metadata, metadata || {});
    const marketContextChanged = previousSymbol !== nextMetadata.symbol || previousTimeframe !== nextMetadata.timeframe;
    const nextCandles = normalizedCandles.filter(isValidCandle);
    const nextSignature = candleSignature(nextCandles, nextMetadata);

    if (!marketContextChanged && nextSignature === lastCandleSignature) {
      return;
    }

    state.candles = nextCandles;
    state.metadata = Object.assign({}, nextMetadata, { candleCount: state.candles.length });
    lastCandleSignature = nextSignature;
    if (marketContextChanged) {
      lastStructureSignature = "";
      lastSupportResistanceSignature = "";
      lastLiquiditySignature = "";
      lastImbalanceSignature = "";
      lastTradePlanSignature = "";
      lastActivePositionSignature = "";
      state.tradePlan.plan = null;
      state.tradePlan.metadata = { direction: "WAIT", summary: "" };
      state.activePosition.position = null;
      state.activePosition.metadata = { direction: "NONE", summary: "", locked: false };
      resetViewToLatest(false);
    } else {
      clampViewState(createLayout(Math.max(canvas.clientWidth, 1), Math.max(canvas.clientHeight, 1)));
    }
    requestRender();
  }

  function setMarketStructure(markers, metadata) {
    const normalizedMarkers = Array.isArray(markers) ? markers : [];
    const nextMetadata = Object.assign({}, state.structure.metadata, metadata || {});
    const normalizedBreaks = Array.isArray(nextMetadata.breaks) ? nextMetadata.breaks : [];
    const nextMarkers = normalizedMarkers.filter(isValidStructureMarker);
    const nextBreaks = normalizedBreaks.filter(isValidStructureBreak);
    const nextSignature = stableSignature({ markers: nextMarkers, breaks: nextBreaks, bias: nextMetadata.bias, latestBreak: nextMetadata.latestBreak });
    if (nextSignature === lastStructureSignature) {
      return;
    }
    state.structure.markers = nextMarkers;
    state.structure.breaks = nextBreaks;
    state.structure.metadata = nextMetadata;
    lastStructureSignature = nextSignature;
    requestRender();
  }

  function setSupportResistance(zones, metadata) {
    const normalizedZones = Array.isArray(zones) ? zones : [];
    const nextZones = normalizedZones.filter(isValidSupportResistanceZone);
    const nextMetadata = Object.assign({}, state.supportResistance.metadata, metadata || {});
    const nextSignature = stableSignature({ zones: nextZones, activeRange: nextMetadata.activeRange });
    if (nextSignature === lastSupportResistanceSignature) {
      return;
    }
    state.supportResistance.zones = nextZones;
    state.supportResistance.metadata = nextMetadata;
    lastSupportResistanceSignature = nextSignature;
    requestRender();
  }

  function setLiquidity(pools, sweeps, metadata) {
    const normalizedPools = Array.isArray(pools) ? pools : [];
    const normalizedSweeps = Array.isArray(sweeps) ? sweeps : [];
    const nextPools = normalizedPools.filter(isValidLiquidityPool);
    const nextSweeps = normalizedSweeps.filter(isValidLiquiditySweep);
    const nextMetadata = Object.assign({}, state.liquidity.metadata, metadata || {});
    const nextSignature = stableSignature({ pools: nextPools, sweeps: nextSweeps });
    if (nextSignature === lastLiquiditySignature) {
      return;
    }
    state.liquidity.pools = nextPools;
    state.liquidity.sweeps = nextSweeps;
    state.liquidity.metadata = nextMetadata;
    lastLiquiditySignature = nextSignature;
    requestRender();
  }

  function setImbalance(fairValueGaps, orderBlocks, metadata) {
    const normalizedFvg = Array.isArray(fairValueGaps) ? fairValueGaps : [];
    const normalizedOb = Array.isArray(orderBlocks) ? orderBlocks : [];
    const nextFairValueGaps = normalizedFvg.filter(isValidImbalanceZone);
    const nextOrderBlocks = normalizedOb.filter(isValidImbalanceZone);
    const nextMetadata = Object.assign({}, state.imbalance.metadata, metadata || {});
    const nextSignature = stableSignature({ fairValueGaps: nextFairValueGaps, orderBlocks: nextOrderBlocks });
    if (nextSignature === lastImbalanceSignature) {
      return;
    }
    state.imbalance.fairValueGaps = nextFairValueGaps;
    state.imbalance.orderBlocks = nextOrderBlocks;
    state.imbalance.metadata = nextMetadata;
    lastImbalanceSignature = nextSignature;
    requestRender();
  }

  function setTradePlan(plan, metadata) {
    const nextPlan = isValidTradePlan(plan) ? plan : null;
    const nextMetadata = Object.assign({}, state.tradePlan.metadata, metadata || {});
    const nextSignature = stableSignature({ plan: nextPlan, metadata: nextMetadata });
    if (nextSignature === lastTradePlanSignature) {
      return;
    }
    state.tradePlan.plan = nextPlan;
    state.tradePlan.metadata = nextMetadata;
    lastTradePlanSignature = nextSignature;
    requestRender();
  }

  function setActivePosition(position, metadata) {
    const nextPosition = isValidActivePosition(position) ? position : null;
    const nextMetadata = Object.assign({}, state.activePosition.metadata, metadata || {});
    const nextSignature = stableSignature({ position: nextPosition, metadata: nextMetadata });
    if (nextSignature === lastActivePositionSignature) {
      return;
    }
    state.activePosition.position = nextPosition;
    state.activePosition.metadata = nextMetadata;
    lastActivePositionSignature = nextSignature;
    requestRender();
  }

  function candleSignature(candles, metadata) {
    if (!Array.isArray(candles) || candles.length === 0) {
      return stableSignature({ symbol: metadata.symbol, timeframe: metadata.timeframe, count: 0 });
    }
    const latest = candles[candles.length - 1];
    const previous = candles.length > 1 ? candles[candles.length - 2] : latest;
    return stableSignature({
      symbol: metadata.symbol,
      timeframe: metadata.timeframe,
      count: candles.length,
      previousTime: previous.time,
      latestTime: latest.time,
      latestOpen: Number(latest.open).toFixed(5),
      latestHigh: Number(latest.high).toFixed(5),
      latestLow: Number(latest.low).toFixed(5),
      latestClose: Number(latest.close).toFixed(5),
    });
  }

  function stableSignature(payload) {
    return JSON.stringify(payload);
  }

  function isValidSupportResistanceZone(zone) {
    return zone && Number.isFinite(Number(zone.lowerPrice)) && Number.isFinite(Number(zone.upperPrice)) &&
      Number(zone.upperPrice) >= Number(zone.lowerPrice) && Number.isFinite(Number(zone.startTime)) &&
      Number.isFinite(Number(zone.endTime)) && (zone.kind === "SUPPORT" || zone.kind === "RESISTANCE");
  }
  function isValidStructureMarker(marker) {
    return marker && Number.isFinite(Number(marker.time)) && Number.isFinite(Number(marker.price)) &&
      (marker.kind === "HIGH" || marker.kind === "LOW");
  }
  function isValidStructureBreak(item) {
    return item && Number.isFinite(Number(item.time)) && Number.isFinite(Number(item.price)) &&
      (item.direction === "BULLISH" || item.direction === "BEARISH");
  }
  function isValidLiquidityPool(pool) {
    return pool && Number.isFinite(Number(pool.time)) && Number.isFinite(Number(pool.endTime)) &&
      Number.isFinite(Number(pool.price)) && (pool.side === "BUY_SIDE" || pool.side === "SELL_SIDE");
  }
  function isValidLiquiditySweep(sweep) {
    return sweep && Number.isFinite(Number(sweep.time)) && Number.isFinite(Number(sweep.wickPrice)) &&
      (sweep.direction === "BULLISH" || sweep.direction === "BEARISH");
  }
  function isValidImbalanceZone(zone) {
    return zone && Number.isFinite(Number(zone.lowerPrice)) && Number.isFinite(Number(zone.upperPrice)) &&
      Number(zone.upperPrice) >= Number(zone.lowerPrice) && Number.isFinite(Number(zone.startTime)) &&
      Number.isFinite(Number(zone.endTime)) && (zone.direction === "BULLISH" || zone.direction === "BEARISH");
  }
  function isValidTradePlan(plan) {
    return plan && (plan.direction === "BUY_READY" || plan.direction === "SELL_READY") &&
      Number.isFinite(Number(plan.entryPrice)) && Number.isFinite(Number(plan.stopLoss)) &&
      Number.isFinite(Number(plan.takeProfit)) && Number.isFinite(Number(plan.riskRewardRatio));
  }
  function isValidActivePosition(position) {
    return position && (position.direction === "BUY" || position.direction === "SELL") &&
      isUsablePrice(position.entryPrice) &&
      (position.stopLoss === null || position.stopLoss === undefined || isUsablePrice(position.stopLoss)) &&
      (position.takeProfit === null || position.takeProfit === undefined || isUsablePrice(position.takeProfit));
  }

  function isUsablePrice(price) {
    return Number.isFinite(Number(price)) && Number(price) > 0;
  }
  function isValidCandle(candle) {
    return candle && Number.isFinite(Number(candle.time)) && Number.isFinite(Number(candle.open)) &&
      Number.isFinite(Number(candle.high)) && Number.isFinite(Number(candle.low)) && Number.isFinite(Number(candle.close));
  }

  function requestRender() {
    if (renderDebounceTimer !== null || renderPending) {
      return;
    }
    renderDebounceTimer = window.setTimeout(function () {
      renderDebounceTimer = null;
      if (renderPending) {
        return;
      }
      renderPending = true;
      window.requestAnimationFrame(function (timestamp) {
        const renderDelay = Math.max(0, 140 - (timestamp - lastRenderTimestamp));
        if (renderDelay > 0) {
          window.setTimeout(function () {
            window.requestAnimationFrame(function (nextTimestamp) {
              renderPending = false;
              lastRenderTimestamp = nextTimestamp;
              renderChart();
            });
          }, renderDelay);
          return;
        }
        renderPending = false;
        lastRenderTimestamp = timestamp;
        renderChart();
      });
    }, 55);
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
    drawSupportResistanceZones(layout, visibleRange, priceRange);
    drawImbalanceZones(layout, visibleRange, priceRange);
    drawCandles(layout, visibleRange, priceRange);
    drawStructureMarkers(layout, visibleRange, priceRange);
    drawStructureBreakMarkers(layout, visibleRange, priceRange);
    drawLiquidityOverlays(layout, visibleRange, priceRange);
    drawAxes(layout, visibleRange);
    drawLatestPriceLine(layout, visibleCandles, priceRange);
    drawActivePositionOrTradePlanOverlay(layout, priceRange);
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
    const padding = { left: 18, right: 84, top: 30, bottom: 36 };
    const plotWidth = Math.max(width - padding.left - padding.right, 20);
    const plotHeight = Math.max(height - padding.top - padding.bottom, 20);
    const baseSlotWidth = 10;
    const slotWidth = Math.max(4, baseSlotWidth * state.view.zoomScale);
    const candleWidth = Math.max(2.5, Math.min(slotWidth * 0.70, 14));
    const candleGap = Math.max(slotWidth - candleWidth, 1);
    const visibleCapacity = Math.max(MIN_VISIBLE_CANDLES, Math.min(MAX_VISIBLE_CANDLES, Math.floor(plotWidth / slotWidth)));
    return {
      width, height, padding,
      plotLeft: padding.left,
      plotRight: width - padding.right,
      plotTop: padding.top,
      plotBottom: height - padding.bottom,
      plotWidth, plotHeight, candleWidth, candleGap, slotWidth, visibleCapacity,
    };
  }

  function resolveVisibleRange(layout) {
    const totalCandles = state.candles.length;
    const visibleCount = Math.min(layout.visibleCapacity, Math.max(totalCandles, MIN_VISIBLE_CANDLES));
    const futureSlots = Math.max(0, -state.view.offsetFromRight);
    const endIndexExclusive = Math.min(totalCandles + futureSlots, totalCandles + MAX_FUTURE_EMPTY_SLOTS);
    const startIndex = Math.max(0, endIndexExclusive - visibleCount);
    const realStartIndex = Math.min(totalCandles, startIndex);
    const realEndIndexExclusive = Math.min(totalCandles, endIndexExclusive);
    return {
      candles: state.candles.slice(realStartIndex, realEndIndexExclusive),
      startIndex,
      realStartIndex,
      realEndIndexExclusive,
      endIndexExclusive: startIndex + visibleCount,
      visibleCount,
      futureSlots: Math.max(0, endIndexExclusive - totalCandles),
    };
  }

  function clampViewState(layout) {
    state.view.zoomScale = clamp(state.view.zoomScale, MIN_ZOOM_SCALE, MAX_ZOOM_SCALE);
    const visibleCount = Math.min(layout.visibleCapacity, Math.max(state.candles.length, MIN_VISIBLE_CANDLES));
    const maxOffsetFromRight = Math.max(0, state.candles.length - visibleCount);
    const maxFutureOffset = Math.min(MAX_FUTURE_EMPTY_SLOTS, Math.max(10, Math.floor(visibleCount * 0.65)));
    state.view.offsetFromRight = Math.round(clamp(state.view.offsetFromRight, -maxFutureOffset, maxOffsetFromRight));
    state.view.manualNavigation = state.view.offsetFromRight !== 0;
  }

  function resolvePriceRange(candles) {
    let minPrice = Number.POSITIVE_INFINITY;
    let maxPrice = Number.NEGATIVE_INFINITY;
    candles.forEach((candle) => {
      minPrice = Math.min(minPrice, Number(candle.low));
      maxPrice = Math.max(maxPrice, Number(candle.high));
    });
    const activePosition = state.activePosition.position;
    if (isValidActivePosition(activePosition)) {
      const activePrices = [activePosition.entryPrice, activePosition.stopLoss, activePosition.takeProfit].filter(isUsablePrice).map(Number);
      activePrices.forEach((price) => {
        minPrice = Math.min(minPrice, price);
        maxPrice = Math.max(maxPrice, price);
      });
    } else {
      const tradePlan = state.tradePlan.plan;
      if (isValidTradePlan(tradePlan)) {
        minPrice = Math.min(minPrice, Number(tradePlan.entryPrice), Number(tradePlan.stopLoss), Number(tradePlan.takeProfit));
        maxPrice = Math.max(maxPrice, Number(tradePlan.entryPrice), Number(tradePlan.stopLoss), Number(tradePlan.takeProfit));
      }
    }
    if (!Number.isFinite(minPrice) || !Number.isFinite(maxPrice)) {
      minPrice = 0; maxPrice = 1;
    }
    const rawRange = Math.max(maxPrice - minPrice, 0.0001);
    const padding = rawRange * 0.08;
    return { min: minPrice - padding, max: maxPrice + padding, range: rawRange + padding * 2 };
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

  function drawCandles(layout, visibleRange, priceRange) {
    const candles = visibleRange.candles;
    candles.forEach((candle, index) => {
      const open = Number(candle.open);
      const high = Number(candle.high);
      const low = Number(candle.low);
      const close = Number(candle.close);
      const visibleIndex = visibleRange.realStartIndex - visibleRange.startIndex + index;
      const x = xForIndex(layout, visibleIndex, visibleRange.visibleCount);
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

  function drawSupportResistanceZones(layout, visibleRange, priceRange) {
    state.supportResistance.renderedActiveRange = false;
    state.supportResistance.renderedRangeRejected = false;
    const activeRange = state.supportResistance.metadata ? state.supportResistance.metadata.activeRange : null;
    if (activeRange) {
      const rendered = drawCombinedSupportResistanceRange(layout, visibleRange, priceRange, activeRange);
      state.supportResistance.renderedActiveRange = rendered;
      state.supportResistance.renderedRangeRejected = !rendered;
      return;
    }
    if (!state.supportResistance.zones || state.supportResistance.zones.length === 0) { return; }
    context.save();
    context.font = "bold 12px Segoe UI, Arial";
    context.textAlign = "center";
    state.supportResistance.zones.forEach((zone) => {
      const lower = Number(zone.lowerPrice);
      const upper = Number(zone.upperPrice);
      const segment = resolveSegmentXRange(layout, visibleRange, Number(zone.startTime), Number(zone.endTime), 12);
      if (!Number.isFinite(lower) || !Number.isFinite(upper) || segment === null) { return; }
      const upperY = yForPrice(layout, priceRange, upper);
      const lowerY = yForPrice(layout, priceRange, lower);
      const top = Math.max(layout.plotTop, Math.min(upperY, lowerY));
      const bottom = Math.min(layout.plotBottom, Math.max(upperY, lowerY));
      if (bottom < layout.plotTop || top > layout.plotBottom) { return; }
      const segmentWidth = Math.max(segment.endX - segment.startX, layout.slotWidth * 3);
      context.strokeStyle = "rgba(229, 73, 93, 0.90)";
      context.lineWidth = 1.8;
      context.strokeRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
      context.fillStyle = "rgba(229, 73, 93, 0.10)";
      context.fillRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
      const labelText = zone.kind === "SUPPORT" ? "S" : "R";
      const labelY = zone.kind === "SUPPORT" ? bottom + 16 : top - 8;
      context.fillStyle = "rgba(135, 255, 135, 0.95)";
      context.fillText(labelText, segment.startX + segmentWidth / 2, labelY);
    });
    context.restore();
  }

  function drawCombinedSupportResistanceRange(layout, visibleRange, priceRange, activeRange) {
    const topPrice = Number(activeRange.upperPrice);
    const bottomPrice = Number(activeRange.lowerPrice);
    if (!Number.isFinite(topPrice) || !Number.isFinite(bottomPrice) || topPrice <= bottomPrice) { return false; }
    const refinedRange = resolveActiveRangeBox(activeRange, bottomPrice, topPrice);
    if (refinedRange === null) { return false; }
    const segment = resolveSegmentXRange(layout, visibleRange, refinedRange.startTime, refinedRange.endTime, 16);
    if (segment === null) { return false; }
    const topY = yForPrice(layout, priceRange, refinedRange.upperPrice);
    const bottomY = yForPrice(layout, priceRange, refinedRange.lowerPrice);
    const top = Math.max(layout.plotTop, Math.min(topY, bottomY));
    const bottom = Math.min(layout.plotBottom, Math.max(topY, bottomY));
    if (bottom < layout.plotTop || top > layout.plotBottom) { return false; }
    const segmentWidth = Math.max(segment.endX - segment.startX, layout.slotWidth * 6);
    context.save();
    context.strokeStyle = "rgba(229, 73, 93, 0.96)";
    context.lineWidth = 2.2;
    context.strokeRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
    context.fillStyle = "rgba(229, 73, 93, 0.08)";
    context.fillRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
    context.fillStyle = "rgba(135, 255, 135, 0.98)";
    context.font = "bold 16px Segoe UI, Arial";
    context.textAlign = "center";
    context.fillText(String(activeRange.resistanceLabel || "R"), segment.startX + segmentWidth / 2, Math.max(layout.plotTop + 18, top - 10));
    context.fillText(String(activeRange.supportLabel || "S"), segment.startX + segmentWidth / 2, Math.min(layout.plotBottom - 6, bottom + 22));
    context.restore();
    return true;
  }

  function resolveActiveRangeBox(activeRange, fallbackLowerPrice, fallbackUpperPrice) {
    if (state.candles.length < ACTIVE_RANGE_MIN_CANDLES + 1) {
      return null;
    }

    const latestIndex = state.candles.length - 1;
    const latestCandle = state.candles[latestIndex];
    const latestTime = Number(latestCandle.time);
    const latestClose = Number(latestCandle.close);
    const rangeEndIndex = latestIndex - 1;
    const hardStartLimit = Math.max(0, rangeEndIndex - ACTIVE_RANGE_MAX_CANDLES + 1);
    let bestCandidate = null;

    for (let startIndex = rangeEndIndex - ACTIVE_RANGE_MIN_CANDLES + 1; startIndex >= hardStartLimit; startIndex -= 1) {
      const candidateCandles = state.candles.slice(startIndex, rangeEndIndex + 1);
      const assessment = assessConsolidationCandidate(candidateCandles);
      if (assessment.valid) {
        const score = scoreConsolidationCandidate(assessment, rangeEndIndex - startIndex + 1);
        if (bestCandidate === null || score > bestCandidate.score) {
          bestCandidate = {
            startIndex,
            endIndex: rangeEndIndex,
            lowerPrice: assessment.lowerPrice,
            upperPrice: assessment.upperPrice,
            averageRange: assessment.averageRange,
            candleCount: rangeEndIndex - startIndex + 1,
            score,
          };
        }
      } else if (bestCandidate !== null) {
        break;
      }
    }

    if (bestCandidate === null) {
      return null;
    }

    const invalidationBuffer = Math.max(bestCandidate.averageRange * 0.18, (bestCandidate.upperPrice - bestCandidate.lowerPrice) * 0.018);
    const closedBelowSupport = latestClose < bestCandidate.lowerPrice - invalidationBuffer;
    const closedAboveResistance = latestClose > bestCandidate.upperPrice + invalidationBuffer;
    if (closedBelowSupport || closedAboveResistance) {
      return null;
    }

    return {
      startTime: Number(state.candles[bestCandidate.startIndex].time),
      endTime: latestTime,
      lowerPrice: bestCandidate.lowerPrice,
      upperPrice: bestCandidate.upperPrice,
    };
  }

  function assessConsolidationCandidate(candidateCandles) {
    if (!Array.isArray(candidateCandles) || candidateCandles.length < ACTIVE_RANGE_MIN_CANDLES) {
      return { valid: false };
    }

    const candidateHigh = Math.max(...candidateCandles.map((candle) => Number(candle.high)));
    const candidateLow = Math.min(...candidateCandles.map((candle) => Number(candle.low)));
    const candidateHeight = Math.max(candidateHigh - candidateLow, 0.0001);
    const averageRange = estimateAverageRange(candidateCandles);
    const maximumCandleRange = Math.max(...candidateCandles.map((candle) => Math.max(Number(candle.high) - Number(candle.low), 0.0001)));
    const maxAllowedHeight = averageRange * 5.8;
    const touchTolerance = Math.max(averageRange * 0.55, candidateHeight * 0.10);
    const resistanceTouches = countSeparatedTouches(candidateCandles, "HIGH", candidateHigh - touchTolerance, 2);
    const supportTouches = countSeparatedTouches(candidateCandles, "LOW", candidateLow + touchTolerance, 2);
    const directionalRatio = directionalBodyRatio(candidateCandles);
    const netMoveRatio = Math.abs(Number(candidateCandles[candidateCandles.length - 1].close) - Number(candidateCandles[0].open)) / candidateHeight;
    const impulseDominance = maximumCandleRange / candidateHeight;

    const valid = (
      candidateHeight <= maxAllowedHeight &&
      resistanceTouches >= ACTIVE_RANGE_MIN_TOUCHES &&
      supportTouches >= ACTIVE_RANGE_MIN_TOUCHES &&
      directionalRatio <= 0.55 &&
      netMoveRatio <= 0.62 &&
      impulseDominance <= 0.58
    );

    return {
      valid,
      lowerPrice: candidateLow,
      upperPrice: candidateHigh,
      averageRange,
      height: candidateHeight,
      resistanceTouches,
      supportTouches,
      directionalRatio,
      netMoveRatio,
      impulseDominance,
    };
  }

  function scoreConsolidationCandidate(assessment, candleCount) {
    const touchScore = (assessment.resistanceTouches + assessment.supportTouches) * 10;
    const compactnessScore = Math.max(0, 18 - (assessment.height / assessment.averageRange));
    const stabilityScore = Math.max(0, 12 - assessment.directionalRatio * 12);
    const lengthPenalty = Math.max(0, candleCount - 18) * 0.5;
    return touchScore + compactnessScore + stabilityScore - lengthPenalty;
  }

  function countSeparatedTouches(candles, side, threshold, minimumGap) {
    let touches = 0;
    let lastTouchIndex = -minimumGap - 1;
    candles.forEach((candle, index) => {
      const touched = side === "HIGH" ? Number(candle.high) >= threshold : Number(candle.low) <= threshold;
      if (touched && index - lastTouchIndex >= minimumGap) {
        touches += 1;
        lastTouchIndex = index;
      }
    });
    return touches;
  }

  function estimateAverageRange(candles) {
    if (!Array.isArray(candles) || candles.length === 0) {
      return 0.0001;
    }
    const total = candles.reduce((sum, candle) => sum + Math.max(Number(candle.high) - Number(candle.low), 0.0001), 0);
    return Math.max(total / candles.length, 0.0001);
  }

  function directionalBodyRatio(candles) {
    if (!Array.isArray(candles) || candles.length === 0) {
      return 1;
    }
    const firstOpen = Number(candles[0].open);
    const latestClose = Number(candles[candles.length - 1].close);
    const directionalMove = Math.abs(latestClose - firstOpen);
    const totalBody = candles.reduce((sum, candle) => sum + Math.abs(Number(candle.close) - Number(candle.open)), 0);
    if (totalBody <= 0) {
      return 0;
    }
    return directionalMove / totalBody;
  }

  function drawImbalanceZones(layout, visibleRange, priceRange) {
    drawFairValueGapZones(layout, visibleRange, priceRange);
    drawOrderBlockZones(layout, visibleRange, priceRange);
  }

  function drawFairValueGapZones(layout, visibleRange, priceRange) {
    if (!state.imbalance.fairValueGaps || state.imbalance.fairValueGaps.length === 0) { return; }
    context.save();
    context.font = "bold 10px Segoe UI, Arial";
    context.textAlign = "left";
    state.imbalance.fairValueGaps.forEach((zone) => {
      const segment = resolveSegmentXRange(layout, visibleRange, Number(zone.startTime), Number(zone.endTime), 6);
      if (segment === null) { return; }
      drawBoxZone(layout, priceRange, segment, zone, {
        bullishFill: zone.filled ? "rgba(32, 201, 151, 0.05)" : (zone.partiallyMitigated ? "rgba(32, 201, 151, 0.11)" : "rgba(32, 201, 151, 0.18)"),
        bearishFill: zone.filled ? "rgba(240, 82, 107, 0.05)" : (zone.partiallyMitigated ? "rgba(240, 82, 107, 0.11)" : "rgba(240, 82, 107, 0.18)"),
        bullishStroke: "rgba(32, 201, 151, 0.82)",
        bearishStroke: "rgba(240, 82, 107, 0.82)",
        labelPrefix: "FVG",
      });
    });
    context.restore();
  }

  function drawOrderBlockZones(layout, visibleRange, priceRange) {
    if (!state.imbalance.orderBlocks || state.imbalance.orderBlocks.length === 0) { return; }
    context.save();
    context.font = "bold 10px Segoe UI, Arial";
    context.textAlign = "left";
    state.imbalance.orderBlocks.forEach((zone) => {
      const segment = resolveSegmentXRange(layout, visibleRange, Number(zone.startTime), Number(zone.endTime), 6);
      if (segment === null) { return; }
      drawBoxZone(layout, priceRange, segment, zone, {
        bullishFill: zone.invalidated ? "rgba(94, 215, 255, 0.05)" : (zone.mitigated ? "rgba(94, 215, 255, 0.11)" : "rgba(94, 215, 255, 0.18)"),
        bearishFill: zone.invalidated ? "rgba(255, 206, 92, 0.05)" : (zone.mitigated ? "rgba(255, 206, 92, 0.11)" : "rgba(255, 206, 92, 0.18)"),
        bullishStroke: "rgba(94, 215, 255, 0.86)",
        bearishStroke: "rgba(255, 206, 92, 0.86)",
        labelPrefix: "OB",
      });
    });
    context.restore();
  }

  function drawBoxZone(layout, priceRange, segment, zone, palette) {
    const lower = Number(zone.lowerPrice);
    const upper = Number(zone.upperPrice);
    const upperY = yForPrice(layout, priceRange, upper);
    const lowerY = yForPrice(layout, priceRange, lower);
    const top = Math.max(layout.plotTop, Math.min(upperY, lowerY));
    const bottom = Math.min(layout.plotBottom, Math.max(upperY, lowerY));
    if (bottom < layout.plotTop || top > layout.plotBottom) { return; }
    const segmentWidth = Math.max(segment.endX - segment.startX, layout.slotWidth * 2);
    const isBullish = zone.direction === "BULLISH";
    const fillColor = isBullish ? palette.bullishFill : palette.bearishFill;
    const strokeColor = isBullish ? palette.bullishStroke : palette.bearishStroke;
    const suffix = isBullish ? "↑" : "↓";
    context.fillStyle = fillColor;
    context.fillRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
    context.strokeStyle = strokeColor;
    context.lineWidth = 1.2;
    context.strokeRect(segment.startX, top, segmentWidth, Math.max(bottom - top, 2));
    context.fillStyle = strokeColor;
    context.fillText(`${palette.labelPrefix}${suffix}`, segment.startX + 5, Math.max(layout.plotTop + 12, top + 13));
  }

  function drawStructureMarkers(layout, visibleRange, priceRange) {
    if (!state.structure.markers || state.structure.markers.length === 0) { return; }
    const visibleTimeToIndex = createVisibleTimeIndex(visibleRange);
    context.save();
    context.font = "bold 10px Segoe UI, Arial";
    context.textAlign = "center";
    state.structure.markers.forEach((marker) => {
      const visibleIndex = visibleTimeToIndex.get(Number(marker.time));
      if (visibleIndex === undefined) { return; }
      const x = xForIndex(layout, visibleIndex, visibleRange.visibleCount);
      const y = yForPrice(layout, priceRange, Number(marker.price));
      const isHigh = marker.kind === "HIGH";
      const markerY = isHigh ? y - 13 : y + 13;
      const labelY = isHigh ? y - 20 : y + 29;
      const fillColor = isHigh ? "#ffce5c" : "#5ed7ff";
      context.fillStyle = fillColor;
      context.beginPath();
      if (isHigh) {
        context.moveTo(x, markerY); context.lineTo(x - 5, markerY - 8); context.lineTo(x + 5, markerY - 8);
      } else {
        context.moveTo(x, markerY); context.lineTo(x - 5, markerY + 8); context.lineTo(x + 5, markerY + 8);
      }
      context.closePath();
      context.fill();
      context.fillText(String(marker.label || (isHigh ? "SH" : "SL")), x, labelY);
    });
    context.restore();
  }

  function drawStructureBreakMarkers(layout, visibleRange, priceRange) {
    if (!state.structure.breaks || state.structure.breaks.length === 0) { return; }
    const visibleTimeToIndex = createVisibleTimeIndex(visibleRange);
    context.save();
    context.font = "bold 12px Segoe UI, Arial";
    context.textAlign = "center";
    state.structure.breaks.forEach((breakItem) => {
      const breakIndex = visibleTimeToIndex.get(Number(breakItem.time));
      if (breakIndex === undefined) { return; }
      const x = xForIndex(layout, breakIndex, visibleRange.visibleCount);
      const y = yForPrice(layout, priceRange, Number(breakItem.price));
      const isBullish = breakItem.direction === "BULLISH";
      const isCoc = breakItem.eventType === "COC";
      const fillColor = isBullish ? (isCoc ? "#7ce3ff" : "#20c997") : (isCoc ? "#ffd37e" : "#f0526b");
      context.fillStyle = "rgba(2, 12, 16, 0.88)";
      context.fillRect(x - 29, y - 14, 58, 23);
      context.strokeStyle = fillColor;
      context.lineWidth = 1.5;
      context.strokeRect(x - 29, y - 14, 58, 23);
      context.fillStyle = fillColor;
      context.fillText(String(breakItem.label || (isBullish ? "BOS↑" : "BOS↓")), x, y + 2);
    });
    context.restore();
  }

  function drawLiquidityOverlays(layout, visibleRange, priceRange) {
    drawLiquidityPools(layout, visibleRange, priceRange);
    drawLiquiditySweeps(layout, visibleRange, priceRange);
  }

  function drawLiquidityPools(layout, visibleRange, priceRange) {
    if (!state.liquidity.pools || state.liquidity.pools.length === 0) { return; }
    context.save();
    context.font = "bold 10px Segoe UI, Arial";
    context.textAlign = "left";
    state.liquidity.pools.forEach((pool) => {
      const price = Number(pool.price);
      const segment = resolveSegmentXRange(layout, visibleRange, Number(pool.time), Number(pool.endTime), 8);
      if (!Number.isFinite(price) || segment === null) { return; }
      const y = yForPrice(layout, priceRange, price);
      if (y < layout.plotTop || y > layout.plotBottom) { return; }
      const isBuySide = pool.side === "BUY_SIDE";
      const lineColor = pool.inducementCandidate ? "rgba(255, 219, 112, 0.90)" : (isBuySide ? "rgba(255, 206, 92, 0.58)" : "rgba(94, 215, 255, 0.58)");
      const label = String(pool.label || (isBuySide ? "BSL" : "SSL"));
      context.strokeStyle = lineColor;
      context.setLineDash(pool.swept ? [2, 6] : [3, 5]);
      context.lineWidth = pool.inducementCandidate ? 1.5 : 1;
      context.beginPath();
      context.moveTo(segment.startX, Math.round(y) + 0.5);
      context.lineTo(segment.endX, Math.round(y) + 0.5);
      context.stroke();
      context.setLineDash([]);
      context.fillStyle = lineColor;
      context.fillText(`${label} ${formatPrice(price)}`, segment.startX + 5, y - 5);
    });
    context.restore();
  }

  function drawLiquiditySweeps(layout, visibleRange, priceRange) {
    if (!state.liquidity.sweeps || state.liquidity.sweeps.length === 0) { return; }
    const visibleTimeToIndex = createVisibleTimeIndex(visibleRange);
    context.save();
    context.font = "bold 11px Segoe UI, Arial";
    context.textAlign = "center";
    state.liquidity.sweeps.forEach((sweep) => {
      const visibleIndex = visibleTimeToIndex.get(Number(sweep.time));
      if (visibleIndex === undefined) { return; }
      const isBullish = sweep.direction === "BULLISH";
      const x = xForIndex(layout, visibleIndex, visibleRange.visibleCount);
      const y = yForPrice(layout, priceRange, Number(sweep.wickPrice));
      const label = isBullish ? "LQ↑" : "LQ↓";
      const fillColor = isBullish ? "#5ed7ff" : "#ffce5c";
      const labelY = isBullish ? y + 26 : y - 22;
      context.fillStyle = "rgba(2, 12, 16, 0.90)";
      context.fillRect(x - 18, labelY - 14, 36, 18);
      context.strokeStyle = fillColor;
      context.lineWidth = 1.3;
      context.strokeRect(x - 18, labelY - 14, 36, 18);
      context.fillStyle = fillColor;
      context.fillText(label, x, labelY);
    });
    context.restore();
  }

  function resolveSegmentXRange(layout, visibleRange, startTime, endTime, minimumSlots) {
    if (!Number.isFinite(startTime) || !Number.isFinite(endTime) || visibleRange.candles.length === 0) { return null; }
    const totalCandles = state.candles.length;
    let startIndex = absoluteIndexForTime(Math.min(startTime, endTime));
    let endIndex = absoluteIndexForTime(Math.max(startTime, endTime));
    if (startIndex === -1 || endIndex === -1) { return null; }
    const minimumWidth = Math.max(1, Number(minimumSlots || 1)) * layout.slotWidth;
    if (startIndex === endIndex) {
      endIndex = Math.min(totalCandles - 1, startIndex + Math.max(1, Number(minimumSlots || 1)));
    }
    if (endIndex < visibleRange.startIndex || startIndex >= visibleRange.endIndexExclusive) { return null; }
    const clampedStartIndex = Math.max(startIndex, visibleRange.startIndex);
    const clampedEndIndex = Math.min(endIndex, visibleRange.endIndexExclusive - 1);
    const visibleStartIndex = clampedStartIndex - visibleRange.startIndex;
    const visibleEndIndex = clampedEndIndex - visibleRange.startIndex;
    let startX = xForIndex(layout, visibleStartIndex, visibleRange.visibleCount) - layout.slotWidth / 2;
    let endX = xForIndex(layout, visibleEndIndex, visibleRange.visibleCount) + layout.slotWidth / 2;
    if (endX - startX < minimumWidth) {
      endX = Math.min(layout.plotRight, startX + minimumWidth);
      startX = Math.max(layout.plotLeft, Math.min(startX, endX - layout.slotWidth));
    }
    return { startX: clamp(startX, layout.plotLeft, layout.plotRight), endX: clamp(endX, layout.plotLeft, layout.plotRight) };
  }

  function absoluteIndexForTime(timestamp) {
    const target = Number(timestamp);
    if (!Number.isFinite(target)) { return -1; }
    let nearestIndex = -1;
    let nearestDistance = Number.POSITIVE_INFINITY;
    state.candles.forEach((candle, index) => {
      const distance = Math.abs(Number(candle.time) - target);
      if (distance < nearestDistance) { nearestDistance = distance; nearestIndex = index; }
    });
    return nearestIndex;
  }
  function createVisibleTimeIndex(visibleRange) {
    const visibleTimeToIndex = new Map();
    visibleRange.candles.forEach((candle, index) => {
      const visibleSlotIndex = visibleRange.realStartIndex - visibleRange.startIndex + index;
      visibleTimeToIndex.set(Number(candle.time), visibleSlotIndex);
    });
    return visibleTimeToIndex;
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
      if (!candle) { continue; }
      const visibleIndex = visibleRange.realStartIndex - visibleRange.startIndex + index;
      const x = xForIndex(layout, visibleIndex, visibleRange.visibleCount) - 22;
      context.fillText(formatTime(Number(candle.time)), x, layout.plotBottom + 20);
    }
    context.restore();
  }

  function drawLatestPriceLine(layout, candles, priceRange) {
    const latest = state.candles[state.candles.length - 1];
    if (!latest) { return; }
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

  function drawActivePositionOrTradePlanOverlay(layout, priceRange) {
    const position = state.activePosition.position;
    if (isValidActivePosition(position)) {
      drawActivePositionOverlay(layout, priceRange, position);
      return;
    }
    drawTradePlanOverlay(layout, priceRange);
  }

  function drawActivePositionOverlay(layout, priceRange, position) {
    const levels = [
      { key: "ACTIVE ENTRY", price: Number(position.entryPrice), color: "#d9f6ff", dash: [] },
      { key: "ACTIVE SL", price: isUsablePrice(position.stopLoss) ? Number(position.stopLoss) : null, color: "#ff5c7a", dash: [6, 4] },
      { key: "ACTIVE TP", price: isUsablePrice(position.takeProfit) ? Number(position.takeProfit) : null, color: "#20c997", dash: [3, 3] },
    ].filter((level) => Number.isFinite(Number(level.price)) && Number(level.price) > 0);
    context.save();
    context.font = "bold 11px Segoe UI, Arial";
    context.textAlign = "left";
    levels.forEach((level, index) => {
      const y = yForPrice(layout, priceRange, level.price);
      if (y < layout.plotTop - 18 || y > layout.plotBottom + 18) { return; }
      context.strokeStyle = level.color;
      context.lineWidth = level.key === "ACTIVE ENTRY" ? 1.9 : 1.3;
      context.setLineDash(level.dash);
      context.beginPath();
      context.moveTo(layout.plotLeft, Math.round(y) + 0.5);
      context.lineTo(layout.plotRight, Math.round(y) + 0.5);
      context.stroke();
      context.setLineDash([]);
      const labelText = `${level.key} ${formatPrice(level.price)}`;
      const labelWidth = Math.max(112, context.measureText(labelText).width + 12);
      const labelX = Math.max(layout.plotLeft + 6, layout.plotRight - labelWidth - 6);
      const labelY = y - 11 - index * 2;
      context.fillStyle = "rgba(2, 12, 16, 0.92)";
      context.fillRect(labelX, labelY, labelWidth, 20);
      context.strokeStyle = level.color;
      context.strokeRect(labelX, labelY, labelWidth, 20);
      context.fillStyle = level.color;
      context.fillText(labelText, labelX + 6, labelY + 14);
    });

    const direction = position.direction === "BUY" ? "BUY" : "SELL";
    const profit = Number.isFinite(Number(position.profit)) ? Number(position.profit).toFixed(2) : "0.00";
    const ticket = position.ticket ? String(position.ticket) : "-";
    const headerText = `ACTIVE ${direction} | P/L ${profit} | TICKET ${ticket}`;
    const protectionStatus = String(position.protectionStatus || "");
    const hasWarning = Boolean(position.missingStopLoss || position.missingTakeProfit);
    const headerWidth = Math.max(180, context.measureText(headerText).width + 14);
    context.fillStyle = "rgba(2, 12, 16, 0.94)";
    context.fillRect(layout.plotLeft + 10, layout.plotTop + 34, headerWidth, 24);
    context.strokeStyle = direction === "BUY" ? "#20c997" : "#ff5c7a";
    context.strokeRect(layout.plotLeft + 10, layout.plotTop + 34, headerWidth, 24);
    context.fillStyle = "#d9f6ff";
    context.fillText(headerText, layout.plotLeft + 17, layout.plotTop + 51);

    if (hasWarning) {
      const warningText = protectionStatus || "WARNING: Missing active position protection";
      const warningWidth = Math.max(190, context.measureText(warningText).width + 14);
      context.fillStyle = "rgba(2, 12, 16, 0.96)";
      context.fillRect(layout.plotLeft + 10, layout.plotTop + 64, warningWidth, 24);
      context.strokeStyle = "#ffcc66";
      context.strokeRect(layout.plotLeft + 10, layout.plotTop + 64, warningWidth, 24);
      context.fillStyle = "#ffcc66";
      context.fillText(warningText, layout.plotLeft + 17, layout.plotTop + 81);
    }
    context.restore();
  }

  function drawTradePlanOverlay(layout, priceRange) {
    const plan = state.tradePlan.plan;
    if (!isValidTradePlan(plan)) { return; }
    const levels = [
      { key: "ENTRY", price: Number(plan.entryPrice), color: "#d9f6ff", dash: [] },
      { key: "SL", price: Number(plan.stopLoss), color: "#ff5c7a", dash: [6, 4] },
      { key: "TP", price: Number(plan.takeProfit), color: "#20c997", dash: [3, 3] },
    ];
    context.save();
    context.font = "bold 11px Segoe UI, Arial";
    context.textAlign = "left";
    levels.forEach((level, index) => {
      const y = yForPrice(layout, priceRange, level.price);
      if (y < layout.plotTop - 18 || y > layout.plotBottom + 18) { return; }
      context.strokeStyle = level.color;
      context.lineWidth = level.key === "ENTRY" ? 1.6 : 1.2;
      context.setLineDash(level.dash);
      context.beginPath();
      context.moveTo(layout.plotLeft, Math.round(y) + 0.5);
      context.lineTo(layout.plotRight, Math.round(y) + 0.5);
      context.stroke();
      context.setLineDash([]);
      const labelText = `${level.key} ${formatPrice(level.price)}`;
      const labelWidth = Math.max(76, context.measureText(labelText).width + 12);
      const labelX = Math.max(layout.plotLeft + 6, layout.plotRight - labelWidth - 6);
      const labelY = y - 11 - index * 2;
      context.fillStyle = "rgba(2, 12, 16, 0.88)";
      context.fillRect(labelX, labelY, labelWidth, 20);
      context.strokeStyle = level.color;
      context.strokeRect(labelX, labelY, labelWidth, 20);
      context.fillStyle = level.color;
      context.fillText(labelText, labelX + 6, labelY + 14);
    });
    const rrText = `${plan.direction === "BUY_READY" ? "BUY" : "SELL"} READY | RR ${Number(plan.riskRewardRatio).toFixed(2)}`;
    const rrWidth = Math.max(118, context.measureText(rrText).width + 14);
    context.fillStyle = "rgba(2, 12, 16, 0.92)";
    context.fillRect(layout.plotLeft + 10, layout.plotTop + 34, rrWidth, 24);
    context.strokeStyle = plan.direction === "BUY_READY" ? "#20c997" : "#ff5c7a";
    context.strokeRect(layout.plotLeft + 10, layout.plotTop + 34, rrWidth, 24);
    context.fillStyle = "#d9f6ff";
    context.fillText(rrText, layout.plotLeft + 17, layout.plotTop + 51);
    context.restore();
  }

  function drawCrosshair(layout, visibleRange, priceRange) {
    if (state.crosshair === null || state.drag.active) { return; }
    const candles = visibleRange.candles;
    const x = state.crosshair.x;
    const y = state.crosshair.y;
    if (x < layout.plotLeft || x > layout.plotRight || y < layout.plotTop || y > layout.plotBottom) { return; }
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

    const rawSlotIndex = Math.round((x - (layout.plotRight - visibleRange.visibleCount * layout.slotWidth) - layout.slotWidth / 2) / layout.slotWidth);
    const slotIndex = Math.max(0, Math.min(visibleRange.visibleCount - 1, rawSlotIndex));
    const absoluteIndex = visibleRange.startIndex + slotIndex;
    const candleIndex = absoluteIndex - visibleRange.realStartIndex;
    const candle = candles[candleIndex];
    if (candle) {
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
    const hasActiveRange = !!state.supportResistance.renderedActiveRange;
    const srText = hasActiveRange ? " | Active range" : "";
    const sweepCount = state.liquidity.sweeps ? state.liquidity.sweeps.length : 0;
    const liquidityText = sweepCount > 0 ? ` | LQ sweeps: ${sweepCount}` : "";
    const fvgCount = state.imbalance.fairValueGaps ? state.imbalance.fairValueGaps.length : 0;
    const obCount = state.imbalance.orderBlocks ? state.imbalance.orderBlocks.length : 0;
    const imbalanceText = (fvgCount + obCount) > 0 ? ` | FVG: ${fvgCount} | OB: ${obCount}` : "";
    const activePosition = state.activePosition.position;
    const activeTradeText = isValidActivePosition(activePosition)
      ? ` | Active Trade: ${activePosition.direction} | Entry ${formatPrice(activePosition.entryPrice)} | SL ${isUsablePrice(activePosition.stopLoss) ? formatPrice(activePosition.stopLoss) : "Not Set"} | TP ${isUsablePrice(activePosition.takeProfit) ? formatPrice(activePosition.takeProfit) : "Not Set"} | P/L ${Number(activePosition.profit || 0).toFixed(2)}`
      : "";
    const tradePlanText = (!isValidActivePosition(activePosition) && isValidTradePlan(state.tradePlan.plan)) ? ` | Plan: ${state.tradePlan.plan.direction} RR ${Number(state.tradePlan.plan.riskRewardRatio).toFixed(2)}` : "";
    setStatus(`${symbol} ${timeframe} | ${visibleText} | Latest: ${latestClose} | ${latestTime}${bias}${srText}${liquidityText}${imbalanceText}${activeTradeText}${tradePlanText} | ${mode} | ${zoom}`);
  }

  function formatPrice(price) { const value = Number(price); return Number.isFinite(value) ? value.toFixed(2) : "-"; }
  function formatTime(timestampSeconds) { const date = new Date(timestampSeconds * 1000); return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }); }
  function formatDateTime(timestampSeconds) { const date = new Date(timestampSeconds * 1000); return date.toISOString().replace("T", " ").replace(".000Z", " UTC"); }

  function clamp(value, minimum, maximum) { return Math.min(Math.max(Number(value), minimum), maximum); }

  function resetViewToLatest(resetZoom) {
    state.view.offsetFromRight = 0;
    state.view.manualNavigation = false;
    if (resetZoom) { state.view.zoomScale = 1; }
  }

  function updateCanvasCursor() {
    if (state.drag.active) { canvas.style.cursor = "grabbing"; }
    else if (state.view.manualNavigation) { canvas.style.cursor = "grab"; }
    else { canvas.style.cursor = "crosshair"; }
  }

  canvas.addEventListener("mousedown", function (event) {
    if (event.button !== 0) { return; }
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
      if (Math.abs(deltaCandles) > 0) { state.drag.moved = true; }
      state.view.offsetFromRight = state.drag.startOffsetFromRight + deltaCandles;
      clampViewState(layout);
    }
    updateCanvasCursor();
    requestRender();
  });

  canvas.addEventListener("mouseup", function () { state.drag.active = false; updateCanvasCursor(); requestRender(); });
  canvas.addEventListener("mouseleave", function () { state.drag.active = false; state.crosshair = null; updateCanvasCursor(); requestRender(); });

  canvas.addEventListener("wheel", function (event) {
    event.preventDefault();
    if (state.candles.length === 0) { return; }
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
    requestRender();
  }, { passive: false });

  canvas.addEventListener("dblclick", function () { resetViewToLatest(true); updateCanvasCursor(); requestRender(); });
  window.addEventListener("mouseup", function () { if (state.drag.active) { state.drag.active = false; updateCanvasCursor(); requestRender(); } });
  window.addEventListener("resize", resizeCanvas);

  window.SentinelChart = {
    setCandles: setCandles,
    setMarketStructure: setMarketStructure,
    setSupportResistance: setSupportResistance,
    setLiquidity: setLiquidity,
    setImbalance: setImbalance,
    setTradePlan: setTradePlan,
    setActivePosition: setActivePosition,
    setStatus: setStatus,
    render: requestRender,
    resetViewToLatest: function () { resetViewToLatest(true); requestRender(); },
  };

  updateCanvasCursor();
  resizeCanvas();
  renderChart();
}());
