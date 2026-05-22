import requests
from backend.cache import ttl_cache

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def _normalize_date(period: str) -> str:
    """Convert any period string to YYYY-MM-DD."""
    p = str(period).strip()
    if len(p) == 10:
        return p
    if len(p) == 7:
        if "Q" in p:
            year, q = p.split("Q")
            month = (int(q) - 1) * 3 + 1
            return f"{year.rstrip('-')}-{month:02d}-01"
        return p + "-01"
    return p


@ttl_cache(seconds=3600 * 2)
def fetch_historical(dataset_id: str, filters_frozen: tuple) -> list[dict] | None:
    filters = dict(filters_frozen)
    params = {**filters, "lang": "en", "sinceTimePeriod": "2000-01"}
    try:
        resp = requests.get(f"{BASE_URL}/{dataset_id}", params=params, timeout=15)
        if resp.status_code != 200:
            return None
        data = resp.json()
        time_index: dict = data["dimension"]["time"]["category"]["index"]
        values: dict = data.get("value", {})
        rows = []
        for period, pos in time_index.items():
            val = values.get(str(pos))
            if val is not None:
                rows.append({"date": _normalize_date(period), "value": round(float(val), 4)})
        return sorted(rows, key=lambda r: r["date"]) or None
    except Exception:
        return None
