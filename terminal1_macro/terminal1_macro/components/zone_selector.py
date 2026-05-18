import streamlit as st
from terminal1_macro.data.loader import load_geo_profiles

def zone_country_selector(key_prefix: str = "thematic"):
    """
    Reusable zone and country selector component.
    
    Args:
        key_prefix: Unique prefix for session state keys
        
    Returns:
        Tuple of (zone, country)
    """
    profiles = load_geo_profiles()
    
    zones = list(profiles.keys())
    zone_labels = {z: profiles[z]["label"] for z in zones}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        zone = st.selectbox(
            "Zone",
            zones,
            format_func=lambda z: zone_labels.get(z, z),
            key=f"{key_prefix}_zone"
        )
    
    with col2:
        country = None
        if zone in ["EU", "ASIA"]:
            profile = profiles[zone]
            countries = profile.get("te_countries", [])
            default_idx = 0
            if profile.get("default_country") in countries:
                default_idx = countries.index(profile["default_country"])
            country = st.selectbox(
                "Country",
                countries,
                index=default_idx,
                key=f"{key_prefix}_country_{zone}"
            )
    
    return zone, country
