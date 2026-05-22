import requests
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from terminal1_macro.data.settings import settings

BASE_URL = "https://api.tradingeconomics.com"

@st.cache_data(ttl=3600)
def fetch_te_historical(country: str, indicator: str) -> pd.DataFrame | None:
    """
    Fetch historical data for a country/indicator from TradingEconomics.
    """
    api_key = settings.trading_economics_api_key
    if not api_key:
        return None
        
    # URL Format: /historical/country/{country}/indicator/{indicator}
    # Using 'guest:guest' style auth in parameter c? Check .env format
    # The .env check showed 'key:secret' format usually for 'c' param.
    
    # Clean country name (TE is picky?)
    # Usually standard English names work. "Euro Area", "China", etc.
    
    url = f"{BASE_URL}/historical/country/{country}/indicator/{indicator}"
    params = {
        "c": api_key,
        "f": "json",
        "d1": "1950-01-01" # Max history per user request
    }
    
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                df = pd.DataFrame(data)
                if not df.empty:
                    df["observation_time"] = pd.to_datetime(df["DateTime"])
                    df["value"] = pd.to_numeric(df["Value"], errors="coerce")
                    df = df.sort_values("observation_time", ascending=False)
                    return df[["observation_time", "value"]]
        return None
    except Exception:
        return None

def get_te_latest_value(df: pd.DataFrame | None) -> dict | None:
    if df is None or df.empty:
        return None
    row = df.iloc[0]
    return {"date": row["observation_time"], "value": row["value"]}
