import { Outlet, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import { api } from "../api/client";
import { useZone } from "../contexts/ZoneContext";

const PAGE_LABELS: Record<string, string> = {
  "/":          "Overview",
  "/inflation": "Inflation",
  "/rates":     "Interest Rates",
  "/labor":     "Labor Market",
  "/growth":    "Economic Growth",
  "/money":     "Money & Credit",
  "/risk":      "Risk & Sentiment",
  "/markets":   "Global Markets",
  "/calendar":  "Calendar",
};

export default function Layout() {
  const { setZones, zone, country, zones, wsReady } = useZone();
  const location = useLocation();
  const [tick, setTick] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setTick(new Date()), 30000);
    return () => clearInterval(id);
  }, []);

  const { data } = useQuery({
    queryKey: ["zones"],
    queryFn: api.zones,
    staleTime: Infinity,
  });

  useEffect(() => {
    if (data?.zones) setZones(data.zones);
  }, [data]);

  const currentZone   = zones.find((z) => z.key === zone);
  const displayCountry = country ?? currentZone?.default_country;
  const pageLabel      = PAGE_LABELS[location.pathname] ?? "";

  return (
    <div className="flex h-screen overflow-hidden bg-[#0d0d0d]">
      <Sidebar />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Top header */}
        <header className="flex items-center justify-between px-6 h-11 border-b border-subtle shrink-0 bg-surface/50">
          <div className="flex items-center gap-2 text-[12px]">
            <span className="text-muted">{currentZone?.label ?? zone}</span>
            {displayCountry && displayCountry !== currentZone?.label && (
              <>
                <span className="text-muted opacity-40">/</span>
                <span className="text-secondary">{displayCountry}</span>
              </>
            )}
            {pageLabel && (
              <>
                <span className="text-muted opacity-40">/</span>
                <span className="text-primary font-medium">{pageLabel}</span>
              </>
            )}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[10px] text-muted">
              <span className={`w-1.5 h-1.5 rounded-full inline-block transition-colors duration-500 ${wsReady ? "bg-positive animate-pulse" : "bg-muted/40"}`} />
              {wsReady ? "Live" : "Connecting"}
            </div>
            <span className="text-[11px] text-muted">
              {tick.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" })} UTC
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
