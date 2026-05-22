import requests
import pandas as pd
import streamlit as st
from datetime import date
from terminal1_macro.data.settings import settings

BASE_URL = "https://api.stlouisfed.org/fred"

@st.cache_data(ttl=3600)
def fetch_fred_historical(series_id: str) -> pd.DataFrame | None:
    """
    Fetch historical data for a series from FRED.
    """
    api_key = settings.fred_api_key
    if not api_key:
        return None
        
    url = f"{BASE_URL}/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if "observations" in data:
                df = pd.DataFrame(data["observations"])
                if not df.empty:
                    df["observation_time"] = pd.to_datetime(df["date"])
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    # Drop rows with NaN values
                    df = df.dropna(subset=["value"])
                    df = df.sort_values("observation_time", ascending=False)
                    return df[["observation_time", "value"]]
        return None
    except Exception:
        return None

def get_fred_latest_value(df: pd.DataFrame | None) -> dict | None:
    if df is None or df.empty:
        return None
    row = df.iloc[0]
    return {"date": row["observation_time"], "value": row["value"]}
