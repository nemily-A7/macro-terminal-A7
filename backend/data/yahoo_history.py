"""
Yahoo Finance v8 chart API — full daily time series.
Same endpoint as equities.py but fetches multi-year history.
Used for daily indicators (yields, VIX, commodities) to bypass FRED's 1-day lag.
Cache: 1-hour TTL (data only changes once per trading day).
"""
import time
import random
import requests
from threading import Lock

_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}
_CACHE_TTL = 3600  # 1 hour

_cache: dict[str, tuple[float, list[dict]]] = {}
_lock = Lock()


def fetch_historical(symbol: str, years: int = 10) -> list[dict] | None:
    """Fetch daily close history for a Yahoo Finance symbol.

    Returns a list of {date, value} dicts sorted ascending, or None on failure.
    Results are cached in-process for 1 hour.
    """
    now = time.time()
    with _lock:
        cached = _cache.get(symbol)
        if cached and now - cached[0] < _CACHE_TTL:
            return cached[1]

    for attempt in range(3):
        try:
            resp = requests.get(
                f"{_BASE}/{symbol}",
                headers=_HEADERS,
                params={"interval": "1d", "range": f"{years}y"},
                timeout=15,
            )
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt + random.uniform(0, 1))
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                return None

            data = resp.json()
            result = data.get("chart", {}).get("result")
            if not result:
                return None

            timestamps = result[0].get("timestamp", [])
            quotes = result[0].get("indicators", {}).get("quote", [{}])
            closes = quotes[0].get("close", []) if quotes else []

            if not timestamps or not closes:
                return None

            from datetime import datetime, timezone
            rows = []
            for ts, close in zip(timestamps, closes):
                if close is None:
                    continue
                date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                rows.append({"date": date_str, "value": round(float(close), 6)})

            rows.sort(key=lambda r: r["date"])

            if rows:
                with _lock:
                    _cache[symbol] = (now, rows)
                return rows
            return None

        except Exception:
            if attempt < 2:
                time.sleep(2.0 ** attempt + random.uniform(0, 0.5))

    return None
