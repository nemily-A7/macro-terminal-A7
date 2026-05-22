import type { Zone, IndicatorData, CalendarEvent, MarketData, DataPoint } from "../types";

const BASE = "http://localhost:8001/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  zones: (): Promise<{ zones: Zone[] }> =>
    get("/zones"),

  zoneIndicators: (zone: string, country?: string): Promise<{ indicators: IndicatorData[]; country: string }> =>
    get(`/zone/${zone}/indicators${country ? `?country=${encodeURIComponent(country)}` : ""}`),

  categoryIndicators: (zone: string, category: string, country?: string): Promise<{ indicators: IndicatorData[] }> =>
    get(`/zone/${zone}/category/${category}${country ? `?country=${encodeURIComponent(country)}` : ""}`),

  calendar: (zones: string[], days_back = 3, days_ahead = 14): Promise<{ events: CalendarEvent[] }> =>
    get(`/calendar?zones=${zones.join(",")}&days_back=${days_back}&days_ahead=${days_ahead}`),

  markets: (): Promise<{ markets: MarketData[] }> =>
    get("/markets"),

  recessions: (): Promise<{ bands: { start: string; end: string }[] }> =>
    get("/recessions"),

  narrative: (zone: string, country?: string): Promise<{ narrative: string; cached: boolean; no_key?: boolean }> =>
    get(`/zone/${zone}/narrative${country ? `?country=${encodeURIComponent(country)}` : ""}`),

  indicatorInsight: (zone: string, key: string, country?: string): Promise<{
    description: string | null;
    interpretation: string | null;
    no_key: boolean;
    cached: boolean;
  }> =>
    get(`/zone/${zone}/indicator/${key}/insight${country ? `?country=${encodeURIComponent(country)}` : ""}`),

  indicatorCompare: (zone: string, indicatorKey: string): Promise<{
    display_name: string;
    unit: string;
    transform_default: string;
    series: { country: string; history: DataPoint[]; history_transformed?: DataPoint[]; latest: DataPoint | null; delta: number | null }[];
  }> =>
    get(`/zone/${zone}/indicator/${indicatorKey}/compare`),
};
