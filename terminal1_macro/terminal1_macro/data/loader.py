import yaml
import streamlit as st
from datetime import datetime, timedelta, timezone
from pathlib import Path

from terminal1_macro.data.db import get_macro_series, get_latest_value
from terminal1_macro.data.catalog_utils import load_catalog
from terminal1_macro.data.te_api import fetch_te_historical, get_te_latest_value
from terminal1_macro.data.ecb_sdmx import get_historical_series, get_ecb_latest_value
from terminal1_macro.data.fred_api import fetch_fred_historical, get_fred_latest_value
from terminal1_macro.data.eurostat_api import fetch_eurostat, get_eurostat_latest_value
from terminal1_macro.data.worldbank_api import fetch_worldbank, get_worldbank_latest_value

GEO_PROFILES_PATH = Path(__file__).parents[2] / "geo_profiles.yml"

@st.cache_data
def load_geo_profiles():
    with open(GEO_PROFILES_PATH, "r") as f:
        return yaml.safe_load(f)

def resolve_indicator_data(ind: dict, selected_country: str | None):
    key = ind.get("key")
    source = ind.get("source")

    # Resolve country-specific series ID (works for FRED and ECB_SDMX)
    series_id = ind.get("series_id", "")
    country_series_map = ind.get("country_series_map")
    if country_series_map and selected_country:
        series_id = country_series_map.get(selected_country, series_id)

    # Resolve Eurostat geo filter per selected country
    eurostat_filters = dict(ind.get("eurostat_filters", {}))
    eurostat_geo_map = ind.get("eurostat_geo_map")
    if eurostat_geo_map and selected_country:
        eurostat_filters["geo"] = eurostat_geo_map.get(
            selected_country, eurostat_filters.get("geo", "EA21")
        )

    query_country = None
    if source in ["TRADING_ECONOMICS", "ECB_SDMX"]:
        query_country = selected_country

    data_point = get_latest_value(key, country=query_country)
    series_data = get_macro_series(key, country=query_country)

    fallback_key = ind.get("fallback_key")
    if fallback_key and data_point is None:
        fb_latest = get_latest_value(fallback_key, country=query_country)
        fb_series = get_macro_series(fallback_key, country=query_country)
        if fb_latest is not None and fb_series is not None and not fb_series.empty:
            data_point = fb_latest
            series_data = fb_series

    if series_data is None or series_data.empty:
        # fred_country_map: per-country FRED series override regardless of default source
        fred_country_map = ind.get("fred_country_map")
        if fred_country_map and selected_country and selected_country in fred_country_map:
            df = fetch_fred_historical(fred_country_map[selected_country])
            if df is not None:
                series_data = df
                data_point = get_fred_latest_value(df)
                if data_point:
                    data_point["provider"] = "FRED"
                    data_point["unit"] = ind.get("unit")
                    data_point["source"] = "FRED"
                return data_point, series_data

        if source == "FRED":
            df = fetch_fred_historical(series_id)
            if df is not None:
                series_data = df
                data_point = get_fred_latest_value(df)

        elif source == "ECB_SDMX":
            parts = series_id.split("/")
            if len(parts) == 2:
                flow, key_id = parts
                df = get_historical_series(flow, key_id)
                if df is not None:
                    series_data = df
                    data_point = get_ecb_latest_value(df)
            if series_data is None or series_data.empty:
                df = fetch_te_historical("Euro Area", ind.get("display_name", ""))
                if df is not None:
                    series_data = df
                    data_point = get_te_latest_value(df)

        elif source == "WORLD_BANK":
            country = selected_country or ind.get("region")
            df = fetch_worldbank(country, series_id)
            if df is not None:
                series_data = df
                data_point = get_worldbank_latest_value(df)

        elif source == "EUROSTAT":
            df = fetch_eurostat(series_id, eurostat_filters)
            if df is not None:
                series_data = df
                data_point = get_eurostat_latest_value(df)

        elif source == "TRADING_ECONOMICS":
            target_country = selected_country
            if ind.get("region") == "EU" and not target_country:
                target_country = "Euro Area"
            df = fetch_te_historical(target_country, series_id)
            if df is not None:
                series_data = df
                data_point = get_te_latest_value(df)

    if data_point and not data_point.get("provider"):
        data_point["provider"] = source
        data_point["unit"] = ind.get("unit")
        data_point["source"] = source

    return data_point, series_data


def get_series_for_zone(zone: str, country: str | None = None):
    profiles = load_geo_profiles()
    catalog = load_catalog()

    if zone not in profiles:
        return [], None

    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]

    indicators = [item for item in catalog if item.get("region") in region_keys]

    selected_country = country or profile.get("default_country")
    results = []

    for ind in indicators:
        data_point, series_data = resolve_indicator_data(ind, selected_country)
        results.append({
            "meta": ind,
            "latest": data_point,
            "history": series_data,
            "resolved_country": selected_country,
        })

    return results, profile


def trigger_ingestion(region: str, provider: str | None = None):
    st.warning("Ingestion is disabled in API-only mode.")
    return False


def get_indicators_by_category(zone: str, category: str, country: str | None = None):
    catalog = load_catalog()
    profiles = load_geo_profiles()

    if zone not in profiles:
        return []

    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]

    indicators = [
        item for item in catalog
        if item.get("region") in region_keys and item.get("category") == category
    ]

    query_country = country if country else profile.get("default_country")
    results = []

    for ind in indicators:
        data_point, series_data = resolve_indicator_data(ind, query_country)
        results.append({
            "meta": ind,
            "latest": data_point,
            "history": series_data,
            "resolved_country": query_country,
        })

    return results
