import yaml
import streamlit as st
from datetime import datetime, timedelta, timezone
from pathlib import Path

from terminal1_macro.data.db import get_macro_series, get_latest_value
from terminal1_macro.data.catalog_utils import load_catalog
from terminal1_macro.data.te_api import fetch_te_historical, get_te_latest_value
from terminal1_macro.data.ecb_sdmx import get_historical_series, get_ecb_latest_value

GEO_PROFILES_PATH = Path(__file__).parents[2] / "geo_profiles.yml"

@st.cache_data
def load_geo_profiles():
    with open(GEO_PROFILES_PATH, "r") as f:
        return yaml.safe_load(f)

def get_series_for_zone(zone: str, country: str | None = None):
    """
    Returns a list of indicators filtered by zone, with resolved data series.
    """
    profiles = load_geo_profiles()
    catalog = load_catalog()
    
    if zone not in profiles:
        return [], None # Return profile too or change signature?
        # Original sig was just return results, profile (tuple)
    
    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]
    
    # Filter catalog
    indicators = [
        item for item in catalog 
        if item.get("region") in region_keys
    ]
    
    # Resolve Data
    results = []
    
    selected_country = country or profile.get("default_country")
    
    def is_stale(meta: dict, latest: dict | None) -> bool:
        if latest is None or latest.get("date") is None:
            return True
        freq = (meta.get("frequency") or "").lower()
        cutoff_days = 10 if freq == "daily" else 90 if freq == "monthly" else 200
        dt = latest["date"]
        if isinstance(dt, datetime):
            ts = dt
        else:
            try:
                ts = datetime.fromisoformat(str(dt))
            except ValueError:
                return True
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts < datetime.now(timezone.utc) - timedelta(days=cutoff_days)

    for ind in indicators:
        key = ind.get("key")
        source = ind.get("source")
        series_id = ind.get("series_id")
        
        data_point = None
        series_data = None
        
        # Determine which country to use for query
        # US/FRED: NO country filter (series_code is unique)
        # EU/ASIA: USE country filter (same indicator across multiple countries)
        query_country = None
        
        if source in ["TRADING_ECONOMICS", "ECB_SDMX"]:
            # For multi-country sources, use selected country or default
            query_country = selected_country if selected_country else profile.get("default_country")
        
        # Primary DB Read
        data_point = get_latest_value(key, country=query_country)
        series_data = get_macro_series(key, country=query_country)

        fallback_key = ind.get("fallback_key")
        if fallback_key and (data_point is None or is_stale(ind, data_point)):
            fb_latest = get_latest_value(fallback_key, country=query_country)
            fb_series = get_macro_series(fallback_key, country=query_country)
            if fb_latest is not None and fb_series is not None and not fb_series.empty:
                data_point = fb_latest
                series_data = fb_series
        
        # 2. If missing, show ingestion prompt (handled by UI)
        # The rest of the source-specific logic now acts as fallbacks if DB read fails or for non-FRED sources.
        
        if source == "ECB_SDMX":
             # Try ECB first
             # flowRef/key should be in series_id?
             # series_id format assumed: "FLOW_REF/KEY" or just KEY if flow implied?
             # Catalog needs an update if we want real ECB calls.
             # Assuming series_id = "FLOW.KEY" -> split? 
             # For now, if catalog has "ICP.M..." we need the flow ref.
             # Let's assume series_id is the FULL key "FLOW/KEY" or fallback.
             
             parts = series_id.split("/")
             if len(parts) == 2:
                 flow, key = parts
                 df = get_historical_series(flow, key)
                 if df is not None:
                     series_data = df
                     data_point = get_ecb_latest_value(df)
            
             # Fallback to TE if ECB fails or config missing
             if series_data is None:
                 # Check if we can map to TE?
                 # Need a generic fallback "Euro Area" + generic indicator name
                 # This requires metadata about "what is this indicator?"
                 # Catalog has 'display_name'.
                 
                 # Heuristic Fallback
                 te_ind = ind.get("display_name") # e.g. "Inflation Rate"
                 df = fetch_te_historical("Euro Area", te_ind)
                 if df is not None:
                     series_data = df
                     data_point = get_te_latest_value(df)

        elif source == "TRADING_ECONOMICS":
            # Use Live API Fallback
            # Using prompt logic: /historical/country/{country}/indicator/{indicator}
            
            target_country = selected_country
            if ind.get("region") == "EU" and not country: 
                target_country = "Euro Area"
            
            # series_id in catalog for TE is the Indicator Name (e.g. "Inflation Rate")
            df = fetch_te_historical(target_country, series_id)
            if df is not None:
                series_data = df
                data_point = get_te_latest_value(df)

        results.append({
            "meta": ind,
            "latest": data_point,
            "history": series_data,
            "resolved_country": selected_country if source == "TRADING_ECONOMICS" else ind.get("region")
        })
        
    return results, profile

