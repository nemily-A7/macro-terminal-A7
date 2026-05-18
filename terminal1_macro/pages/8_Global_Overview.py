import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from terminal1_macro.components.layout import page_header
from terminal1_macro.components.zone_selector import zone_country_selector
from terminal1_macro.data.loader import get_indicators_by_category

def show():
    page_header("Global Overview", "Cross-Region Macro Dashboard")
    
    # Zone and Country selector
    zone, country = zone_country_selector(key_prefix="global")
    
    zone_label = zone
    if country:
        zone_label = f"{zone} - {country}"
    
    st.markdown(f"### {zone_label} Macro Snapshot")
    st.divider()
    
    # Load all categories for selected zone
    categories = ["Inflation", "Rates", "Labor", "Growth", "Money_Credit", "Risk_Sentiment"]
    
    # Display each category
    for category in categories:
        indicators = get_indicators_by_category(zone, category, country)
        
        if not indicators:
            continue
        
        st.markdown(f"## {category}")
        
        # KPIs row
        cols = st.columns(min(len(indicators), 4))
        for idx, item in enumerate(indicators[:4]):
            meta = item["meta"]
            latest = item["latest"]
            
            with cols[idx]:
                if latest:
                    value_str = f"{latest['value']:.2f}"
                    unit = meta.get("unit", "")
                    st.metric(
                        meta["display_name"],
                        f"{value_str}",
                        help=f"{unit} - {meta.get('source', '')}"
                    )
                else:
                    st.metric(meta["display_name"], "-", help="No data")
        
        # Charts for this category
        if len(indicators) > 0:
            # Show up to 2 charts side by side
            chart_cols = st.columns(2)
            
            for idx, item in enumerate(indicators[:2]):
                hist = item["history"]
                meta = item["meta"]
                
                with chart_cols[idx]:
                    if hist is not None and not hist.empty:
                        fig = px.line(
                            hist[-100:],  # Last 100 points
                            x="observation_time",
                            y="value",
                            title=meta["display_name"]
                        )
                        fig.update_layout(
                            height=300,
                            margin=dict(l=0, r=0, t=30, b=0),
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No data for {meta['display_name']}")
        
        st.divider()

show()
