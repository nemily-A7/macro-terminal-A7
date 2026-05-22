from datetime import date
from fastapi import APIRouter, Query
from backend.catalog import load_catalog, load_geo_profiles
from backend.data.loader import resolve

router = APIRouter()


@router.get("/zones")
def get_zones():
    profiles = load_geo_profiles()
    return {
        "zones": [
            {
                "key": key,
                "label": p["label"],
                "countries": p["te_countries"],
                "default_country": p.get("default_country"),
            }
            for key, p in profiles.items()
        ]
    }


@router.get("/zone/{zone}/indicators")
def get_zone_indicators(zone: str, country: str | None = Query(default=None)):
    profiles = load_geo_profiles()
    catalog = load_catalog()

    if zone not in profiles:
        return {"error": "Zone not found"}

    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]
    selected_country = country or profile.get("default_country")

    indicators = [ind for ind in catalog if ind.get("region") in region_keys]

    results = []
    for ind in indicators:
        data = resolve(ind, selected_country)
        results.append({
            "key": ind["key"],
            "display_name": ind["display_name"],
            "category": ind.get("category"),
            "region": ind.get("region"),
            "source": ind.get("source"),
            "unit": ind.get("unit"),
            "frequency": ind.get("frequency"),
            "transform_default": ind.get("transform_default", "level"),
            "priority": ind.get("priority", 2),
            **data,
        })

    return {
        "zone": zone,
        "country": selected_country,
        "indicators": results,
    }


@router.get("/zone/{zone}/category/{category}")
def get_category_indicators(zone: str, category: str, country: str | None = Query(default=None)):
    profiles = load_geo_profiles()
    catalog = load_catalog()

    if zone not in profiles:
        return {"error": "Zone not found"}

    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]
    selected_country = country or profile.get("default_country")

    indicators = [
        ind for ind in catalog
        if ind.get("region") in region_keys and ind.get("category") == category
    ]

    results = []
    for ind in indicators:
        data = resolve(ind, selected_country)
        results.append({
            "key": ind["key"],
            "display_name": ind["display_name"],
            "category": ind.get("category"),
            "unit": ind.get("unit"),
            "frequency": ind.get("frequency"),
            "transform_default": ind.get("transform_default", "level"),
            "priority": ind.get("priority", 2),
            **data,
        })

    return {
        "zone": zone,
        "country": selected_country,
        "category": category,
        "indicators": results,
    }


@router.get("/zone/{zone}/indicator/{indicator_key}/compare")
def get_indicator_compare(zone: str, indicator_key: str):
    profiles = load_geo_profiles()
    catalog = load_catalog()

    if zone not in profiles:
        return {"error": "Zone not found"}

    profile = profiles[zone]
    countries = profile["te_countries"]
    region_keys = profile["region_keys_in_catalog"]

    ind = next((i for i in catalog if i["key"] == indicator_key and i.get("region") in region_keys), None)
    if not ind:
        return {"error": "Indicator not found"}

    # Determine which countries have explicit data (not fallback to default series)
    country_series_map = ind.get("country_series_map") or {}
    eurostat_geo_map   = ind.get("eurostat_geo_map") or {}
    fred_country_map   = ind.get("fred_country_map") or {}
    source = ind.get("source", "")

    if country_series_map:
        eligible = [c for c in countries if c in country_series_map]
    elif eurostat_geo_map:
        eligible = [c for c in countries if c in eurostat_geo_map]
    elif fred_country_map:
        eligible = [c for c in countries if c in fred_country_map]
    elif source == "WORLD_BANK":
        eligible = countries  # World Bank has per-country data
    else:
        eligible = countries[:1]  # single-series: only default country

    series = []
    for country in eligible:
        data = resolve(ind, country)
        if not data.get("history"):
            continue
        series.append({
            "country": country,
            "history": data["history"],
            "history_transformed": data.get("history_transformed"),
            "latest": data.get("latest"),
            "delta": data.get("delta"),
        })

    return {
        "zone": zone,
        "indicator_key": indicator_key,
        "display_name": ind.get("display_name"),
        "unit": ind.get("unit"),
        "transform_default": ind.get("transform_default", "level"),
        "series": series,
    }


@router.get("/recessions")
def get_recessions():
    from backend.data.fred import fetch_historical
    rows = fetch_historical("USREC")
    if not rows:
        return {"bands": []}

    bands = []
    in_recession = False
    start: str | None = None
    for r in rows:
        val = r.get("value")
        if val == 1.0 and not in_recession:
            in_recession = True
            start = r["date"]
        elif val == 0.0 and in_recession:
            in_recession = False
            bands.append({"start": start, "end": r["date"]})
    if in_recession and start:
        bands.append({"start": start, "end": date.today().isoformat()})

    return {"bands": bands}
