import { useState, useEffect, useRef } from "react";
import {
  createChart,
  ColorType,
  CrosshairMode,
  LineStyle,
} from "lightweight-charts";
import type { IChartApi, ISeriesApi } from "lightweight-charts";
import type { DataPoint } from "../types";

const PERIODS = ["1Y", "3Y", "5Y", "10Y", "Max"] as const;

function filterByPeriod(data: DataPoint[], period: string): DataPoint[] {
  if (period === "Max") return data;
  const years = { "1Y": 1, "3Y": 3, "5Y": 5, "10Y": 10 }[period] ?? 5;
  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - years);
  return data.filter((d) => new Date(d.date) >= cutoff);
}

export interface RecessionBand { start: string; end: string }

function toHistogramPoints(bands: RecessionBand[]): { time: string; value: number }[] {
  const points: { time: string; value: number }[] = [];
  for (const band of bands) {
    const cur = new Date(band.start + "T00:00:00Z");
    const end = new Date(band.end + "T00:00:00Z");
    while (cur <= end) {
      points.push({ time: cur.toISOString().slice(0, 10), value: 1 });
      cur.setUTCMonth(cur.getUTCMonth() + 1);
    }
  }
  return points.sort((a, b) => a.time.localeCompare(b.time));
}

interface Props {
  data: DataPoint[];
  title: string;
  unit: string;
  transform: string;
  color?: string;
  compact?: boolean;
  recessionBands?: RecessionBand[];
}

export default function IndicatorChart({
  data,
  title,
  unit,
  transform,
  color = "#3b82f6",
  compact,
  recessionBands,
}: Props) {
  const [period, setPeriod] = useState<string>("5Y");
  const containerRef   = useRef<HTMLDivElement>(null);
  const chartRef       = useRef<IChartApi | null>(null);
  const seriesRef      = useRef<ISeriesApi<"Area"> | null>(null);
  const recSeriesRef   = useRef<ISeriesApi<"Histogram"> | null>(null);
  const [crosshair, setCrosshair] = useState<{ value: number; date: string } | null>(null);

  const valid    = data.filter((d) => d.value != null);
  const filtered = filterByPeriod(valid, period);
  const isPercent = transform !== "level" || unit.toLowerCase().includes("percent");
  const latest   = filtered[filtered.length - 1];

  // ── Chart init: only when color or compact changes ─────────────────────────
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = createChart(el, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#555",
        fontFamily: "inherit",
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { color: "rgba(255,255,255,0.04)", style: LineStyle.Dotted },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          color: "rgba(255,255,255,0.15)",
          width: 1,
          style: LineStyle.Dashed,
          labelVisible: false,
        },
        horzLine: {
          color: "rgba(255,255,255,0.1)",
          width: 1,
          labelBackgroundColor: "#1a1a1a",
        },
      },
      rightPriceScale: {
        borderVisible: false,
        textColor: "#444",
        scaleMargins: { top: 0.12, bottom: 0.08 },
      },
      timeScale: {
        borderVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: false },
      handleScale: { mouseWheel: false, pinch: false, axisPressedMouseMove: false },
    });

    // Recession overlay series — always created, data set separately
    const recSeries = chart.addHistogramSeries({
      priceScaleId: "recession",
      color: "rgba(160, 160, 160, 0.10)",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    chart.priceScale("recession").applyOptions({
      scaleMargins: { top: 0, bottom: 0 },
      visible: false,
    });

    const series = chart.addAreaSeries({
      lineColor: color,
      topColor: `${color}28`,
      bottomColor: `${color}00`,
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: true,
      crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: "#0d0d0d",
      crosshairMarkerBackgroundColor: color,
      crosshairMarkerBorderWidth: 2,
    });

    chart.subscribeCrosshairMove((param) => {
      if (!param.time || !param.seriesData?.size) { setCrosshair(null); return; }
      const pt = param.seriesData.get(series) as { value: number } | undefined;
      if (pt) {
        const dateStr = typeof param.time === "string" ? param.time : "";
        setCrosshair({ value: pt.value, date: dateStr });
      } else {
        setCrosshair(null);
      }
    });

    chartRef.current    = chart;
    seriesRef.current   = series;
    recSeriesRef.current = recSeries;

    return () => {
      chart.remove();
      chartRef.current     = null;
      seriesRef.current    = null;
      recSeriesRef.current = null;
    };
  }, [color, compact]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Update data + recession bands + visible range atomically ──────────────
  useEffect(() => {
    if (!seriesRef.current || !chartRef.current) return;
    const chartData = filtered
      .filter((d) => d.value != null)
      .map((d) => ({ time: d.date, value: d.value as number }));
    if (!chartData.length) return;

    // Main series
    seriesRef.current.setData(chartData);

    // Recession bands — clipped to the indicator's visible date range so they
    // never force the chart to zoom out to 1854
    if (recSeriesRef.current) {
      if (recessionBands?.length) {
        const from = chartData[0].time;
        const to   = chartData[chartData.length - 1].time;
        const clipped = recessionBands.filter((b) => b.end >= from && b.start <= to);
        recSeriesRef.current.setData(toHistogramPoints(clipped));
      } else {
        recSeriesRef.current.setData([]);
      }
    }

    // Explicitly pin the visible range to the indicator data — not the recession bands
    chartRef.current.timeScale().setVisibleRange({
      from: chartData[0].time as import("lightweight-charts").Time,
      to:   chartData[chartData.length - 1].time as import("lightweight-charts").Time,
    });
  }, [filtered, recessionBands]);

  const display = crosshair ?? (latest ? { value: latest.value as number, date: latest.date } : null);

  return (
    <div className="bg-card rounded-xl border border-subtle p-4 transition-all duration-200 hover:border-white/[0.1]">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-4">
        <div>
          <h3 className="text-sm font-medium text-primary">{title}</h3>
          <p className="text-[10px] text-muted mt-0.5">
            {unit}{isPercent && transform !== "level" ? " · YoY" : ""}
          </p>
        </div>
        <div className="flex gap-0.5 bg-[#111] rounded-lg p-0.5 border border-subtle shrink-0">
          {PERIODS.map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-2 py-1 text-[10px] rounded-md transition-all duration-150 font-medium ${
                p === period ? "bg-white/[0.08] text-primary" : "text-muted hover:text-secondary"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Value display */}
      {display && (
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-semibold tabular transition-all duration-100" style={{ color }}>
            {display.value.toFixed(2)}{isPercent ? "%" : ""}
          </span>
          <span className="text-[10px] text-muted">{display.date}</span>
        </div>
      )}

      {/* Chart canvas — CSS height drives autoSize */}
      <div ref={containerRef} className={compact ? "h-28 w-full" : "h-44 w-full"} />
    </div>
  );
}
