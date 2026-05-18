import requests
import pandas as pd
import io
import streamlit as st
from datetime import date, timedelta

BASE_URL = "https://data-api.ecb.europa.eu/service/data"

@st.cache_data(ttl=3600*24)
def get_historical_series(flow_ref: str, key: str, start_period: str | None = None, end_period: str | None = None) -> pd.DataFrame | None:
    """
    Fetch data from ECB SDMX API.
    URL Pattern: {BASE_URL}/{flow_ref}/{key}
    """
    url = f"{BASE_URL}/{flow_ref}/{key}"
    
    if not start_period:
        start_period = (date.today() - timedelta(days=365*5)).isoformat()
        
    params = {
        "startPeriod": start_period,
        "format": "csvdata" # CSV implies cleaner parsing than XML
    }
    
    if end_period:
        params["endPeriod"] = end_period
        
    try:
        # ECB requires Accept header for specific formats sometimes, but 'format' query param works too.
        headers = {"Accept": "text/csv"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            # Parse CSV
            # ECB CSV structure: usually TIME_PERIOD, OPS_VALUE, ...
            csv_data = io.StringIO(resp.text)
            df = pd.read_csv(csv_data)
            
            # Identify columns
            # Usually 'TIME_PERIOD' and 'OBS_VALUE'
            if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                df["observation_time"] = pd.to_datetime(df["TIME_PERIOD"])
                df["value"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
                df = df.sort_values("observation_time", ascending=False)
                return df[["observation_time", "value"]]
            
            return None
        else:
            # Log warning?
            # print(f"ECB Error {resp.status_code}: {resp.text}")
            return None
            
    except Exception as e:
        # print(f"ECB Exception: {e}")
        return None

def get_ecb_latest_value(df: pd.DataFrame | None) -> dict | None:
    if df is None or df.empty:
        return None
    row = df.iloc[0]
    return {"date": row["observation_time"], "value": row["value"]}
