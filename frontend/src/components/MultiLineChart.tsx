import { useState, useEffect, useRef, useCallback } from "react";
import { createChart, ColorType, CrosshairMode, LineStyle } from "lightweight-charts";
import type { IChartApi, ISeriesApi } from "lightweight-charts";
import type { DataPoint } from "../types";
import type { RecessionBand } from "./IndicatorChart";

const PERIODS = ["1Y", "3Y", "5Y", "10Y", "Max"] as const;

const COUNTRY_COLORS: Record<string, string> = {
  "Euro Area":   "#3b82f6",
  "Germany":     "#f59e0b",
  "France":      "#22c55e",
  "Italy":       "#ef4444",
  "Spain":       "#8b5cf6",
  "Netherlands": "#06b6d4",
  "China":       "#ef4444",
  "Japan":       "#3b82f6",
  "South Korea": "#22c55e",
  "India":       "#f59e0b",
  "Singapore":   "#8b5cf6",
  "Australia":   "#06b6d4",
};

const FALLBACK_COLORS = ["#3b82f6", "#f59e0b", "#22c55e", "#ef4444", "#8b5cf6", "#06b6d4"];

function filterByPeriod(data: DataPoint[], period: string): DataPoint[] {
  if (period === "Max") return data;
  const years = { "1Y": 1, "3Y": 3, "5Y": 5, "10Y": 10 }[period] ?? 5;
  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - years);
  return data.filter((d) => new Date(d.date) >= cutoff);
}

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

export interface CountrySeries {
  country: string;
  history: DataPoint[];
  history_transformed?: DataPoint[];
  latest: DataPoint | null;
  delta: number | null;
}

interface Props {
  series: CountrySeries[];
  title: string;
  unit: string;
  transform: string;
  recessionBands?: RecessionBand[];
}

export default function MultiLineChart({ series, title, unit, transform, recessionBands }: Props) {
  const [period, setPeriod] = useState<string>("5Y");
  const containerRef  = useRef<HTMLDivElement>(null);
  const chartRef      = useRef<IChartApi | null>(null);
  const lineSeriesRef = useRef<ISeriesApi<"Line">[]>([]);
  const recSeriesRef  = useRef<ISeriesApi<"Histogram"> | null>(null);

  const isPercent = transform !== "level" || unit.toLowerCase().includes("percent");

  // ── Chart init: only when series list (countries) changes ──────────────────
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !series.length) return;

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
        vertLine: { color: "rgba(255,255,255,0.15)", width: 1, style: LineStyle.Dashed, labelVisible: false },
        horzLine: { color: "rgba(255,255,255,0.1)", width: 1, labelBackgroundColor: "#1a1a1a" },
      },
      rightPriceScale: {
        borderVisible: false,
        textColor: "#444",
        scaleMargins: { top: 0.12, bottom: 0.08 },
      },
      timeScale: { borderVisible: false, fixLeftEdge: true, fixRightEdge: true },
      handleScroll: { mouseWheel: true, pressedMouseMove: false },
      handleScale: { mouseWheel: false, pinch: false, axisPressedMouseMove: false },
    });

    // Recession overlay
    const recSeries = chart.addHistogramSeries({
      priceScaleId: "recession",
      color: "rgba(160, 160, 160, 0.10)",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    chart.priceScale("recession").applyOptions({ scaleMargins: { top: 0, bottom: 0 }, visible: false });

    // One line series per country
    const lines = series.map((s, idx) => {
      const color = COUNTRY_COLORS[s.country] ?? FALLBACK_COLORS[idx % FALLBACK_COLORS.length];
      return chart.addLineSeries({
        color,
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerRadius: 4,
        crosshairMarkerBorderColor: "#0d0d0d",
        crosshairMarkerBackgroundColor: color,
        crosshairMarkerBorderWidth: 2,
      });
    });

    chartRef.current      = chart;
    lineSeriesRef.current = lines;
    recSeriesRef.current  = recSeries;

    return () => {
      chart.remove();
      chartRef.current      = null;
      lineSeriesRef.current = [];
      recSeriesRef.current  = null;
    };
  }, [series]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Update lines + recession bands + visible range atomically ────────────
  const updateData = useCallback(() => {
    if (!chartRef.current || !lineSeriesRef.current.length) return;
    let from: string | null = null;
    let to:   string | null = null;

    series.forEach((s, idx) => {
      const line = lineSeriesRef.current[idx];
      if (!line) return;
      const raw = transform === "level" ? s.history : (s.history_transformed ?? s.history);
      const pts = filterByPeriod(raw.filter((d) => d.value != null), period)
        .map((d) => ({ time: d.date, value: d.value as number }));
      line.setData(pts);
      if (pts.length) {
        if (!from || pts[0].time < from) from = pts[0].time;
        if (!to   || pts[pts.length - 1].time > to) to = pts[pts.length - 1].time;
      }
    });

    // Recession bands clipped to visible date range
    if (recSeriesRef.current) {
      if (recessionBands?.length && from && to) {
        const clipped = recessionBands.filter((b) => b.end >= from! && b.start <= to!);
        recSeriesRef.current.setData(toHistogramPoints(clipped));
      } else {
        recSeriesRef.current.setData([]);
      }
    }

    if (from && to) {
      chartRef.current.timeScale().setVisibleRange({
        from: from as import("lightweight-charts").Time,
        to:   to   as import("lightweight-charts").Time,
      });
    }
  }, [series, period, transform, recessionBands]);

  useEffect(() => { updateData(); }, [updateData]);

  return (
    <div className="bg-card rounded-xl border border-subtle p-4 hover:border-white/[0.1] transition-all duration-200">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div>
          <h3 className="text-sm font-medium text-primary">{title}</h3>
          <p className="text-[10px] text-muted mt-0.5">
            {unit}{isPercent && transform !== "level" ? " · YoY" : ""} · comparaison pays
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

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 mb-3">
        {series.map((s, idx) => {
          const color  = COUNTRY_COLORS[s.country] ?? FALLBACK_COLORS[idx % FALLBACK_COLORS.length];
          const raw    = transform === "level" ? s.history : (s.history_transformed ?? s.history);
          const latest = raw.filter((d) => d.value != null).at(-1);
          return (
            <div key={s.country} className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-[10px] text-muted">{s.country}</span>
              {latest?.value != null && (
                <span className="text-[10px] font-semibold tabular" style={{ color }}>
                  {latest.value.toFixed(2)}{isPercent ? "%" : ""}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Chart canvas */}
      <div ref={containerRef} className="h-48 w-full" />
    </div>
  );
}
