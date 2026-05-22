import io
import requests
import pandas as pd
from datetime import date, timedelta
from backend.cache import ttl_cache

BASE_URL = "https://data-api.ecb.europa.eu/service/data"


def _normalize_date(period: str) -> str:
    """Convert any period string to YYYY-MM-DD (lightweight-charts requirement).

    Handles: YYYY-MM-DD (pass-through), YYYY-MM → YYYY-MM-01,
             YYYY-QN → first month of quarter.
    """
    p = str(period).strip()
    if len(p) == 10:          # already YYYY-MM-DD
        return p
    if len(p) == 7:
        if "Q" in p:          # e.g. 2020-Q1 → 2020-01-01
            year, q = p.split("-Q")
            month = (int(q) - 1) * 3 + 1
            return f"{year}-{month:02d}-01"
        return p + "-01"      # YYYY-MM → YYYY-MM-01
    return p


@ttl_cache(seconds=3600 * 2)
def fetch_historical(flow_ref: str, key: str) -> list[dict] | None:
    start_period = (date.today() - timedelta(days=365 * 10)).isoformat()
    url = f"{BASE_URL}/{flow_ref}/{key}"
    try:
        resp = requests.get(
            url,
            params={"startPeriod": start_period, "format": "csvdata"},
            headers={"Accept": "text/csv"},
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(resp.text))
        if "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
            return None
        df["value"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
        df = df.dropna(subset=["value"]).sort_values("TIME_PERIOD")
        return [{"date": _normalize_date(row["TIME_PERIOD"]), "value": round(float(row["value"]), 4)}
                for _, row in df.iterrows()]
    except Exception:
        return None
