"""
DBnomics — free, no API key, 1.7B series from 93 providers (BIS, ECB, Eurostat, ILO, WTO, …).
Series path format: PROVIDER/DATASET/SERIES_KEY
"""
import requests
from backend.cache import ttl_cache


@ttl_cache(seconds=3600 * 2)
def fetch_historical(provider: str, dataset: str, series: str) -> list[dict] | None:
    try:
        url = f"https://api.db.nomics.world/v22/series/{provider}/{dataset}/{series}"
        resp = requests.get(url, params={"align_periods": "true"}, timeout=15)
        if resp.status_code != 200:
            return None
        data = resp.json()
        docs = data.get("series", {}).get("docs", [])
        if not docs:
            return None
        doc = docs[0]
        periods = doc.get("period_start_day") or doc.get("periods", [])
        values = doc.get("value", [])
        if not periods or not values:
            return None
        rows = []
        for period, val in zip(periods, values):
            if val is not None:
                rows.append({"date": str(period)[:10], "value": round(float(val), 4)})
        return sorted(rows, key=lambda r: r["date"]) or None
    except Exception:
        return None
