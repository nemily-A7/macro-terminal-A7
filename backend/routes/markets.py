from fastapi import APIRouter
from backend.catalog import load_catalog
from backend.data.loader import resolve
from backend.data import twelvedata, equities

router = APIRouter()


@router.get("/markets")
def get_markets():
    catalog = load_catalog()
    indicators = [
        ind for ind in catalog
        if ind.get("category") == "Markets"
        and ind.get("region") in ("GLOBAL", "EU", "ASIA")
    ]

    keys = [ind["key"] for ind in indicators]
    live_td  = twelvedata.fetch_quotes(keys)   # FX + crypto (Twelve Data)
    live_eq  = equities.fetch_quotes(keys)     # Equity indices (Yahoo Finance)

    results = []
    for ind in indicators:
        data = resolve(ind, None)
        key = ind["key"]
        q = live_td.get(key) or live_eq.get(key)
        live_src = (
            "twelvedata" if key in live_td else
            "yahoo"      if key in live_eq else
            "fred"
        )

        entry: dict = {
            "key":          key,
            "display_name": ind["display_name"],
            "unit":         ind.get("unit", ""),
            "frequency":    ind.get("frequency", "daily"),
            "asset_class":  ind.get("asset_class", "other"),
            "market_zone":  ind.get("market_zone", ind.get("region", "GLOBAL")),
            "priority":     ind.get("priority", 2),
            **data,
            "live_price":       q["price"]          if q else None,
            "live_pct_change":  q["pct_change"]     if q else None,
            "live_change":      q["change"]         if q else None,
            "live_prev_close":  q["prev_close"]     if q else None,
            "is_market_open":   q["is_market_open"] if q else None,
            "live_datetime":    q["datetime"]       if q else None,
            "live_source":      live_src if q else "fred",
        }
        results.append(entry)

    return {"markets": results}
