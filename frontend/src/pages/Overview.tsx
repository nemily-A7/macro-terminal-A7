import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";
import { useZone } from "../contexts/ZoneContext";
import KpiCard from "../components/KpiCard";
import SkeletonCard from "../components/SkeletonCard";
import IndicatorChart from "../components/IndicatorChart";
import MacroNarrative from "../components/MacroNarrative";
import IndicatorInsight from "../components/IndicatorInsight";
import { CATEGORIES } from "../types";
import type { IndicatorData } from "../types";
import type { RecessionBand } from "../components/IndicatorChart";

const CATEGORY_COLORS: Record<string, string> = {
  Inflation:     "#f59e0b",
  Rates:         "#3b82f6",
  Labor:         "#8b5cf6",
  Growth:        "#22c55e",
  Money_Credit:  "#06b6d4",
  Risk_Sentiment:"#ef4444",
};

export default function Overview() {
  const { zone, country, zones } = useZone();
  const [selected, setSelected] = useState<IndicatorData | null>(null);

  const currentZone    = zones.find((z) => z.key === zone);
  const resolvedCountry = country ?? currentZone?.default_country;

  const { data, isLoading } = useQuery({
    queryKey: ["zone-indicators", zone, resolvedCountry],
    queryFn: () => api.zoneIndicators(zone, resolvedCountry ?? undefined),
    enabled: !!zone,
    staleTime: 1000 * 60 * 5,
  });

  const { data: recData } = useQuery({
    queryKey: ["recessions"],
    queryFn: api.recessions,
    enabled: zone === "US",
    staleTime: 1000 * 60 * 60 * 24,
  });
  const recessionBands: RecessionBand[] | undefined = zone === "US" ? recData?.bands : undefined;

  const indicators = data?.indicators ?? [];
  const byCategory  = CATEGORIES.reduce<Record<string, IndicatorData[]>>((acc, cat) => {
    acc[cat.key] = indicators
      .filter((ind) => ind.category === cat.key && ind.priority <= 2)
      .sort((a, b) => a.priority - b.priority);
    return acc;
  }, {});

  return (
    <div className="p-5 max-w-screen-2xl mx-auto space-y-7">
      <MacroNarrative zone={zone} country={resolvedCountry} />
      {CATEGORIES.map(({ key, label }) => {
        const inds  = byCategory[key];
        const color = CATEGORY_COLORS[key] ?? "#3b82f6";
        const showSection = isLoading || (inds?.length ?? 0) > 0;
        if (!showSection) return null;

        return (
          <section key={key}>
            {/* Section header */}
            <div className="flex items-center gap-2 mb-3">
              <div className="w-0.5 h-3.5 rounded-full" style={{ backgroundColor: color }} />
              <h2 className="text-[11px] font-semibold text-muted uppercase tracking-widest">{label}</h2>
              {!isLoading && (
                <span className="text-[10px] text-muted opacity-50 ml-1">{inds.length}</span>
              )}
            </div>

            {/* KPI grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-2.5">
              {isLoading
                ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
                : inds.map((ind, i) => (
                    <KpiCard
                      key={ind.key}
                      indicator={ind}
                      selected={selected?.key === ind.key}
                      animDelay={i * 40}
                      onClick={() => setSelected(selected?.key === ind.key ? null : ind)}
                    />
                  ))}
            </div>

            {/* Expanded chart + insight panel */}
            {selected && !isLoading && inds.find((i) => i.key === selected.key) && (
              <div className="mt-3 animate-fadeIn">
                <IndicatorChart
                  data={
                    selected.transform_default === "level"
                      ? selected.history
                      : selected.history_transformed ?? selected.history
                  }
                  title={selected.display_name}
                  unit={selected.unit}
                  transform={selected.transform_default}
                  color={color}
                  recessionBands={recessionBands}
                />
                <IndicatorInsight
                  zone={zone}
                  indicatorKey={selected.key}
                  country={resolvedCountry}
                />
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
