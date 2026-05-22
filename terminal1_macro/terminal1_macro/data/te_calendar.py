import requests
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from terminal1_macro.data.settings import settings

BASE_URL = "https://api.tradingeconomics.com/calendar"

COUNTRY_MAP = {
    "US": ["United States"],
    "EU": ["Euro Area", "Germany", "France"],
    "ASIA": ["China", "Japan", "India", "South Korea"],
}

IMPORTANCE_LABEL = {1: "Low", 2: "Medium", 3: "High"}
IMPORTANCE_COLOR = {1: "🟢", 2: "🟡", 3: "🔴"}


@st.cache_data(ttl=900)
def fetch_te_calendar(countries: list[str], d1: str, d2: str) -> pd.DataFrame | None:
    api_key = settings.trading_economics_api_key
    if not api_key:
        return None

    all_rows = []
    for country in countries:
        country_slug = country.replace(" ", "%20")
        url = f"{BASE_URL}/country/{country_slug}/{d1}/{d2}"
        try:
            resp = requests.get(url, params={"c": api_key, "f": "json"}, timeout=10)
            if resp.status_code == 401:
                # Calendar not included in current TE subscription
                return None
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    all_rows.extend(data)
        except Exception:
            continue

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)

    rename = {
        "Date": "date_utc",
        "Country": "country",
        "Category": "category",
        "Event": "event",
        "Reference": "reference",
        "Actual": "actual",
        "Previous": "previous",
        "Forecast": "forecast",
        "TEForecast": "te_forecast",
        "Importance": "importance",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if "date_utc" in df.columns:
        df["date_utc"] = pd.to_datetime(df["date_utc"], utc=True, errors="coerce")
        df = df.dropna(subset=["date_utc"])
        df = df.sort_values("date_utc")

    if "importance" in df.columns:
        df["importance"] = pd.to_numeric(df["importance"], errors="coerce").fillna(1).astype(int)
        df["importance_label"] = df["importance"].map(IMPORTANCE_LABEL)
        df["importance_icon"] = df["importance"].map(IMPORTANCE_COLOR)

    df["source"] = "Trading Economics"
    return df


def get_calendar_for_zones(zones: list[str], days_back: int = 3, days_ahead: int = 14) -> pd.DataFrame | None:
    countries = []
    for zone in zones:
        countries.extend(COUNTRY_MAP.get(zone, []))

    if not countries:
        return None

    d1 = (date.today() - timedelta(days=days_back)).isoformat()
    d2 = (date.today() + timedelta(days=days_ahead)).isoformat()

    return fetch_te_calendar(tuple(countries), d1, d2)
