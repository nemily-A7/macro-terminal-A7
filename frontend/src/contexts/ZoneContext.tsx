import { createContext, useContext, useState, useEffect, useRef, ReactNode } from "react";
import type { Zone } from "../types";

export interface LiveValue {
  value: number | null;
  delta: number | null;
  date: string;
}

export interface LiveMarketQuote {
  price: number;
  pct_change: number;
  change: number;
  is_market_open: boolean;
  datetime: string;
  received_at: number; // Date.now() when the WS message arrived
}

interface ZoneCtx {
  zone: string;
  country: string | null;
  zones: Zone[];
  liveData: Map<string, LiveValue>;
  liveMarkets: Map<string, LiveMarketQuote>;
  wsReady: boolean;
  setZone: (z: string) => void;
  setCountry: (c: string) => void;
  setZones: (z: Zone[]) => void;
}

const ZoneContext = createContext<ZoneCtx>({
  zone: "US",
  country: null,
  zones: [],
  liveData: new Map(),
  liveMarkets: new Map(),
  wsReady: false,
  setZone: () => {},
  setCountry: () => {},
  setZones: () => {},
});

export function ZoneProvider({ children }: { children: ReactNode }) {
  const [zone, setZoneState]           = useState("US");
  const [country, setCountryState]     = useState<string | null>(null);
  const [zones, setZones]             = useState<Zone[]>([]);
  const [liveData, setLiveData]       = useState<Map<string, LiveValue>>(new Map());
  const [liveMarkets, setLiveMarkets] = useState<Map<string, LiveMarketQuote>>(new Map());
  const [wsReady, setWsReady]         = useState(false);
  const wsRef    = useRef<WebSocket | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const setZone    = (z: string) => { setZoneState(z); setCountryState(null); setLiveData(new Map()); };
  const setCountry = (c: string) => { setCountryState(c); setLiveData(new Map()); };

  const currentZone      = zones.find((z) => z.key === zone);
  const resolvedCountry  = country ?? currentZone?.default_country ?? null;

  useEffect(() => {
    if (!zone) return;
    let dead = false;

    function connect() {
      if (dead) return;
      const params = new URLSearchParams({ zone });
      if (resolvedCountry) params.set("country", resolvedCountry);
      const ws = new WebSocket(`ws://localhost:8001/ws/live?${params}`);
      wsRef.current = ws;

      ws.onopen = () => setWsReady(true);

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data) as {
            type: string;
            indicators?: { key: string; value: number | null; delta: number | null; date: string }[];
            market_prices?: Record<string, Omit<LiveMarketQuote, "received_at">>;
          };

          if (msg.type !== "snapshot") return;

          // Update macro indicator live values
          if (msg.indicators) {
            const map = new Map<string, LiveValue>();
            for (const ind of msg.indicators) {
              if (ind.value != null) {
                map.set(ind.key, { value: ind.value, delta: ind.delta, date: ind.date });
              }
            }
            setLiveData(map);
          }

          // Update live market quotes
          if (msg.market_prices && Object.keys(msg.market_prices).length > 0) {
            const now = Date.now();
            const mmap = new Map<string, LiveMarketQuote>();
            for (const [key, q] of Object.entries(msg.market_prices)) {
              mmap.set(key, { ...q, received_at: now });
            }
            setLiveMarkets(mmap);
          }
        } catch { /* ignore parse errors */ }
      };

      ws.onclose = () => {
        setWsReady(false);
        if (!dead) timerRef.current = setTimeout(connect, 15000);
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      dead = true;
      if (timerRef.current) clearTimeout(timerRef.current);
      wsRef.current?.close();
      wsRef.current = null;
      setWsReady(false);
    };
  }, [zone, resolvedCountry]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <ZoneContext.Provider value={{ zone, country, zones, liveData, liveMarkets, wsReady, setZone, setCountry, setZones }}>
      {children}
    </ZoneContext.Provider>
  );
}

export const useZone = () => useContext(ZoneContext);