import sys
import subprocess
import os
from pathlib import Path

def trigger_ingestion(region: str, provider: str | None = None):
    """Run ingestion script for region."""
    try:
        # Determine Project Root (Assuming this file is at terminal/terminal1_macro/data/loader.py)
        # Root is 2 levels up: terminal/
        files_dir = Path(__file__).resolve().parent
        repo_root = files_dir.parents[1]  # terminal/ (not [2] which goes to CODE/)
        
        # Test1 path needs to be in PYTHONPATH to import terminal_ingestion
        test1_path = repo_root / "test1"
        
        # Build direct path to script (more reliable than -m)
        script_path = test1_path / "terminal_ingestion" / "macro" / "run.py"
        
        # Validate paths exist
        if not script_path.exists():
            st.error(f"Script not found: {script_path}")
            return False
            
        # Set up environment with PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{test1_path}:{env.get('PYTHONPATH', '')}"
        
        # Direct script execution (more reliable than -m in Streamlit context)
        cmd = [sys.executable, str(script_path), "--region", region]
        if provider:
            cmd.extend(["--provider", provider])
        
        # Debug info
        debug_info = f"""
Repo Root: {repo_root}
Test1 Path: {test1_path}
Script Path: {script_path}
Script Exists: {script_path.exists()}
PYTHONPATH: {env['PYTHONPATH']}
CWD: {repo_root}
Command: {' '.join(cmd)}
"""
        
        res = subprocess.run(
            cmd,
            cwd=str(repo_root),  # Execute from root
            env=env,
            capture_output=True,
            text=True
        )
        
        if res.returncode != 0:
            st.error(f"Ingestion failed (Exit Code {res.returncode})")
            with st.expander("Debug Info", expanded=False):
                st.code(debug_info)
            with st.expander("❌ Error Logs", expanded=True):
                st.code(f"STDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}")
            return False
            
        st.success("✅ Ingestion complete!")
        with st.expander("Ingestion Logs", expanded=False):
            st.code(res.stdout)
             
        st.cache_data.clear()
        return True
        
    except Exception as e:
        st.error(f"Execution Error: {e}")
        import traceback
        with st.expander("Exception Details", expanded=True):
            st.code(traceback.format_exc())
        return False

def get_indicators_by_category(zone: str, category: str, country: str | None = None):
    """
    Get all indicators for a specific zone and category.
    
    Args:
        zone: Zone code (US, EU, ASIA)
        category: Category name (Inflation, Rates, Labor, Growth, Money_Credit, Risk_Sentiment)
        country: Optional country filter for multi-country zones
        
    Returns:
        List of dicts with keys: meta, latest, history
    """
    catalog = load_catalog()
    profiles = load_geo_profiles()
    
    if zone not in profiles:
        return []
    
    profile = profiles[zone]
    region_keys = profile["region_keys_in_catalog"]
    
    # Filter by zone and category
    indicators = [
        item for item in catalog 
        if item.get("region") in region_keys and item.get("category") == category
    ]
    
    # Determine country to use
    query_country = country if country else profile.get("default_country")
    
    results = []
    for ind in indicators:
        key = ind.get("key")
        source = ind.get("source")
        
        # For US/FRED, no country filter. For EU/ASIA, use country filter
        country_filter = None
        if source in ["TRADING_ECONOMICS", "ECB_SDMX"]:
            country_filter = query_country
        
        # Get data
        data_point = get_latest_value(key, country=country_filter)
        series_data = get_macro_series(key, country=country_filter)
        
        results.append({
            "meta": ind,
            "latest": data_point,
            "history": series_data
        })
    
    return results
