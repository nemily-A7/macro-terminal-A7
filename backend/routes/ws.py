from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.catalog import load_catalog, load_geo_profiles
from backend.data.loader import resolve
from backend.data import twelvedata, equities

router = APIRouter()


def _get_snapshot(zone: str, country: str | None) -> dict:
    profiles = load_geo_profiles()
    catalog  = load_catalog()

    if zone not in profiles:
        return {"type": "error", "message": "Zone not found"}

    profile        = profiles[zone]
    region_keys    = profile["region_keys_in_catalog"]
    selected_country = country or profile.get("default_country")

    indicators = [
        ind for ind in catalog
        if ind.get("region") in region_keys and ind.get("priority", 99) <= 2
    ]

    items = []
    for ind in indicators:
        try:
            data   = resolve(ind, selected_country)
            latest = data.get("latest")
            if latest:
                items.append({
                    "key":   ind["key"],
                    "value": latest.get("value"),
                    "date":  latest.get("date"),
                    "delta": data.get("delta"),
                })
        except Exception:
            pass

    # Market live quotes (served from in-memory cache — no extra API credits)
    market_inds  = [ind for ind in catalog if ind.get("region") == "GLOBAL"]
    market_keys  = [ind["key"] for ind in market_inds]
    live_quotes  = twelvedata.fetch_quotes(market_keys)   # cache-first, 15-min TTL
    market_prices = {
        key: {
            "price":          q["price"],
            "pct_change":     q["pct_change"],
            "change":         q["change"],
            "is_market_open": q["is_market_open"],
            "datetime":       q["datetime"],
        }
        for key, q in live_quotes.items()
    }

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Live FX overlay for EU zone — override FRED daily values with Twelve Data intraday
    if zone == "EU":
        eu_fx_keys = ["eu_eurusd", "eu_eurgbp"]
        eu_fx_quotes = twelvedata.fetch_quotes(eu_fx_keys)
        items_map = {i["key"]: i for i in items}
        for key, q in eu_fx_quotes.items():
            items_map[key] = {
                "key":   key,
                "value": q.get("price"),
                "date":  today,
                "delta": q.get("change"),
            }
        items = list(items_map.values())

    # Live Yahoo Finance overlay for US daily financial indicators — bypass FRED 1-day lag
    if zone == "US":
        yf_keys = ["us_vix", "us_10y", "us_30y"]
        yf_quotes = equities.fetch_quotes(yf_keys)
        items_map = {i["key"]: i for i in items}
        for key, q in yf_quotes.items():
            items_map[key] = {
                "key":   key,
                "value": q.get("price"),
                "date":  today,
                "delta": q.get("change"),
            }
        items = list(items_map.values())

    return {
        "type":          "snapshot",
        "zone":          zone,
        "country":       selected_country,
        "indicators":    items,
        "market_prices": market_prices,
    }


@router.websocket("/ws/live")
async def live_stream(
    websocket: WebSocket,
    zone:    str          = Query(default="US"),
    country: str | None   = Query(default=None),
):
    await websocket.accept()
    try:
        # Initial snapshot on connect
        snapshot = await asyncio.to_thread(_get_snapshot, zone, country)
        await websocket.send_json(snapshot)

        # Push updates every 30 s — Twelve Data cache absorbs repeat calls
        while True:
            await asyncio.sleep(30)
            snapshot = await asyncio.to_thread(_get_snapshot, zone, country)
            await websocket.send_json(snapshot)

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
