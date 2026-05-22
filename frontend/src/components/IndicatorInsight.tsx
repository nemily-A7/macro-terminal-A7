import { useQuery } from "@tanstack/react-query";
import { Sparkles, BookOpen, Loader2 } from "lucide-react";
import { api } from "../api/client";

interface Props {
  zone: string;
  indicatorKey: string;
  country?: string;
}

export default function IndicatorInsight({ zone, indicatorKey, country }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ["insight", zone, indicatorKey, country],
    queryFn: () => api.indicatorInsight(zone, indicatorKey, country),
    staleTime: 1000 * 60 * 60,
    retry: false,
  });

  const hasDescription = !!data?.description;
  const hasInterpretation = !!data?.interpretation;
  const showInterpretation = isLoading || hasInterpretation || data?.no_key === true;

  if (!isLoading && !hasDescription && !hasInterpretation) return null;

  return (
    <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 animate-fadeIn">

      {/* Static description */}
      {(isLoading || hasDescription) && (
        <div className="p-4 rounded-xl border border-subtle bg-card">
          <div className="flex items-center gap-2 mb-2.5">
            <BookOpen size={11} className="text-muted" />
            <span className="text-[10px] font-semibold text-muted uppercase tracking-widest">
              About this indicator
            </span>
          </div>
          {isLoading ? (
            <div className="space-y-2">
              <div className="skeleton h-2.5 w-full rounded" />
              <div className="skeleton h-2.5 w-5/6 rounded" />
              <div className="skeleton h-2.5 w-4/6 rounded" />
            </div>
          ) : (
            <p className="text-[12px] text-secondary leading-relaxed">{data!.description}</p>
          )}
        </div>
      )}

      {/* AI interpretation */}
      {showInterpretation && (
        <div className="p-4 rounded-xl border border-subtle bg-card">
          <div className="flex items-center gap-2 mb-2.5">
            <Sparkles size={11} className="text-accent" />
            <span className="text-[10px] font-semibold text-muted uppercase tracking-widest">
              AI Interpretation
            </span>
            {data?.cached && (
              <span className="text-[9px] text-muted/50 ml-auto">cached</span>
            )}
          </div>

          {isLoading ? (
            <div className="flex items-center gap-2 text-muted">
              <Loader2 size={11} className="animate-spin shrink-0" />
              <span className="text-[11px]">Analyzing current data…</span>
            </div>
          ) : data?.no_key ? (
            <p className="text-[11px] text-muted italic">
              Set ANTHROPIC_API_KEY in .env to enable AI interpretations.
            </p>
          ) : hasInterpretation ? (
            <p className="text-[12px] text-secondary leading-relaxed">{data!.interpretation}</p>
          ) : (
            <p className="text-[11px] text-muted italic">No data available to interpret.</p>
          )}
        </div>
      )}

    </div>
  );
}
