import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

@st.cache_data(ttl=3600 * 6)
def fetch_eurostat(dataset_id: str, filters: dict) -> pd.DataFrame | None:
    """
    Fetch data from Eurostat JSON API.
    filters: e.g. {"geo": "EA", "s_adj": "SA", "age": "TOTAL", "sex": "T", "unit": "PC_ACT"}
    """
    params = {**filters, "lang": "en", "sinceTimePeriod": "2000-01"}
    try:
        resp = requests.get(f"{BASE_URL}/{dataset_id}", params=params, timeout=15)
        if resp.status_code != 200:
            return None

        data = resp.json()
        time_index = data["dimension"]["time"]["category"]["index"]
        values = data.get("value", {})

        rows = []
        for period, pos in time_index.items():
            val = values.get(str(pos))
            if val is not None:
                rows.append({"observation_time": pd.to_datetime(period), "value": float(val)})

        if not rows:
            return None

        df = pd.DataFrame(rows).sort_values("observation_time", ascending=False)
        return df[["observation_time", "value"]]
    except Exception:
        return None


def get_eurostat_latest_value(df: pd.DataFrame | None) -> dict | None:
    if df is None or df.empty:
        return None
    row = df.iloc[0]
    return {"date": row["observation_time"], "value": row["value"]}
