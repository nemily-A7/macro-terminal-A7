"""
Real-time equity index quotes via Yahoo Finance v8 chart API.
No API key required. Covers EU and ASIA major indices.
Cache: 1-min TTL to avoid hammering the endpoint.
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
_CACHE_TTL = 60  # 1 minute

_cache: dict[str, tuple[float, dict]] = {}
_lock = Lock()

SYMBOL_MAP: dict[str, str] = {
    # US equities
    "market_sp500":      "^GSPC",
    "market_nasdaq":     "^IXIC",
    "market_djia":       "^DJI",
    # EU equity indices
    "market_eurostoxx":  "^STOXX50E",
    "market_dax":        "^GDAXI",
    "market_cac40":      "^FCHI",
    "market_ftse_mib":   "FTSEMIB.MI",
    "market_ibex35":     "^IBEX",
    # ASIA equity indices
    "market_nikkei":     "^N225",
    "market_hangseng":   "^HSI",
    "market_kospi":      "^KS11",
    "market_asx200":     "^AXJO",
    "market_csi300":     "000300.SS",
    # US Treasury yields (value in % — e.g. 4.487 means 4.487%)
    "us_10y":            "^TNX",
    "us_30y":            "^TYX",
    # Short-term rates
    "us_3m":             "^IRX",
    # Volatility
    "us_vix":            "^VIX",
    # Commodities (futures — same-day prices, no FRED lag)
    "market_wti":        "CL=F",
    "market_brent":      "BZ=F",
    "market_natgas":     "NG=F",
    "market_gold":       "GC=F",
    # FX spot rates
    "market_eurusd":     "EURUSD=X",
    "market_usdjpy":     "USDJPY=X",
    "market_gbpusd":     "GBPUSD=X",
    "market_audusd":     "AUDUSD=X",
    "market_usdcny":     "USDCNY=X",
    "eu_eurusd":         "EURUSD=X",
    "eu_eurgbp":         "EURGBP=X",
    # Dollar Index
    "global_dxy":        "DX-Y.NYB",
}


def _fetch_one(symbol: str) -> dict | None:
    for attempt in range(3):
        try:
            resp = requests.get(
                f"{_BASE}/{symbol}",
                headers=_HEADERS,
                params={"interval": "1d", "range": "1d"},
                timeout=8,
            )
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt + random.uniform(0, 1))
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                return None
            data = resp.json()
            results = data.get("chart", {}).get("result")
            if not results:
                return None
            meta = results[0].get("meta", {})
            price = meta.get("regularMarketPrice")
            if not price:
                return None
            prev = float(meta.get("previousClose") or meta.get("chartPreviousClose") or price)
            price = float(price)
            change = round(price - prev, 4)
            pct = round((change / prev * 100) if prev else 0, 4)
            return {
                "price":          price,
                "prev_close":     prev,
                "change":         change,
                "pct_change":     pct,
                "is_market_open": meta.get("marketState") == "REGULAR",
                "datetime":       str(meta.get("regularMarketTime", "")),
            }
        except Exception:
            if attempt < 2:
                time.sleep(2.0 ** attempt + random.uniform(0, 0.5))
    return None


def fetch_quotes(keys: list[str]) -> dict[str, dict]:
    """Fetch live quotes for a list of catalog keys. Falls back gracefully."""
    now = time.time()
    result: dict[str, dict] = {}
    missing: list[str] = []

    with _lock:
        for key in keys:
            if key not in SYMBOL_MAP:
                continue
            cached = _cache.get(key)
            if cached and now - cached[0] < _CACHE_TTL:
                result[key] = cached[1]
            else:
                missing.append(key)

    for key in missing:
        parsed = _fetch_one(SYMBOL_MAP[key])
        if parsed:
            with _lock:
                _cache[key] = (now, parsed)
            result[key] = parsed

    return result
