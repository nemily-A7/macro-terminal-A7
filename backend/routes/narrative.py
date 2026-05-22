from __future__ import annotations
import os
import time
from fastapi import APIRouter, Query
from backend.catalog import load_catalog, load_geo_profiles
from backend.data.loader import resolve

router = APIRouter()

# Simple in-process cache: (zone, country) -> (timestamp, text)
_cache: dict[tuple[str, str], tuple[float, str]] = {}
_CACHE_TTL = 3600  # 1 hour — macro data rarely changes intraday


def _build_snapshot(zone: str, country: str) -> list[dict]:
    profiles = load_geo_profiles()
    catalog  = load_catalog()
    profile  = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]

    indicators = [i for i in catalog if i.get("region") in region_keys]
    rows = []
    for ind in indicators:
        try:
            data   = resolve(ind, country)
            latest = data.get("latest")
            prev   = data.get("latest_raw")
            if not latest or latest.get("value") is None:
                continue
            rows.append({
                "name":      ind["display_name"],
                "category":  ind.get("category", ""),
                "value":     latest["value"],
                "date":      latest["date"],
                "unit":      ind.get("unit", ""),
                "transform": ind.get("transform_default", "level"),
                "delta":     data.get("delta"),
                "prev":      prev["value"] if prev else None,
            })
        except Exception:
            pass
    return rows


def _format_value(row: dict) -> str:
    v = row["value"]
    unit = row["unit"].lower()
    if row["transform"] != "level" or "percent" in unit:
        return f"{v:+.2f}%" if row["transform"] != "level" else f"{v:.2f}%"
    if "billions" in unit:
        return f"${v/1000:.1f}T"
    return f"{v:.2f}"


def _generate_narrative(zone: str, country: str, rows: list[dict]) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return ""

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    # Build a compact data table for the prompt
    lines = []
    for r in rows:
        delta_str = f" (Δ {r['delta']:+.2f})" if r["delta"] is not None else ""
        lines.append(f"- {r['category']} | {r['name']}: {_format_value(r)}{delta_str} [{r['date']}]")

    data_block = "\n".join(lines)
    zone_label = {"US": "United States", "EU": "Euro Area", "ASIA": "Asia"}.get(zone, zone)
    country_label = country if country != zone_label else zone_label

    prompt = f"""You are a senior macro analyst. Based on the latest economic data for {country_label}, write a concise professional macro snapshot in 3-4 sentences.

Rules:
- Focus on the most significant signals (inflation, growth, labor, rates)
- Mention key trends and their direction
- Note any divergences or tensions between indicators
- Be direct and data-driven, no filler phrases
- Write in English, present tense
- Do NOT start with "The data shows" or similar generic openers

Current data ({country_label}):
{data_block}

Write the macro snapshot now:"""

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return ""


@router.get("/zone/{zone}/narrative")
def get_narrative(
    zone:    str,
    country: str | None = Query(default=None),
):
    profiles = load_geo_profiles()
    if zone not in profiles:
        return {"narrative": "", "error": "Zone not found"}

    profile  = profiles[zone]
    resolved = country or profile.get("default_country", zone)
    cache_key = (zone, resolved)

    # Return cached if fresh
    cached = _cache.get(cache_key)
    if cached and time.time() - cached[0] < _CACHE_TTL:
        return {"narrative": cached[1], "zone": zone, "country": resolved, "cached": True}

    rows = _build_snapshot(zone, resolved)
    text = _generate_narrative(zone, resolved, rows)

    if text:
        _cache[cache_key] = (time.time(), text)

    return {
        "narrative": text,
        "zone":      zone,
        "country":   resolved,
        "cached":    False,
        "no_key":    not bool(os.getenv("ANTHROPIC_API_KEY", "")),
    }
