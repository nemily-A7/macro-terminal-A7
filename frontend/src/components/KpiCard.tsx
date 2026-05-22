import { useRef, useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import clsx from "clsx";
import type { IndicatorData } from "../types";
import MiniChart from "./MiniChart";
import { useZone } from "../contexts/ZoneContext";

function formatValue(value: number | null | undefined, unit: string, transform: string): string {
  if (value == null || isNaN(value)) return "—";
  const isPercent = transform !== "level" || unit.toLowerCase().includes("percent");
  if (isPercent) return `${value >= 0 ? "" : ""}${value.toFixed(2)}%`;
  if (unit.toLowerCase().includes("billions")) return `$${(value / 1000).toFixed(1)}T`;
  if (unit.toLowerCase().includes("thousands")) {
    return value >= 1000 ? `${(value / 1000).toFixed(1)}M` : `${Math.round(value).toLocaleString()}K`;
  }
  if (Math.abs(value) >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (Math.abs(value) >= 100) return value.toFixed(1);
  return value.toFixed(2);
}

function formatDelta(delta: number | null, transform: string, unit: string): string | null {
  if (delta == null || isNaN(delta)) return null;
  const sign = delta > 0 ? "+" : "";
  const isPercent = transform !== "level" || unit.toLowerCase().includes("percent");
  if (isPercent) return `${sign}${delta.toFixed(2)}pp`;
  return `${sign}${delta.toFixed(2)}`;
}

interface Props {
  indicator: IndicatorData;
  onClick?: () => void;
  selected?: boolean;
  animDelay?: number;
}

const TREND_STYLES = {
  up:   { icon: TrendingUp,   badge: "bg-positive/10 text-positive", dot: "bg-positive" },
  down: { icon: TrendingDown, badge: "bg-negative/10 text-negative", dot: "bg-negative" },
  flat: { icon: Minus,        badge: "bg-muted/10 text-muted",       dot: "bg-muted" },
};

export default function KpiCard({ indicator, onClick, selected, animDelay = 0 }: Props) {
  const { liveData } = useZone();
  const { display_name, transform_default: transform, unit, history_transformed, history } = indicator;

  const live = liveData.get(indicator.key);
  const value = live?.value ?? indicator.latest?.value ?? null;
  const delta = live?.delta ?? indicator.delta ?? null;
  const date  = live?.date ?? indicator.latest?.date;

  const chartData = (transform === "level" ? history : history_transformed) ?? [];
  const validChart = chartData.filter((d) => d.value != null).slice(-48);

  const trend = delta == null ? null : delta > 0.001 ? "up" : delta < -0.001 ? "down" : "flat";
  const trendStyle = trend ? TREND_STYLES[trend] : null;
  const TrendIcon  = trendStyle?.icon;
  const deltaStr   = formatDelta(delta, transform, unit);
  const hasValue   = value != null;

  // Flash on live update
  const prevValueRef = useRef<number | null>(null);
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    if (live?.value != null && prevValueRef.current !== null && prevValueRef.current !== live.value) {
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 900);
      return () => clearTimeout(t);
    }
    prevValueRef.current = live?.value ?? null;
  }, [live?.value]);

  return (
    <button
      onClick={onClick}
      style={{ animationDelay: `${animDelay}ms` }}
      className={clsx(
        "group animate-fadeUp flex flex-col gap-2.5 p-4 rounded-xl border text-left w-full",
        "transition-all duration-200 hover:-translate-y-0.5",
        flash && "ring-1 ring-accent/40",
        selected
          ? "bg-accent/5 border-accent/30 shadow-lg shadow-accent/5"
          : "bg-card border-subtle hover:border-white/[0.12] hover:bg-[#1f1f1f]"
      )}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-1">
        <p className="text-[11px] font-medium text-secondary uppercase tracking-wider leading-tight">
          {display_name}
        </p>
        {trendStyle && TrendIcon && (
          <span className={clsx("shrink-0 p-0.5 rounded", trendStyle.badge)}>
            <TrendIcon size={10} />
          </span>
        )}
      </div>

      {/* Value */}
      <div className="flex items-end justify-between gap-2">
        <div>
          <p className={clsx(
            "text-[22px] font-semibold tracking-tight leading-none tabular transition-colors duration-300",
            !hasValue && "text-muted",
            hasValue && value! > 0 && transform !== "level" && "text-positive",
            hasValue && value! < 0 && transform !== "level" && "text-negative",
          )}>
            {formatValue(value, unit, transform)}
          </p>
          {date && (
            <p className="text-[10px] text-muted mt-1">
              {new Date(date).toLocaleDateString("en-US", { month: "short", year: "numeric", timeZone: "UTC" })}
            </p>
          )}
        </div>
        {deltaStr && (
          <span className={clsx(
            "text-[10px] font-medium px-1.5 py-0.5 rounded-md mb-0.5 shrink-0 tabular",
            trendStyle?.badge
          )}>
            {deltaStr}
          </span>
        )}
      </div>

      {/* Mini sparkline */}
      {validChart.length > 2 && (
        <div className="h-9 -mx-0.5 mt-0.5">
          <MiniChart data={validChart} positive={trend !== "down"} />
        </div>
      )}
    </button>
  );
}
