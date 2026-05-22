import clsx from "clsx";
import type { MarketData } from "../types";
import MiniChart from "./MiniChart";

function formatPrice(value: number, assetClass: string, unit: string): string {
  if (assetClass === "fx") {
    return value.toFixed(unit === "JPY" || unit === "CNY" ? 2 : 4);
  }
  if (assetClass === "crypto") {
    return value >= 10000
      ? value.toLocaleString("en-US", { maximumFractionDigits: 0 })
      : value.toFixed(2);
  }
  // equity / commodity
  if (value >= 10000) return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 1000)  return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return value.toFixed(2);
}

interface Props {
  market: MarketData;
  selected: boolean;
  onClick: () => void;
  animDelay?: number;
}

export default function TickerCard({ market, selected, onClick, animDelay = 0 }: Props) {
  const isLive = market.live_price != null;

  // Use live price from Twelve Data when available, fall back to last FRED close
  const price = isLive
    ? market.live_price!
    : (market.history.filter((d) => d.value != null).at(-1)?.value ?? null);

  const pctChange = isLive
    ? market.live_pct_change
    : (() => {
        const h = market.history.filter((d) => d.value != null);
        const latest = h.at(-1);
        const prev   = h.at(-2);
        if (latest?.value != null && prev?.value != null && prev.value !== 0)
          return ((latest.value - prev.value) / Math.abs(prev.value)) * 100;
        return null;
      })();

  const isUp = pctChange !== null && pctChange >= 0;

  const sparklineRaw = market.history.filter((d) => d.value != null).slice(-60);
  // Append live price to sparkline so the chart tip reflects today
  const sparkline = isLive && sparklineRaw.length > 0
    ? [...sparklineRaw.slice(0, -1), { date: market.live_datetime ?? sparklineRaw.at(-1)!.date, value: market.live_price! }]
    : sparklineRaw;

  return (
    <button
      onClick={onClick}
      style={{ animationDelay: `${animDelay}ms` }}
      className={clsx(
        "animate-fadeUp flex flex-col gap-2 p-3.5 rounded-xl border text-left w-full",
        "transition-all duration-150 hover:-translate-y-0.5",
        selected
          ? "border-accent/40 bg-accent/5 shadow-lg shadow-accent/5"
          : "border-subtle bg-card hover:border-white/[0.12] hover:bg-[#1f1f1f]"
      )}
    >
      {/* Name + live badge */}
      <div className="flex items-center justify-between gap-1">
        <p className="text-[10px] font-semibold text-muted uppercase tracking-widest leading-none">
          {market.display_name}
        </p>
        {isLive && (
          <span className={clsx(
            "text-[8px] font-semibold px-1 py-0.5 rounded leading-none",
            market.is_market_open
              ? "bg-positive/10 text-positive"
              : "bg-muted/10 text-muted"
          )}>
            {market.is_market_open ? "LIVE" : "COB"}
          </span>
        )}
      </div>

      {/* Price */}
      <p className="text-[18px] font-semibold tabular text-primary leading-none">
        {price != null ? formatPrice(price, market.asset_class, market.unit) : "—"}
      </p>

      {/* % change */}
      <p className={clsx(
        "text-[11px] font-medium tabular",
        pctChange == null ? "text-muted" : isUp ? "text-positive" : "text-negative"
      )}>
        {pctChange != null
          ? `${isUp ? "▲" : "▼"} ${Math.abs(pctChange).toFixed(2)}%`
          : "—"}
      </p>

      {/* Mini sparkline */}
      {sparkline.length > 4 && (
        <div className="h-8 -mx-0.5">
          <MiniChart data={sparkline} positive={isUp} />
        </div>
      )}
    </button>
  );
}
