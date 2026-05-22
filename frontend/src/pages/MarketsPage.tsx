import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { Wifi } from "lucide-react";
import { api } from "../api/client";
import { useZone } from "../contexts/ZoneContext";
import TickerCard from "../components/TickerCard";
import IndicatorChart from "../components/IndicatorChart";
import type { MarketData, AssetClass } from "../types";

const SECTIONS: { key: AssetClass; label: string; color: string }[] = [
  { key: "equity",    label: "Equities",    color: "#22c55e" },
  { key: "fx",        label: "FX",          color: "#3b82f6" },
  { key: "commodity", label: "Commodities", color: "#f59e0b" },
  { key: "crypto",    label: "Crypto",      color: "#8b5cf6" },
];

const EQUITY_ZONES: { key: string; label: string }[] = [
  { key: "US",     label: "United States" },
  { key: "EU",     label: "Europe" },
  { key: "ASIA",   label: "Asia-Pacific" },
  { key: "GLOBAL", label: "Global" },
];

function SkeletonTicker() {
  return (
    <div className="flex flex-col gap-2 p-3.5 rounded-xl border border-subtle bg-card">
      <div className="skeleton h-2 w-16 rounded" />
      <div className="skeleton h-5 w-24 rounded" />
      <div className="skeleton h-2.5 w-12 rounded" />
      <div className="skeleton h-8 rounded" />
    </div>
  );
}

export default function MarketsPage() {
  const [selected, setSelected] = useState<MarketData | null>(null);
  const { liveMarkets, wsReady } = useZone();

  const { data, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["markets"],
    queryFn: api.markets,
    staleTime: 1000 * 60 * 15,
    refetchInterval: 1000 * 60 * 15,
  });

  // Merge WS live quotes over HTTP data — WS updates every 30s, HTTP every 15 min
  const markets: MarketData[] = useMemo(() => {
    const base = data?.markets ?? [];
    if (!liveMarkets.size) return base;
    return base.map((m) => {
      const ws = liveMarkets.get(m.key);
      if (!ws) return m;
      return {
        ...m,
        live_price:      ws.price,
        live_pct_change: ws.pct_change,
        live_change:     ws.change,
        is_market_open:  ws.is_market_open,
        live_datetime:   ws.datetime,
        live_source:     "twelvedata" as const,
      };
    });
  }, [data, liveMarkets]);

  const byClass = useMemo(() => {
    const map: Partial<Record<AssetClass, MarketData[]>> = {};
    for (const s of SECTIONS) {
      map[s.key] = markets
        .filter((m) => m.asset_class === s.key)
        .sort((a, b) => a.priority - b.priority);
    }
    return map;
  }, [markets]);

  const selectedSection = SECTIONS.find((s) => s.key === selected?.asset_class);
  const selectedMarket  = selected ? (markets.find((m) => m.key === selected.key) ?? selected) : null;

  const hasLive    = markets.some((m) => m.live_source === "twelvedata");
  const wsLiveCount = liveMarkets.size;
  const updatedLabel = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })
    : null;

  return (
    <div className="p-5 max-w-screen-xl mx-auto space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-sm font-semibold text-primary">Global Markets</h1>
          <p className="text-[11px] text-muted mt-0.5">
            {hasLive
              ? "FX & Crypto live via Twelve Data · Equities live via Finnhub · Historical via FRED"
              : "US · EU · Asia-Pacific Equities · FX · Commodities · Crypto — via FRED"}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* WS live indicator */}
          {wsLiveCount > 0 && (
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-full border border-positive/20 bg-positive/5">
              <Wifi size={10} className="text-positive" />
              <span className="text-[10px] text-positive font-medium">
                {wsLiveCount} live · 30s
              </span>
            </div>
          )}
          {!wsReady && (
            <span className="text-[10px] text-muted px-2 py-1 rounded-full border border-subtle">
              WS reconnecting…
            </span>
          )}
          {updatedLabel && (
            <span className="text-[10px] text-muted">
              HTTP {updatedLabel}
            </span>
          )}
          {!isLoading && data && (
            <span className="text-[10px] text-muted px-2 py-1 rounded-full border border-subtle">
              {data.markets.length} instruments
            </span>
          )}
        </div>
      </div>

      {/* Sections */}
      {SECTIONS.map(({ key, label, color }) => {
        const items = byClass[key] ?? [];
        if (!isLoading && items.length === 0) return null;

        // Equities: split by market_zone for clarity
        const isEquity = key === "equity";
        const equityByZone = isEquity
          ? EQUITY_ZONES.map((z) => ({
              ...z,
              items: items.filter((m) => (m.market_zone ?? "GLOBAL") === z.key),
            })).filter((z) => z.items.length > 0)
          : [];

        return (
          <section key={key}>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-0.5 h-3.5 rounded-full" style={{ backgroundColor: color }} />
              <h2 className="text-[11px] font-semibold text-muted uppercase tracking-widest">{label}</h2>
            </div>

            {isEquity && !isLoading ? (
              <div className="space-y-4">
                {equityByZone.map(({ key: zone, label: zoneLabel, items: zItems }) => (
                  <div key={zone}>
                    <p className="text-[10px] text-muted mb-2 font-medium tracking-wide">{zoneLabel}</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2.5">
                      {zItems.map((m, i) => (
                        <TickerCard
                          key={m.key}
                          market={m}
                          selected={selected?.key === m.key}
                          animDelay={i * 40}
                          onClick={() => setSelected(selected?.key === m.key ? null : m)}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2.5">
                {isLoading
                  ? Array.from({ length: key === "fx" ? 5 : key === "equity" ? 4 : 2 }).map((_, i) => (
                      <SkeletonTicker key={i} />
                    ))
                  : items.map((m, i) => (
                      <TickerCard
                        key={m.key}
                        market={m}
                        selected={selected?.key === m.key}
                        animDelay={i * 40}
                        onClick={() => setSelected(selected?.key === m.key ? null : m)}
                      />
                    ))}
              </div>
            )}

            {selectedMarket && selectedSection?.key === key && !isLoading && (
              <div className="mt-3 animate-fadeIn">
                <IndicatorChart
                  data={selectedMarket.history}
                  title={selectedMarket.display_name}
                  unit={selectedMarket.unit}
                  transform="level"
                  color={color}
                />
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
