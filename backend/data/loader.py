from __future__ import annotations
from backend.data import fred, ecb, worldbank, eurostat, oecd, gpr, dbnomics


def _apply_transform(rows: list[dict], transform: str, frequency: str) -> list[dict]:
    if not rows or transform == "level":
        return rows
    periods = {"monthly": 12, "quarterly": 4, "annual": 1, "daily": 252}.get(frequency, 12)
    if transform == "yoy":
        result = []
        for i, row in enumerate(rows):
            if i < periods:
                result.append({**row, "value": None})
            else:
                prev = rows[i - periods]["value"]
                if prev and prev != 0:
                    result.append({**row, "value": round((row["value"] - prev) / abs(prev) * 100, 4)})
                else:
                    result.append({**row, "value": None})
        return result
    if transform == "mom":
        result = [rows[0]]
        for i in range(1, len(rows)):
            prev = rows[i - 1]["value"]
            if prev and prev != 0:
                result.append({**rows[i], "value": round((rows[i]["value"] - prev) / abs(prev) * 100, 4)})
            else:
                result.append({**rows[i], "value": None})
        return result
    return rows


def resolve(ind: dict, selected_country: str | None) -> dict:
    source = ind.get("source", "")
    transform = ind.get("transform_default", "level")
    frequency = ind.get("frequency", "monthly")

    series_id = ind.get("series_id", "")
    country_series_map = ind.get("country_series_map")
    if country_series_map and selected_country:
        series_id = country_series_map.get(selected_country, series_id)

    eurostat_filters = dict(ind.get("eurostat_filters", {}))
    eurostat_geo_map = ind.get("eurostat_geo_map")
    if eurostat_geo_map and selected_country:
        eurostat_filters["geo"] = eurostat_geo_map.get(selected_country, eurostat_filters.get("geo", "EA21"))

    fred_country_map = ind.get("fred_country_map")

    raw: list[dict] | None = None

    if fred_country_map and selected_country and selected_country in fred_country_map:
        raw = fred.fetch_historical(fred_country_map[selected_country])

    elif source == "FRED":
        raw = fred.fetch_historical(series_id)

    elif source == "ECB_SDMX":
        parts = series_id.split("/")
        if len(parts) == 2:
            raw = ecb.fetch_historical(parts[0], parts[1])

    elif source == "WORLD_BANK":
        country = selected_country or "United States"
        raw = worldbank.fetch_historical(country, series_id)

    elif source == "EUROSTAT":
        raw = eurostat.fetch_historical(series_id, tuple(sorted(eurostat_filters.items())))

    elif source == "OECD":
        parts = series_id.split("/")
        if len(parts) == 2:
            dataset, key_template = parts
            country_code = oecd.COUNTRY_ISO.get(selected_country or "") if selected_country else None
            country_series_map = ind.get("country_series_map")
            if country_series_map and selected_country and selected_country in country_series_map:
                key = country_series_map[selected_country]
            elif country_code:
                key = key_template.replace("{country}", country_code)
            else:
                key = key_template
            raw = oecd.fetch_historical(dataset, key)

    elif source == "GPR":
        raw = gpr.fetch_historical(series_id)

    elif source == "DBNOMICS":
        parts = series_id.split("/")
        if len(parts) == 3:
            raw = dbnomics.fetch_historical(parts[0], parts[1], parts[2])

    elif source == "LIVE_ONLY":
        raw = None  # history intentionally empty — live value injected via WebSocket

    if not raw:
        return {"history": [], "latest": None, "latest_raw": None}

    transformed = _apply_transform(raw, transform, frequency)
    valid_transformed = [r for r in transformed if r["value"] is not None]

    latest_raw = raw[-1] if raw else None
    latest = valid_transformed[-1] if valid_transformed else None

    prev_transformed = valid_transformed[-2] if len(valid_transformed) > 1 else None
    delta = None
    if latest and prev_transformed:
        delta = round(latest["value"] - prev_transformed["value"], 4)

    return {
        "history": raw,
        "history_transformed": transformed,
        "latest_raw": latest_raw,
        "latest": latest,
        "delta": delta,
        "transform": transform,
    }
