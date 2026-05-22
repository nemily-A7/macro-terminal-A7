import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TrendingUp, Percent, Users, BarChart2, Banknote, Activity } from "lucide-react";
import { ZoneProvider } from "./contexts/ZoneContext";
import Layout from "./components/Layout";
import Overview from "./pages/Overview";
import CategoryPage from "./pages/CategoryPage";
import CalendarPage from "./pages/CalendarPage";
import MarketsPage from "./pages/MarketsPage";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});

const CATEGORY_ROUTES = [
  { path: "inflation", category: "Inflation" as const,      label: "Inflation",        color: "#f59e0b", icon: <TrendingUp size={16} /> },
  { path: "rates",     category: "Rates" as const,          label: "Interest Rates",   color: "#3b82f6", icon: <Percent size={16} /> },
  { path: "labor",     category: "Labor" as const,          label: "Labor Market",     color: "#8b5cf6", icon: <Users size={16} /> },
  { path: "growth",    category: "Growth" as const,         label: "Economic Growth",  color: "#22c55e", icon: <BarChart2 size={16} /> },
  { path: "money",     category: "Money_Credit" as const,   label: "Money & Credit",   color: "#06b6d4", icon: <Banknote size={16} /> },
  { path: "risk",      category: "Risk_Sentiment" as const, label: "Risk & Sentiment", color: "#ef4444", icon: <Activity size={16} /> },
];

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <ZoneProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route index element={<Overview />} />
              {CATEGORY_ROUTES.map(({ path, ...props }) => (
                <Route key={path} path={path} element={<CategoryPage {...props} />} />
              ))}
              <Route path="calendar" element={<CalendarPage />} />
              <Route path="markets" element={<MarketsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ZoneProvider>
    </QueryClientProvider>
  );
}
