"""
Finnhub — real-time quotes for global equity indices (EU, ASIA).
Free tier: 60 req/min, no attribution required.
Register at https://finnhub.io to obtain an API key.
Set FINNHUB_API_KEY in .env to enable live equity prices.
"""
import os
import time
import requests
from threading import Lock

_API_KEY = os.getenv("FINNHUB_API_KEY", "")
_BASE = "https://finnhub.io/api/v1"

_cache: dict[str, tuple[float, dict]] = {}
_lock = Lock()
_CACHE_TTL = 60  # 1-min cache — equities update tick-by-tick

SYMBOL_MAP: dict[str, str] = {
    # EU equity indices
    "market_eurostoxx": "^STOXX50E",
    "market_dax":       "^GDAXI",
    "market_cac40":     "^FCHI",
    "market_ftse_mib":  "FTSEMIB.MI",
    "market_ibex35":    "^IBEX",
    # ASIA equity indices
    "market_nikkei":    "^N225",
    "market_hangseng":  "^HSI",
    "market_kospi":     "^KS11",
    "market_asx200":    "^AXJO",
    "market_csi300":    "000300.SS",
}


def fetch_quotes(keys: list[str]) -> dict[str, dict]:
    """Fetch live quotes for a list of catalog keys. Returns {} if key not configured."""
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

    for key in missing:
        symbol = SYMBOL_MAP[key]
        try:
            resp = requests.get(
                f"{_BASE}/quote",
                params={"symbol": symbol, "token": _API_KEY},
                timeout=8,
            )
            if resp.status_code != 200:
                continue
            q = resp.json()
            current = q.get("c")
            if not current:
                continue
            pc = float(q.get("pc") or 0)
            c = float(current)
            change = round(c - pc, 4)
            pct = round((change / pc * 100) if pc else 0, 4)
            parsed = {
                "price":          c,
                "prev_close":     pc,
                "change":         change,
                "pct_change":     pct,
                "is_market_open": bool(q.get("t", 0)),
                "datetime":       str(q.get("t", "")),
            }
            with _lock:
                _cache[key] = (now, parsed)
            result[key] = parsed
        except Exception:
            pass

    return result
