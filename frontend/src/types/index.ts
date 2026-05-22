export interface Zone {
  key: string;
  label: string;
  countries: string[];
  default_country: string;
}

export interface DataPoint {
  date: string;
  value: number | null;
}

export interface IndicatorData {
  key: string;
  display_name: string;
  category: string;
  region: string;
  source: string;
  unit: string;
  frequency: string;
  transform_default: "yoy" | "mom" | "level";
  priority: number;
  history: DataPoint[];
  history_transformed?: DataPoint[];
  latest: DataPoint | null;
  latest_raw: DataPoint | null;
  delta: number | null;
  transform: string;
}

export type AssetClass = "equity" | "fx" | "commodity" | "crypto" | "other";

export type MarketZone = "GLOBAL" | "US" | "EU" | "ASIA";

export interface MarketData {
  key: string;
  display_name: string;
  unit: string;
  frequency: string;
  asset_class: AssetClass;
  market_zone: MarketZone;
  priority: number;
  history: DataPoint[];
  history_transformed?: DataPoint[];
  latest: DataPoint | null;
  latest_raw: DataPoint | null;
  delta: number | null;
  transform: string;
  // Live fields — null when key not configured or market closed
  live_price: number | null;
  live_pct_change: number | null;
  live_change: number | null;
  live_prev_close: number | null;
  is_market_open: boolean | null;
  live_datetime: string | null;
  live_source: "twelvedata" | "yahoo" | "fred";
}

export interface CalendarEvent {
  date_utc: string;
  country: string;
  event: string;
  importance: 1 | 2 | 3;
  importance_label: "Low" | "Medium" | "High";
  importance_icon: string;
  actual: number | null;
  previous: number | null;
  forecast: number | null;
  source: string;
}

export const CATEGORIES = [
  { key: "Inflation",      label: "Inflation" },
  { key: "Rates",          label: "Rates" },
  { key: "Labor",          label: "Labor" },
  { key: "Growth",         label: "Growth" },
  { key: "Money_Credit",   label: "Money & Credit" },
  { key: "Risk_Sentiment", label: "Risk & Sentiment" },
] as const;

export type CategoryKey = typeof CATEGORIES[number]["key"];
