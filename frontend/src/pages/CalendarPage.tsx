import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { Loader2, Calendar, Clock, ChevronRight } from "lucide-react";
import clsx from "clsx";
import { api } from "../api/client";
import { useZone } from "../contexts/ZoneContext";
import type { CalendarEvent } from "../types";

const WINDOWS = [
  { label: "This week",  days_back: 0, days_ahead: 7 },
  { label: "2 weeks",    days_back: 0, days_ahead: 14 },
  { label: "±2 weeks",   days_back: 7, days_ahead: 14 },
  { label: "This month", days_back: 0, days_ahead: 30 },
];

const IMP_DOT: Record<number, string> = {
  3: "bg-negative",
  2: "bg-warning",
  1: "bg-muted/60",
};
function formatTime(dateUtc: string): string {
  const d = new Date(dateUtc);
  const h = d.getUTCHours(), m = d.getUTCMinutes();
  if (h === 0 && m === 0) return "TBA";
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")} UTC`;
}

function relativeTo(dateUtc: string, now: Date): string {
  const d = new Date(dateUtc);
  const diffMs = d.getTime() - now.getTime();
  const diffMin = Math.round(diffMs / 60000);
  if (diffMin < 0) {
    const abs = Math.abs(diffMin);
    if (abs < 60) return `${abs}m ago`;
    if (abs < 1440) return `${Math.floor(abs / 60)}h ago`;
    return `${Math.floor(abs / 1440)}d ago`;
  }
  if (diffMin < 60) return `in ${diffMin}m`;
  if (diffMin < 1440) return `in ${Math.floor(diffMin / 60)}h ${diffMin % 60}m`;
  return `in ${Math.floor(diffMin / 1440)}d`;
}

function dayLabel(dateUtc: string, now: Date): string {
  const d = new Date(dateUtc);
  const today = new Date(now);
  today.setUTCHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setUTCDate(today.getUTCDate() + 1);
  const dayStart = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  if (dayStart.getTime() === today.getTime()) return "Today";
  if (dayStart.getTime() === tomorrow.getTime()) return "Tomorrow";
  return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
}

function groupByDay(events: CalendarEvent[]): [string, CalendarEvent[]][] {
  const map = new Map<string, CalendarEvent[]>();
  for (const ev of events) {
    const dayKey = ev.date_utc.slice(0, 10);
    if (!map.has(dayKey)) map.set(dayKey, []);
    map.get(dayKey)!.push(ev);
  }
  return Array.from(map.entries());
}

function EventRow({ event, now }: { event: CalendarEvent; now: Date }) {
  const isPast = new Date(event.date_utc) < now;
  const hasActual = event.actual != null;
  const beatForecast = hasActual && event.forecast != null
    ? event.actual! > event.forecast! ? "beat" : "miss"
    : null;

  return (
    <div className={clsx(
      "flex items-center gap-3 px-4 py-2.5 border-b border-subtle/50 last:border-0",
      "hover:bg-white/[0.02] transition-colors",
      isPast && !hasActual && "opacity-50"
    )}>
      {/* Importance dot */}
      <div className={clsx("w-1.5 h-1.5 rounded-full shrink-0", IMP_DOT[event.importance])} />

      {/* Time */}
      <span className="text-[11px] text-muted w-16 shrink-0 tabular">
        {formatTime(event.date_utc)}
      </span>

      {/* Relative time */}
      <span className={clsx(
        "text-[10px] w-16 shrink-0 tabular",
        isPast ? "text-muted/50" : "text-accent/70"
      )}>
        {relativeTo(event.date_utc, now)}
      </span>

      {/* Country flag area */}
      <span className="text-[11px] text-muted w-24 shrink-0 truncate">{event.country}</span>

      {/* Event name */}
      <span className={clsx(
        "text-[13px] flex-1 font-medium min-w-0 truncate",
        event.importance === 3 ? "text-primary" : "text-secondary"
      )}>
        {event.event}
      </span>

      {/* Values */}
      <div className="flex items-center gap-4 shrink-0 text-[11px]">
        <span className="text-muted w-16 text-right tabular">
          {event.previous != null ? event.previous.toFixed(2) : "—"}
        </span>
        <span className="text-muted w-16 text-right tabular">
          {event.forecast != null ? event.forecast.toFixed(2) : "—"}
        </span>
        <span className={clsx(
          "w-16 text-right font-medium tabular",
          !hasActual && "text-muted",
          beatForecast === "beat" && "text-positive",
          beatForecast === "miss" && "text-negative",
          hasActual && !beatForecast && "text-accent",
        )}>
          {hasActual ? event.actual!.toFixed(2) : isPast ? "—" : "Pending"}
        </span>
      </div>
    </div>
  );
}

function NextEventBanner({ event, now }: { event: CalendarEvent; now: Date }) {
  const mins = Math.round((new Date(event.date_utc).getTime() - now.getTime()) / 60000);
  const timeStr = mins < 60
    ? `in ${mins}m`
    : `in ${Math.floor(mins / 60)}h ${mins % 60}m`;

  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl border border-accent/20 bg-accent/5 mb-5">
      <Clock size={14} className="text-accent shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-[10px] text-accent uppercase tracking-widest font-semibold">Next key release</p>
        <p className="text-sm font-semibold text-primary truncate mt-0.5">{event.event}</p>
        <p className="text-[11px] text-muted">{event.country} · {formatTime(event.date_utc)}</p>
      </div>
      <div className="text-right shrink-0">
        <p className="text-lg font-semibold text-accent tabular">{timeStr}</p>
        <p className="text-[10px] text-muted mt-0.5">
          {new Date(event.date_utc).toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" })}
        </p>
      </div>
      <ChevronRight size={14} className="text-muted shrink-0" />
    </div>
  );
}

