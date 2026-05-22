import os
import requests
import pandas as pd
from backend.cache import ttl_cache
from backend import db as _db

_mem: dict[str, list[dict]] = {}  # L1 in-process cache

BASE_URL = "https://api.stlouisfed.org/fred"
_API_KEY = os.getenv("FRED_API_KEY", "fde5589cb6f49add72064defa1643452")

RELEASE_TIMES: dict[str, str] = {
    "Employment Situation (NFP)": "13:30",
    "CPI": "13:30",
    "GDP": "13:30",
    "Personal Income & PCE": "13:30",
    "PPI": "13:30",
    "Retail Sales": "13:30",
    "Housing Starts": "13:30",
    "Trade Balance": "13:30",
    "Jobless Claims": "13:30",
    "Durable Goods": "13:30",
    "PCE": "13:30",
    "Industrial Production": "14:15",
    "FOMC": "19:00",
    "New Home Sales": "15:00",
    "Existing Home Sales": "15:00",
    "Consumer Sentiment": "15:00",
    "ISM": "15:00",
    "HICP Inflation": "10:00",
    "ECB Interest Rates": "13:15",
}

IMPORTANCE_RULES: list[tuple[str, int, str | None, str]] = [
    ("Employment Situation", 3, "Employment Situation (NFP)", "United States"),
    ("Consumer Price Index", 3, "CPI", "United States"),
    ("Gross Domestic Product", 3, "GDP", "United States"),
    ("Personal Income and Outlays", 3, "Personal Income & PCE", "United States"),
    ("FOMC", 3, None, "United States"),
    ("Producer Price Index", 3, "PPI", "United States"),
    ("Advance Retail", 3, "Retail Sales", "United States"),
    ("Industrial Production", 2, "Industrial Production", "United States"),
    ("Housing Starts", 2, "Housing Starts", "United States"),
    ("Trade Balance", 2, "Trade Balance", "United States"),
    ("Unemployment Insurance", 2, "Jobless Claims", "United States"),
    ("Consumer Sentiment", 2, "Consumer Sentiment", "United States"),
    ("ISM", 2, None, "United States"),
    ("PCE", 2, "PCE", "United States"),
    ("Durable Goods", 2, "Durable Goods", "United States"),
    ("New Home", 2, "New Home Sales", "United States"),
    ("Existing Home", 2, "Existing Home Sales", "United States"),
    ("HICP", 2, "HICP Inflation", "Euro Area"),
    ("Key ECB", 2, "ECB Interest Rates", "Euro Area"),
    ("Euro Area", 1, None, "Euro Area"),
]

ALWAYS_HIDE = {
    "Coinbase", "Tri-Party", "SOFR", "SONIA", "AMERIBOR", "Moody",
    "Nasdaq Daily", "Nikkei", "Optimal Blue", "Temporary Open Market",
    "Arbitrage-Free", "Quits and Layoffs", "Unemployment in States",
}

SERIES_FOR_EVENT: dict[str, str] = {
    "Employment Situation (NFP)": "PAYEMS",
    "CPI": "CPIAUCSL",
    "GDP": "GDPC1",
    "Personal Income & PCE": "PCEPI",
    "PPI": "PPIACO",
    "Retail Sales": "RSXFS",
    "Jobless Claims": "ICSA",
    "Industrial Production": "INDPRO",
    "Consumer Sentiment": "UMCSENT",
    "FOMC": "FEDFUNDS",
    "PCE": "PCEPI",
    "Durable Goods": "DGORDER",
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


def fetch_historical(series_id: str) -> list[dict] | None:
    # L1: in-process memory
    if series_id in _mem:
        return _mem[series_id]
    # L2: DuckDB persistent cache
    cached = _db.get_cached(series_id, max_age_hours=1)
    if cached is not None:
        _mem[series_id] = cached
        return cached
    # L3: FRED API
    resp = requests.get(
        f"{BASE_URL}/series/observations",
        params={"series_id": series_id, "api_key": _API_KEY, "file_type": "json"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    obs = resp.json().get("observations", [])
    rows = []
    for o in obs:
        try:
            v = float(o["value"])
            rows.append({"date": o["date"], "value": v})
        except (ValueError, KeyError):
            continue
    if rows:
        _mem[series_id] = rows
        _db.set_cached(series_id, rows)
    return rows or None


@ttl_cache(seconds=3600)
def _fetch_tail(series_id: str, n: int = 2) -> list[float]:
    try:
        resp = requests.get(
            f"{BASE_URL}/series/observations",
            params={
                "series_id": series_id,
                "api_key": _API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": n,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        return [float(o["value"]) for o in resp.json().get("observations", [])
                if o.get("value") not in (".", None, "")]
    except Exception:
        return []


@ttl_cache(seconds=3600)
def fetch_calendar(days_back: int = 3, days_ahead: int = 14) -> list[dict]:
    from datetime import date, timedelta
    d1 = (date.today() - timedelta(days=days_back)).isoformat()
    d2 = (date.today() + timedelta(days=days_ahead)).isoformat()
    try:
        resp = requests.get(
            f"{BASE_URL}/releases/dates",
            params={
                "api_key": _API_KEY,
                "file_type": "json",
                "realtime_start": d1,
                "realtime_end": d2,
                "include_release_dates_with_no_data": "false",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        items = resp.json().get("release_dates", [])
    except Exception:
        return []

    actuals: dict[str, dict] = {}
    for event_name, sid in SERIES_FOR_EVENT.items():
        vals = _fetch_tail(sid, 2)
        if vals:
            actuals[event_name] = {
                "actual": round(vals[0], 2) if vals else None,
                "previous": round(vals[1], 2) if len(vals) > 1 else None,
            }

    rows = []
    seen: set = set()
    for item in items:
        name = item.get("release_name", "")
        if _should_hide(name):
            continue
        imp, imp_label, imp_icon, display_name, country = _classify(name)
        import pandas as pd
        dt = pd.to_datetime(item["date"])
        week_key = (display_name, dt.isocalendar()[:2])
        if week_key in seen:
            continue
        seen.add(week_key)

        release_time = RELEASE_TIMES.get(display_name)
        if release_time:
            h, m = map(int, release_time.split(":"))
            date_utc = f"{item['date']}T{release_time}:00Z"
        else:
            date_utc = f"{item['date']}T00:00:00Z"

        ev = actuals.get(display_name, {})
        rows.append({
            "date_utc": date_utc,
            "country": country,
            "event": display_name,
            "importance": imp,
            "importance_label": imp_label,
            "importance_icon": imp_icon,
            "actual": ev.get("actual"),
            "previous": ev.get("previous"),
            "forecast": None,
            "source": "FRED",
        })

    return sorted(rows, key=lambda r: r["date_utc"])
