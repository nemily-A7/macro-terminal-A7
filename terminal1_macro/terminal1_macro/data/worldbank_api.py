import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.worldbank.org/v2/country"

COUNTRY_ISO = {
    # ASIA
    "China": "CHN",
    "Japan": "JPN",
    "India": "IND",
    "South Korea": "KOR",
    "Singapore": "SGP",
    "Australia": "AUS",
    # EU countries
    "Euro Area": "EMU",
    "Germany": "DEU",
    "France": "FRA",
    "Italy": "ITA",
    "Spain": "ESP",
    "Netherlands": "NLD",
    # US
    "United States": "USA",
}


@st.cache_data(ttl=3600 * 12)
def fetch_worldbank(country_name: str, indicator: str) -> pd.DataFrame | None:
    iso = COUNTRY_ISO.get(country_name)
    if not iso:
        return None

    url = f"{BASE_URL}/{iso}/indicator/{indicator}"
    params = {"format": "json", "per_page": 60, "mrv": 60}
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            return None

        payload = resp.json()
        if not payload or len(payload) < 2 or not payload[1]:
            return None

        rows = []
        for obs in payload[1]:
            if obs.get("value") is not None:
                year = obs["date"]
                rows.append({
                    "observation_time": pd.to_datetime(f"{year}-12-31"),
                    "value": float(obs["value"]),
                })

        if not rows:
            return None

        df = pd.DataFrame(rows).sort_values("observation_time", ascending=False)
        return df[["observation_time", "value"]]
    except Exception:
        return None


def get_worldbank_latest_value(df: pd.DataFrame | None) -> dict | None:
    if df is None or df.empty:
        return None
    row = df.iloc[0]
    return {"date": row["observation_time"], "value": row["value"]}
