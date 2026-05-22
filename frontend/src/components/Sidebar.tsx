import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, TrendingUp, Percent, Users,
  BarChart2, Banknote, Activity, Calendar, ChevronDown, Globe2,
} from "lucide-react";
import { useZone } from "../contexts/ZoneContext";
import { useState } from "react";
import clsx from "clsx";

const NAV_MACRO = [
  { to: "/",          label: "Overview",         icon: LayoutDashboard },
  { to: "/inflation", label: "Inflation",         icon: TrendingUp },
  { to: "/rates",     label: "Rates",             icon: Percent },
  { to: "/labor",     label: "Labor",             icon: Users },
  { to: "/growth",    label: "Growth",            icon: BarChart2 },
  { to: "/money",     label: "Money & Credit",    icon: Banknote },
  { to: "/risk",      label: "Risk & Sentiment",  icon: Activity },
];

const NAV_GLOBAL = [
  { to: "/markets",  label: "Markets",  icon: Globe2 },
  { to: "/calendar", label: "Calendar", icon: Calendar },
];

const ZONES = [
  { key: "US",   label: "US",   flag: "🇺🇸" },
  { key: "EU",   label: "EU",   flag: "🇪🇺" },
  { key: "ASIA", label: "Asia", flag: "🌏" },
];

export default function Sidebar() {
  const { zone, country, zones, setZone, setCountry } = useZone();
  const [countryOpen, setCountryOpen] = useState(false);

  const currentZone = zones.find((z) => z.key === zone);
  const countries = currentZone?.countries ?? [];
  const displayCountry = country ?? currentZone?.default_country;

  return (
    <aside className="flex flex-col w-52 min-h-screen shrink-0 border-r border-subtle bg-surface">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 h-13 py-3.5 border-b border-subtle">
        <div className="w-6 h-6 rounded-md bg-accent flex items-center justify-center shrink-0">
          <BarChart2 size={12} className="text-white" />
        </div>
        <span className="font-semibold text-[13px] tracking-tight text-primary">Macro Terminal</span>
      </div>

      {/* Zone tabs — prominent at top */}
      <div className="px-3 pt-3 pb-2">
        <p className="text-[10px] font-semibold text-muted uppercase tracking-widest mb-2 px-1">Region</p>
        <div className="flex gap-1 p-1 bg-card rounded-lg border border-subtle">
          {ZONES.map((z) => (
            <button
              key={z.key}
              onClick={() => { setZone(z.key); setCountryOpen(false); }}
              className={clsx(
                "flex-1 flex items-center justify-center gap-1 py-1.5 rounded-md text-xs font-medium transition-all duration-150",
                zone === z.key
                  ? "bg-accent text-white shadow-sm"
                  : "text-secondary hover:text-primary hover:bg-white/[0.05]"
              )}
            >
              <span>{z.flag}</span>
              <span>{z.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Country picker — only for multi-country zones */}
      {countries.length > 1 && (
        <div className="px-3 pb-3">
          <div className="relative">
            <button
              onClick={() => setCountryOpen((o) => !o)}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-subtle text-xs text-secondary hover:text-primary hover:border-white/[0.14] transition-all"
            >
              <span className="flex-1 text-left truncate">{displayCountry}</span>
              <ChevronDown size={11} className={clsx("shrink-0 transition-transform duration-150", countryOpen && "rotate-180")} />
            </button>
            {countryOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-subtle rounded-lg shadow-2xl z-50 overflow-hidden">
                {countries.map((c) => (
                  <button
                    key={c}
                    onClick={() => { setCountry(c); setCountryOpen(false); }}
                    className={clsx(
                      "w-full text-left px-3 py-2 text-xs transition-colors",
                      c === displayCountry
                        ? "text-accent bg-accent/10"
                        : "text-secondary hover:text-primary hover:bg-white/[0.05]"
                    )}
                  >
                    {c}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="h-px bg-subtle mx-3 mb-1" style={{ background: "rgba(255,255,255,0.06)" }} />

      {/* Nav — macro section */}
      <nav className="flex-1 px-2 py-2 space-y-0.5 overflow-y-auto">
        <p className="text-[9px] font-semibold text-muted uppercase tracking-widest px-3 pt-1 pb-1.5 opacity-60">Macro</p>
        {NAV_MACRO.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] transition-all duration-100",
                isActive
                  ? "bg-white/[0.07] text-primary font-medium"
                  : "text-secondary hover:bg-white/[0.04] hover:text-primary"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={13} className={clsx("shrink-0", isActive ? "text-accent" : "text-muted")} />
                {label}
              </>
            )}
          </NavLink>
        ))}

        <div className="h-px mx-1 my-2" style={{ background: "rgba(255,255,255,0.06)" }} />
        <p className="text-[9px] font-semibold text-muted uppercase tracking-widest px-3 pb-1.5 opacity-60">Global</p>
        {NAV_GLOBAL.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] transition-all duration-100",
                isActive
                  ? "bg-white/[0.07] text-primary font-medium"
                  : "text-secondary hover:bg-white/[0.04] hover:text-primary"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={13} className={clsx("shrink-0", isActive ? "text-accent" : "text-muted")} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-subtle">
        <p className="text-[10px] text-muted">FRED · ECB · World Bank · OECD</p>
      </div>
    </aside>
  );
}
