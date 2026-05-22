import { useQuery } from "@tanstack/react-query";
import { Sparkles, RefreshCw, KeyRound } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";

interface Props {
  zone: string;
  country?: string;
}

export default function MacroNarrative({ zone, country }: Props) {
  const [refreshKey, setRefreshKey] = useState(0);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ["narrative", zone, country, refreshKey],
    queryFn: () => api.narrative(zone, country),
    staleTime: 1000 * 60 * 55, // refresh just before 1h server cache expires
    retry: 1,
  });

  const spinning = isLoading || isFetching;

  // No API key configured
  if (data?.no_key) {
    return (
      <div className="flex items-center gap-3 px-4 py-3 rounded-xl border border-subtle bg-card mb-5">
        <KeyRound size={14} className="text-muted shrink-0" />
        <p className="text-[11px] text-muted">
          Add <code className="text-accent">ANTHROPIC_API_KEY</code> to <code className="text-accent">.env</code> to enable AI macro narratives.
        </p>
      </div>
    );
  }

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="px-4 py-3 rounded-xl border border-subtle bg-card mb-5 space-y-2 animate-pulse">
        <div className="h-2.5 bg-white/[0.05] rounded w-3/4" />
        <div className="h-2.5 bg-white/[0.05] rounded w-full" />
        <div className="h-2.5 bg-white/[0.05] rounded w-2/3" />
      </div>
    );
  }

  if (!data?.narrative) return null;

  return (
    <div className="px-4 py-3 rounded-xl border border-accent/15 bg-accent/[0.03] mb-5 group">
      <div className="flex items-start gap-3">
        <Sparkles size={13} className="text-accent shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[9px] font-semibold text-accent uppercase tracking-widest">
              AI Macro Snapshot
            </span>
            {data.cached && (
              <span className="text-[9px] text-muted/50">cached</span>
            )}
          </div>
          <p className="text-[12px] text-secondary leading-relaxed">
            {data.narrative}
          </p>
        </div>
        <button
          onClick={() => setRefreshKey((k) => k + 1)}
          disabled={spinning}
          className="shrink-0 p-1 rounded-md text-muted hover:text-primary hover:bg-white/[0.05] transition-colors opacity-0 group-hover:opacity-100"
          title="Regenerate"
        >
          <RefreshCw size={11} className={spinning ? "animate-spin" : ""} />
        </button>
      </div>
    </div>
  );
}
