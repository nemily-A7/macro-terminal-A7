import os
import time
import requests
from threading import Lock

_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")
_BASE = "https://api.twelvedata.com"

# In-memory cache: key -> (timestamp, data)
_cache: dict[str, tuple[float, dict]] = {}
_lock = Lock()
_CACHE_TTL = 900  # 15 minutes → 576 credits/day max, within free tier 800/day limit

# Map catalog keys to Twelve Data symbols.
# Free tier (800 credits/day, 8/min): only FX pairs + crypto qualify.
# Indices (SPX/IXIC/DJI) require paid plan; commodities (WTI/Brent/NG) unavailable on free.
# Those fall back to FRED end-of-day data automatically.
SYMBOL_MAP: dict[str, str] = {
    "market_eurusd": "EUR/USD",
    "market_usdjpy": "USD/JPY",
    "market_gbpusd": "GBP/USD",
    "market_audusd": "AUD/USD",
    "market_usdcny": "USD/CNY",
    "market_btc":    "BTC/USD",
    # EU zone FX — live via same Twelve Data cache
    "eu_eurusd": "EUR/USD",
    "eu_eurgbp": "EUR/GBP",
}


def fetch_quotes(keys: list[str]) -> dict[str, dict]:
    """Fetch live quotes for a list of catalog keys.

    Returns a dict of {catalog_key: {price, pct_change, change, prev_close, is_market_open, datetime}}.
    Returns empty dict if API key not configured or all values are cached.
    Falls back gracefully on any error.
    """
    if not _API_KEY:
        return {}

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

    if not missing:
        return result

    symbols = ",".join(SYMBOL_MAP[k] for k in missing)
    try:
        resp = requests.get(
            f"{_BASE}/quote",
            params={"symbol": symbols, "apikey": _API_KEY},
            timeout=10,
        )
        if resp.status_code != 200:
            return result

        raw = resp.json()

        # Single symbol: response is the quote object directly
        # Multiple symbols: response is {symbol: quote}
        if len(missing) == 1:
            raw = {SYMBOL_MAP[missing[0]]: raw}

        with _lock:
            for key in missing:
                td_sym = SYMBOL_MAP[key]
                q = raw.get(td_sym, {})
                if not q or q.get("status") == "error":
                    continue
                close = q.get("close")
                if close is None:
                    continue
                parsed: dict = {
                    "price":         float(close),
                    "prev_close":    float(q.get("previous_close") or 0),
                    "change":        float(q.get("change") or 0),
                    "pct_change":    float(q.get("percent_change") or 0),
                    "is_market_open": bool(q.get("is_market_open", False)),
                    "datetime":      q.get("datetime", ""),
                }
                _cache[key] = (now, parsed)
                result[key] = parsed

    except Exception:
        pass

    return result
