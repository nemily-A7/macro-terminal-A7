import streamlit as st
import plotly.express as px
from terminal1_macro.components.layout import page_header
from terminal1_macro.components.zone_selector import zone_country_selector
from terminal1_macro.data.loader import get_indicators_by_category

def show():
    page_header("Labor Market", "Employment & Wages")
    
    zone, country = zone_country_selector(key_prefix="labor")
    
    indicators = get_indicators_by_category(zone, "Labor", country)
    
    if not indicators:
        st.warning(f"No labor indicators found for {zone}")
        return
    
    # Display KPIs
    cols = st.columns(min(len(indicators), 4))
    for idx, item in enumerate(indicators[:4]):
        meta = item["meta"]
        latest = item["latest"]
        
        if latest:
            value_str = f"{latest['value']:.2f}"
            unit = meta.get("unit", "")
            cols[idx].metric(
                meta["display_name"],
                f"{value_str} {unit}",
                help=f"{meta.get('key')} - {meta.get('source')}"
            )
        else:
            cols[idx].metric(meta["display_name"], "-", help="No data available")
    
    st.divider()
    
    # Charts
    if len(indicators) > 0:
        tab_labels = [item["meta"]["display_name"] for item in indicators]
        tabs = st.tabs(tab_labels)
        
        for idx, (tab, item) in enumerate(zip(tabs, indicators)):
            with tab:
                hist = item["history"]
                meta = item["meta"]
                
                if hist is not None and not hist.empty:
                    fig = px.line(
                        hist, 
                        x="observation_time", 
                        y="value",
                        title=f"{meta['display_name']} - {meta.get('source', '')}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No historical data available")

show()
