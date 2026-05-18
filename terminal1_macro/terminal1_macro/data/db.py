from sqlalchemy import create_engine, text
from terminal1_macro.data.settings import settings
import pandas as pd
import streamlit as st

@st.cache_resource
def get_engine():
    return create_engine(settings.db_url, pool_pre_ping=True)

@st.cache_data(ttl=60)
def get_macro_series(series_code: str, country: str | None = None, limit: int = 100) -> pd.DataFrame:
    """Get macro series data, optionally filtered by country."""
    if country:
        sql = """
            SELECT observation_time, value, provider, unit, source
            FROM macro_series
            WHERE series_code = :code AND country = :country
            ORDER BY observation_time DESC
            LIMIT :limit
        """
        params = {"code": series_code, "country": country, "limit": limit}
    else:
        sql = """
            SELECT observation_time, value, provider, unit, source
            FROM macro_series
            WHERE series_code = :code
            ORDER BY observation_time DESC
            LIMIT :limit
        """
        params = {"code": series_code, "limit": limit}
        
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

@st.cache_data(ttl=60)
def get_latest_value(series_code: str, country: str | None = None) -> dict | None:
    """Get latest value for a series, optionally filtered by country."""
    df = get_macro_series(series_code, country=country, limit=1)
    if df.empty:
        return None
    row = df.iloc[0]
    return {
        "date": row["observation_time"],
        "value": row["value"],
        "provider": row.get("provider"),
        "unit": row.get("unit"),
        "source": row.get("source"),
    }
