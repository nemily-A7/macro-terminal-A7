import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { GitCompareArrows } from "lucide-react";
import clsx from "clsx";
import { api } from "../api/client";
import { useZone } from "../contexts/ZoneContext";
import KpiCard from "../components/KpiCard";
import SkeletonCard from "../components/SkeletonCard";
import IndicatorChart from "../components/IndicatorChart";
import MultiLineChart from "../components/MultiLineChart";
import type { CategoryKey, IndicatorData } from "../types";
import type { RecessionBand } from "../components/IndicatorChart";

interface Props {
  category: CategoryKey;
  label: string;
  color: string;
  icon: React.ReactNode;
}

export default function CategoryPage({ category, label, color, icon }: Props) {
  const { zone, country, zones } = useZone();
  const [selected, setSelected] = useState<IndicatorData | null>(null);
  const [compareMode, setCompareMode] = useState(false);

  const currentZone     = zones.find((z) => z.key === zone);
  const resolvedCountry = country ?? currentZone?.default_country;
  const isMultiCountry  = (currentZone?.countries.length ?? 0) > 1;

  const { data, isLoading } = useQuery({
    queryKey: ["category", zone, category, resolvedCountry],
    queryFn: () => api.categoryIndicators(zone, category, resolvedCountry ?? undefined),
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

  const indicators = (data?.indicators ?? []).sort((a, b) => a.priority - b.priority);

  // Compare data — fetch for all indicators when compareMode active
  const compareQueries = useQuery({
    queryKey: ["compare", zone, category],
    queryFn: async () => {
      const results = await Promise.all(
        indicators.map((ind) => api.indicatorCompare(zone, ind.key))
      );
      return results;
    },
    enabled: compareMode && !isLoading && indicators.length > 0,
    staleTime: 1000 * 60 * 15,
  });

  return (
    <div className="p-5 max-w-screen-xl mx-auto">
      {/* Category banner */}
      <div
        className="flex items-center gap-3 px-4 py-3 rounded-xl mb-5 border"
        style={{
          background: `linear-gradient(135deg, ${color}10, ${color}05)`,
          borderColor: `${color}20`,
        }}
      >
        <span style={{ color }} className="text-lg">{icon}</span>
        <div>
          <h1 className="text-sm font-semibold text-primary">{label}</h1>
          <p className="text-[11px] text-muted">
            {currentZone?.label}{!compareMode && resolvedCountry ? ` · ${resolvedCountry}` : " · All countries"}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {!isLoading && (
            <span
              className="text-xs font-medium px-2 py-0.5 rounded-full"
              style={{ background: `${color}15`, color }}
            >
              {indicators.length} indicators
            </span>
          )}
          {isMultiCountry && (
            <button
              onClick={() => { setCompareMode((m) => !m); setSelected(null); }}
              className={clsx(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all",
                compareMode
                  ? "bg-accent/10 border-accent/30 text-accent"
                  : "border-subtle text-secondary hover:text-primary hover:bg-white/[0.05]"
              )}
            >
              <GitCompareArrows size={12} />
              Compare
            </button>
          )}
        </div>
      </div>

      {/* Normal mode */}
      {!compareMode && (
        <>
          {/* KPI cards row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5 mb-5">
            {isLoading
              ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
              : indicators.map((ind, i) => (
                  <KpiCard
                    key={ind.key}
                    indicator={ind}
                    selected={selected?.key === ind.key}
                    animDelay={i * 50}
                    onClick={() => setSelected(selected?.key === ind.key ? null : ind)}
                  />
                ))}
          </div>

          {/* Selected indicator — full detail chart */}
          {selected && !isLoading && (
            <div className="mb-5 animate-fadeIn">
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
            </div>
          )}

          {/* Charts grid — all indicators */}
          {!isLoading && indicators.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {indicators.map((ind) => (
                <div
                  key={ind.key}
                  onClick={() => setSelected(selected?.key === ind.key ? null : ind)}
                  className="cursor-pointer"
                >
                  <IndicatorChart
                    data={
                      ind.transform_default === "level"
                        ? ind.history
                        : ind.history_transformed ?? ind.history
                    }
                    title={ind.display_name}
                    unit={ind.unit}
                    transform={ind.transform_default}
                    color={color}
                    recessionBands={recessionBands}
                  />
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Compare mode */}
      {compareMode && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {compareQueries.isLoading
            ? Array.from({ length: indicators.length || 4 }).map((_, i) => (
                <div key={i} className="skeleton h-64 rounded-xl" />
              ))
            : (compareQueries.data ?? []).map((comp, i) => (
                comp.series.length > 0 && (
                  <MultiLineChart
                    key={indicators[i]?.key ?? i}
                    series={comp.series}
                    title={comp.display_name}
                    unit={comp.unit}
                    transform={comp.transform_default}
                    recessionBands={recessionBands}
                  />
                )
              ))}
        </div>
      )}
    </div>
  );
}
