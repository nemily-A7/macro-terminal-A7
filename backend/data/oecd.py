from __future__ import annotations
import io
import requests
import pandas as pd
from backend.cache import ttl_cache

BASE_URL = "https://stats.oecd.org/sdmx-json/data"

# Country codes for OECD API
COUNTRY_ISO = {
    "United States": "USA",
    "Japan": "JPN",
    "South Korea": "KOR",
    "Australia": "AUS",
    "China": "CHN",
    "India": "IND",
    "Singapore": "SGP",
    "Germany": "DEU",
    "France": "FRA",
    "Italy": "ITA",
    "Spain": "ESP",
    "Netherlands": "NLD",
    "Euro Area": "EA17",
    "United Kingdom": "GBR",
    "Canada": "CAN",
}


def _parse_oecd_csv(text: str, time_col: str = "TIME", value_col: str = "Value") -> list[dict]:
    df = pd.read_csv(io.StringIO(text))
    if time_col not in df.columns or value_col not in df.columns:
        # Try alternate column names
        time_col = next((c for c in df.columns if "TIME" in c.upper()), None)
        value_col = next((c for c in df.columns if "VALUE" in c.upper()), None)
        if not time_col or not value_col:
            return []
    df = df[[time_col, value_col]].dropna()
    df = df.rename(columns={time_col: "date", value_col: "value"})
    # Normalize date format: YYYY-MM → YYYY-MM-01
    df["date"] = df["date"].astype(str).apply(
        lambda d: d + "-01" if len(d) == 7 else d
    )
    df = df.sort_values("date")
    return [{"date": r["date"], "value": round(float(r["value"]), 4)} for _, r in df.iterrows()]


@ttl_cache(seconds=3600 * 6)
def fetch_historical(dataset: str, key: str) -> list[dict] | None:
    url = f"{BASE_URL}/{dataset}/{key}/all"
    try:
        resp = requests.get(
            url,
            params={"contentType": "csv", "startTime": "2000-01"},
            timeout=20,
        )
        if resp.status_code != 200:
            return None
        rows = _parse_oecd_csv(resp.text)
        return rows if rows else None
    except Exception:
        return None
