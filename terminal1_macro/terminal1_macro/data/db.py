from sqlalchemy import create_engine, text
from terminal1_macro.data.settings import settings
import pandas as pd
import streamlit as st

@st.cache_resource
def get_engine():
    # Ne tente plus de se connecter, retourne juste un dummy
    return None

@st.cache_data(ttl=60)
def get_macro_series(series_code: str, country: str | None = None, limit: int = 100) -> pd.DataFrame:
    """Get macro series data (Bypassed: returns empty DataFrame)."""
    return pd.DataFrame()

@st.cache_data(ttl=60)
def get_latest_value(series_code: str, country: str | None = None) -> dict | None:
    """Get latest value for a series (Bypassed: returns None)."""
    return None
