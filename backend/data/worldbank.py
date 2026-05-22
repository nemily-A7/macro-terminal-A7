import requests
from backend.cache import ttl_cache

BASE_URL = "https://api.worldbank.org/v2/country"

COUNTRY_ISO = {
    "China": "CHN", "Japan": "JPN", "India": "IND",
    "South Korea": "KOR", "Singapore": "SGP", "Australia": "AUS",
    "Euro Area": "EMU", "Germany": "DEU", "France": "FRA",
    "Italy": "ITA", "Spain": "ESP", "Netherlands": "NLD",
    "United States": "USA",
}


@ttl_cache(seconds=3600 * 12)
def fetch_historical(country_name: str, indicator: str) -> list[dict] | None:
    iso = COUNTRY_ISO.get(country_name)
    if not iso:
        return None
    try:
        resp = requests.get(
            f"{BASE_URL}/{iso}/indicator/{indicator}",
            params={"format": "json", "per_page": 60, "mrv": 60},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if not payload or len(payload) < 2 or not payload[1]:
            return None
        rows = []
        for obs in payload[1]:
            if obs.get("value") is not None:
                rows.append({"date": f"{obs['date']}-12-31", "value": round(float(obs["value"]), 4)})
        return sorted(rows, key=lambda r: r["date"]) or None
    except Exception:
        return None
