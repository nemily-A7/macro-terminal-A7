import requests
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from terminal1_macro.data.settings import settings

BASE_URL = "https://api.stlouisfed.org/fred"

# (keyword_in_name, importance, display_label, country)
IMPORTANCE_RULES: list[tuple[str, int, str | None, str]] = [
    ("Employment Situation",        3, "Employment Situation (NFP)", "United States"),
    ("Consumer Price Index",        3, "CPI",                        "United States"),
    ("Gross Domestic Product",      3, "GDP",                        "United States"),
    ("Personal Income and Outlays", 3, "Personal Income & PCE",      "United States"),
    ("FOMC",                        3, None,                         "United States"),
    ("Producer Price Index",        3, "PPI",                        "United States"),
    ("Advance Retail",              3, "Retail Sales",               "United States"),
    ("Industrial Production",       2, "Industrial Production",      "United States"),
    ("Housing Starts",              2, "Housing Starts",             "United States"),
    ("Trade Balance",               2, "Trade Balance",              "United States"),
    ("Unemployment Insurance",      2, "Jobless Claims",             "United States"),
    ("Consumer Sentiment",          2, "Consumer Sentiment",         "United States"),
    ("Chicago Fed",                 2, None,                         "United States"),
    ("ISM",                         2, None,                         "United States"),
    ("PCE",                         2, "PCE",                        "United States"),
    ("Durable Goods",               2, "Durable Goods",              "United States"),
    ("New Home",                    2, "New Home Sales",             "United States"),
    ("Existing Home",               2, "Existing Home Sales",        "United States"),
    # EU events tracked by FRED
    ("HICP",                        2, "HICP Inflation",             "Euro Area"),
    ("Key ECB",                     2, "ECB Interest Rates",         "Euro Area"),
    ("Euro Area",                   1, None,                         "Euro Area"),
]

ALWAYS_HIDE = {
    "Coinbase", "Tri-Party", "SOFR", "SONIA", "AMERIBOR", "Moody",
    "Nasdaq Daily", "Nikkei", "Optimal Blue", "Temporary Open Market",
    "Arbitrage-Free", "Quits and Layoffs", "Unemployment in States",
}

# Known UTC release times (HH:MM) for common events
RELEASE_TIMES: dict[str, str] = {
    "Employment Situation (NFP)": "13:30",
    "CPI":                        "13:30",
    "GDP":                        "13:30",
    "Personal Income & PCE":      "13:30",
    "PPI":                        "13:30",
    "Retail Sales":               "13:30",
    "Housing Starts":             "13:30",
    "Trade Balance":              "13:30",
    "Jobless Claims":             "13:30",
    "Durable Goods":              "13:30",
    "PCE":                        "13:30",
    "Industrial Production":      "14:15",
    "FOMC":                       "19:00",
    "New Home Sales":             "15:00",
    "Existing Home Sales":        "15:00",
    "Consumer Sentiment":         "15:00",
    "ISM":                        "15:00",
    "HICP Inflation":             "10:00",
    "ECB Interest Rates":         "13:15",
}

# FRED series to fetch actual + previous for known events
SERIES_FOR_EVENT: dict[str, str] = {
    "Employment Situation (NFP)": "PAYEMS",
    "CPI":                        "CPIAUCSL",
    "GDP":                        "GDPC1",
    "Personal Income & PCE":      "PCEPI",
    "PPI":                        "PPIACO",
    "Retail Sales":               "RSXFS",
    "Jobless Claims":             "ICSA",
    "Industrial Production":      "INDPRO",
    "Consumer Sentiment":         "UMCSENT",
    "FOMC":                       "FEDFUNDS",
    "PCE":                        "PCEPI",
    "Durable Goods":              "DGORDER",
}


def _classify(name: str) -> tuple[int, str, str, str, str]:
    for keyword, importance, label, country in IMPORTANCE_RULES:
        if keyword.lower() in name.lower():
            display = label if label else name
            icon = "🔴" if importance == 3 else ("🟡" if importance == 2 else "🟢")
            label_str = {3: "High", 2: "Medium", 1: "Low"}[importance]
            return importance, label_str, icon, display, country
    return 1, "Low", "🟢", name, "United States"


def _should_hide(name: str) -> bool:
    return any(h.lower() in name.lower() for h in ALWAYS_HIDE)


@st.cache_data(ttl=3600)
def _fetch_series_tail(series_id: str, api_key: str, n: int = 2) -> list[float]:
    """Return the last n observed values for a FRED series, newest first."""
    try:
        resp = requests.get(
            f"{BASE_URL}/series/observations",
            params={
                "api_key": api_key,
                "file_type": "json",
                "series_id": series_id,
                "sort_order": "desc",
                "limit": n,
                "output_type": 1,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        obs = resp.json().get("observations", [])
        return [float(o["value"]) for o in obs if o.get("value") not in (".", None, "")]
    except Exception:
        return []


@st.cache_data(ttl=3600)
def _build_actuals_map(api_key: str) -> dict[str, dict]:
    """Fetch actual + previous for each event that has a known FRED series."""
    result: dict[str, dict] = {}
    for event_name, series_id in SERIES_FOR_EVENT.items():
        vals = _fetch_series_tail(series_id, api_key, n=2)
        if vals:
            result[event_name] = {
                "actual":   round(vals[0], 2) if len(vals) > 0 else None,
                "previous": round(vals[1], 2) if len(vals) > 1 else None,
            }
    return result


@st.cache_data(ttl=3600)
def fetch_fred_release_dates(days_back: int = 3, days_ahead: int = 21) -> pd.DataFrame | None:
    api_key = settings.fred_api_key
    if not api_key:
        return None

    d1 = (date.today() - timedelta(days=days_back)).isoformat()
    d2 = (date.today() + timedelta(days=days_ahead)).isoformat()

    try:
        resp = requests.get(
            f"{BASE_URL}/releases/dates",
            params={
                "api_key": api_key,
                "file_type": "json",
                "realtime_start": d1,
                "realtime_end": d2,
                "include_release_dates_with_no_data": "false",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None

        items = resp.json().get("release_dates", [])
        if not items:
            return None

        actuals = _build_actuals_map(api_key)

        rows = []
        seen = set()
        for item in items:
            name = item.get("release_name", "")
            if _should_hide(name):
                continue

            imp, imp_label, imp_icon, display_name, country = _classify(name)
            dt = pd.to_datetime(item["date"])
            week_key = (display_name, dt.isocalendar()[:2])
            if week_key in seen:
                continue
            seen.add(week_key)

            # Apply known UTC release time
            release_time = RELEASE_TIMES.get(display_name)
            if release_time:
                h, m = map(int, release_time.split(":"))
                date_utc = pd.Timestamp(item["date"], tz="UTC").replace(hour=h, minute=m)
            else:
                date_utc = pd.Timestamp(item["date"], tz="UTC")

            ev_actuals = actuals.get(display_name, {})

            rows.append({
                "date_utc":         date_utc,
                "country":          country,
                "event":            display_name,
                "category":         "Release",
                "actual":           ev_actuals.get("actual"),
                "previous":         ev_actuals.get("previous"),
                "forecast":         None,
                "importance":       imp,
                "importance_label": imp_label,
                "importance_icon":  imp_icon,
                "source":           "FRED",
            })

        if not rows:
            return None

        return pd.DataFrame(rows).sort_values("date_utc")

    except Exception:
        return None
