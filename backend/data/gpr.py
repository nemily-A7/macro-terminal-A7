"""
Geopolitical Risk Index (GPR) — Caldara & Iacoviello (Fed Board).
Monthly data for 44 countries. Free download (Excel .xls format).
Source: https://www.matteoiacoviello.com/gpr.htm
"""
import io
import time
import requests
import pandas as pd
from threading import Lock

_GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
_CACHE_TTL = 86400  # 24h — monthly data, rarely changes

_df_cache: tuple[float, "pd.DataFrame | None"] = (0.0, None)
_lock = Lock()


def _load_df() -> "pd.DataFrame | None":
    global _df_cache
    now = time.time()
    ts, df = _df_cache
    if df is not None and now - ts < _CACHE_TTL:
        return df
    try:
        resp = requests.get(_GPR_URL, timeout=30)
        if resp.status_code != 200:
            return None
        df = pd.read_excel(io.BytesIO(resp.content), engine="xlrd")
        # First column is the date
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.rename(columns={date_col: "date"})
        df = df.dropna(subset=["date"])
        with _lock:
            _df_cache = (time.time(), df)
        return df
    except Exception:
        return None


def fetch_historical(column: str) -> list[dict] | None:
    """Return [{date, value}] for the given GPR column name."""
    df = _load_df()
    if df is None:
        return None
    if column not in df.columns:
        return None
    sub = df[["date", column]].dropna()
    return [
        {"date": row["date"].strftime("%Y-%m-%d"), "value": round(float(row[column]), 4)}
        for _, row in sub.iterrows()
    ]