export default function CalendarPage() {
  const { zone } = useZone();
  const [windowIdx, setWindowIdx] = useState(2);
  const [minImp, setMinImp] = useState(1);
  const [tab, setTab] = useState<"upcoming" | "past" | "all">("upcoming");

  const win = WINDOWS[windowIdx];
  const now = useMemo(() => new Date(), []);

  const { data, isLoading } = useQuery({
    queryKey: ["calendar", zone, win.days_back, win.days_ahead],
    queryFn: () => api.calendar([zone, "EU", "US"].slice(0, 3), win.days_back, win.days_ahead),
    staleTime: 1000 * 60 * 15,
    refetchInterval: 1000 * 60 * 5,
  });

  const allEvents  = (data?.events ?? []).filter((e) => e.importance >= minImp);
  const upcoming   = allEvents.filter((e) => new Date(e.date_utc) >= now);
  const past       = allEvents.filter((e) => new Date(e.date_utc) < now).reverse();
  const displayed  = tab === "upcoming" ? upcoming : tab === "past" ? past : allEvents;

  const nextKey = upcoming.find((e) => e.importance >= 2) ?? upcoming[0] ?? null;
  const groups  = groupByDay(displayed);

  return (
    <div className="p-6 max-w-screen-xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
          <Calendar size={16} className="text-accent" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-primary">Economic Calendar</h1>
          <p className="text-[11px] text-muted mt-0.5">Macro releases & central bank events</p>
        </div>
      </div>

      {/* Next key event banner */}
      {!isLoading && nextKey && tab === "upcoming" && (
        <NextEventBanner event={nextKey} now={now} />
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        {WINDOWS.map((w, i) => (
          <button
            key={w.label}
            onClick={() => setWindowIdx(i)}
            className={clsx(
              "px-3 py-1.5 text-xs rounded-lg border transition-colors",
              i === windowIdx
                ? "bg-accent/10 border-accent/30 text-accent font-medium"
                : "border-subtle text-secondary hover:text-primary hover:bg-white/[0.04]"
            )}
          >
            {w.label}
          </button>
        ))}

        <div className="ml-auto flex items-center gap-1.5">
          <span className="text-[10px] text-muted mr-1">Impact:</span>
          {[1, 2, 3].map((imp) => (
            <button
              key={imp}
              onClick={() => setMinImp(imp)}
              className={clsx(
                "px-2.5 py-1.5 text-xs rounded-lg border transition-colors",
                imp === minImp
                  ? "bg-white/[0.08] border-white/20 text-primary"
                  : "border-subtle text-secondary hover:text-primary"
              )}
            >
              {imp === 1 ? "All" : imp === 2 ? "Medium+" : "High only"}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b border-subtle mb-4">
        {(["upcoming", "past", "all"] as const).map((t) => {
          const count = t === "upcoming" ? upcoming.length : t === "past" ? past.length : allEvents.length;
          return (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={clsx(
                "px-4 py-2.5 text-sm font-medium capitalize border-b-2 -mb-px transition-colors",
                t === tab ? "border-accent text-primary" : "border-transparent text-secondary hover:text-primary"
              )}
            >
              {t}
              <span className={clsx("ml-1.5 text-xs", t === tab ? "text-accent" : "text-muted")}>{count}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <Loader2 size={24} className="animate-spin text-accent" />
        </div>
      ) : displayed.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-secondary text-sm">
          No events found for this selection.
        </div>
      ) : (
        <div className="space-y-5">
          {groups.map(([dayKey, events]) => (
            <div key={dayKey}>
              {/* Day header */}
              <div className="flex items-center gap-3 mb-2">
                <span className={clsx(
                  "text-[11px] font-semibold uppercase tracking-widest",
                  dayLabel(dayKey + "T00:00:00Z", now) === "Today"
                    ? "text-accent"
                    : dayLabel(dayKey + "T00:00:00Z", now) === "Tomorrow"
                    ? "text-primary"
                    : "text-muted"
                )}>
                  {dayLabel(dayKey + "T00:00:00Z", now)}
                </span>
                <div className="flex-1 h-px bg-subtle/50" />
                <span className="text-[10px] text-muted/50 tabular">{events.length} event{events.length !== 1 ? "s" : ""}</span>
              </div>

              {/* Column headers — show once per group */}
              <div className="flex items-center gap-3 px-4 pb-1 text-[9px] font-semibold text-muted uppercase tracking-widest">
                <div className="w-1.5 shrink-0" />
                <span className="w-16 shrink-0">Time</span>
                <span className="w-16 shrink-0">Rel.</span>
                <span className="w-24 shrink-0">Country</span>
                <span className="flex-1">Event</span>
                <div className="flex gap-4 shrink-0">
                  <span className="w-16 text-right">Prev.</span>
                  <span className="w-16 text-right">Fcst</span>
                  <span className="w-16 text-right">Actual</span>
                </div>
              </div>

              {/* Events */}
              <div className="rounded-xl border border-subtle overflow-hidden bg-card">
                {events.map((ev, i) => (
                  <EventRow key={`${ev.date_utc}-${ev.event}-${i}`} event={ev} now={now} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
