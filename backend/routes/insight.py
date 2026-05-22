from __future__ import annotations
import os
import time
from fastapi import APIRouter, Query
from backend.catalog import load_catalog
from backend.data.loader import resolve
from backend.data.descriptions import DESCRIPTIONS

router = APIRouter()

_cache: dict[tuple, tuple[float, str]] = {}
_CACHE_TTL = 3600  # 1 hour — indicator values change slowly


def _build_prompt(ind: dict, data: dict, zone: str, country: str | None) -> str:
    latest   = data.get("latest")
    delta    = data.get("delta")
    transform = ind.get("transform_default", "level")
    unit      = ind.get("unit", "")
    desc      = DESCRIPTIONS.get(ind["key"], "")

    display_unit = "%" if (transform != "level" or "percent" in unit.lower()) else unit
    value_str = f"{latest['value']:.4g}{display_unit}" if latest and latest["value"] is not None else "no data"
    date_str  = (latest.get("date") or "")[:7] if latest else "N/A"
    delta_str = f"{delta:+.4g}{display_unit}" if delta is not None else "N/A"

    return f"""You are a professional macro economist at an investment bank. Provide a concise, precise interpretation of this indicator reading for a financial professional.

Indicator: {ind["display_name"]} ({ind["category"]})
Geography: {country or zone}
Latest value: {value_str} (as of {date_str})
Change vs prior period: {delta_str}
What it measures: {desc}

In exactly 2–3 sentences, interpret what this reading signals for the economy and financial markets right now. Be specific about the absolute level and its trend. Do not include labels, preamble, or markdown — return plain prose only."""


@router.get("/zone/{zone}/indicator/{key}/insight")
async def indicator_insight(
    zone: str,
    key: str,
    country: str | None = Query(default=None),
):
    catalog = load_catalog()
    ind = next((i for i in catalog if i["key"] == key), None)
    if not ind:
        return {"description": None, "interpretation": None, "no_key": False, "cached": False}

    description = DESCRIPTIONS.get(key)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"description": description, "interpretation": None, "no_key": True, "cached": False}

    cache_key = (zone, key, country or "")
    now = time.time()
    if cache_key in _cache:
        ts, interp = _cache[cache_key]
        if now - ts < _CACHE_TTL:
            return {"description": description, "interpretation": interp, "no_key": False, "cached": True}

    data = resolve(ind, country)
    if not data.get("latest"):
        return {"description": description, "interpretation": None, "no_key": False, "cached": False}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=220,
            messages=[{"role": "user", "content": _build_prompt(ind, data, zone, country)}],
        )
        interp = msg.content[0].text.strip()
        _cache[cache_key] = (now, interp)
        return {"description": description, "interpretation": interp, "no_key": False, "cached": False}
    except Exception:
        return {"description": description, "interpretation": None, "no_key": False, "cached": False}
