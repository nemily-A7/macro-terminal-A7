import streamlit as st
import plotly.express as px
from terminal1_macro.components.layout import page_header
from terminal1_macro.components.kpi_cards import render_kpi, placeholder_chart
from terminal1_macro.data.loader import get_series_for_zone
from terminal1_macro.data.settings import settings

def render_zone_tab(zone_key: str):
    # First, load profile to get country list (without loading all data yet)
    from terminal1_macro.data.loader import load_geo_profiles
    profiles = load_geo_profiles()
    
    if zone_key not in profiles:
        st.error(f"Zone {zone_key} not found in profiles")
        return
    
    profile = profiles[zone_key]
    
    # Country Selector for multi-country zones (BEFORE loading data)
    country = None
    if zone_key in ["EU", "ASIA"]:
        countries = profile.get("te_countries", [])
        default_idx = 0
        if profile.get("default_country") in countries:
            default_idx = countries.index(profile["default_country"])
        country = st.selectbox(
            f"Select Country ({profile['label']})", 
            countries, 
            index=default_idx, 
            key=f"sel_{zone_key}"
        )
    
    # NOW load data with the selected country
    results, profile = get_series_for_zone(zone_key, country=country)
    
    # KPI Grid
    st.markdown(f"### {profile['label']} Snapshot")
    
    # Check if we have data
    valid_data = [r for r in results if r["latest"] is not None]
    
    if not valid_data:
        st.warning(f"No database data found for {zone_key}.")
        
        # Offer ingestion for EU/ASIA, and Massive for US if key is present.
        if zone_key in ["EU", "ASIA"]:
            from terminal1_macro.data.loader import trigger_ingestion
            if st.button(f"Run Ingestion for {zone_key}", key=f"ingest_{zone_key}"):
                with st.spinner("Ingesting data..."):
                    if trigger_ingestion(zone_key):
                        st.success("Done! Refreshing...")
                        st.rerun()
        elif zone_key == "US":
            if not settings.massive_api_key:
                st.warning("Massive API key missing; cannot ingest Massive data.")
            else:
                from terminal1_macro.data.loader import trigger_ingestion
                if st.button("Run Massive Ingestion (US)", key="ingest_massive"):
                    with st.spinner("Ingesting Massive data..."):
                        if trigger_ingestion(zone_key, provider="massive"):
                            st.success("Done! Refreshing...")
                            st.rerun()
        return

    # Separate metrics by category for clarity? Or just flow
    cols = st.columns(4)
    
    # Priority 1 items — sort by data availability first, MASSIVE last if no data
    p1_items = [r for r in results if r["meta"].get("priority") == 1]
    p1_items = sorted(p1_items, key=lambda r: (0 if r["latest"] is not None else 1, r["meta"].get("key", "")))
    
    if not p1_items:
        st.warning(f"No indicators found for {zone_key}")
        return

    for idx, item in enumerate(p1_items[:4]): # Top 4
        meta = item["meta"]
        latest = item["latest"]
        val = latest["value"] if latest else None
        unit = (latest.get("unit") if latest else None) or meta.get("unit", "")
        render_kpi(meta["display_name"], val, unit=unit, col=cols[idx % 4])
        if latest:
            src = latest.get("provider") or meta.get("source")
            cols[idx % 4].caption(f"{src} | {latest.get('date')}")

    st.divider()
    
    # Charts
    st.markdown("### Trends")
    c1, c2 = st.columns(2)
    
    has_charts = False
    for idx, item in enumerate(p1_items[:2]): # Show charts for top 2
        hist = item["history"]
        meta = item["meta"]
        if hist is not None and not hist.empty:
            has_charts = True
            src = item["latest"].get("provider") if item.get("latest") else meta.get("source")
            fig = px.line(hist, x="observation_time", y="value", title=f"{meta['display_name']} ({src})")
            (c1 if idx == 0 else c2).plotly_chart(fig, use_container_width=True, key=f"chart_{zone_key}_{idx}")
            
    if not has_charts:
         if zone_key == "US":
             st.info("Charts loaded from FRED.")
         else:
             st.warning("Data not available. (Requires TE/ECB Ingestion)")


def show():
    page_header("Global Macro Overview", "Multi-Zone Analysis")
    
    tab_us, tab_eu, tab_asia = st.tabs(["United States", "Euro Area", "Asia"])
    
    with tab_us:
        render_zone_tab("US")
    
    with tab_eu:
        render_zone_tab("EU")
        
    with tab_asia:
        render_zone_tab("ASIA")

show()
