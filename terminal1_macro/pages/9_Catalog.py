import streamlit as st
import pandas as pd
from terminal1_macro.components.layout import page_header
from terminal1_macro.data.catalog_utils import load_catalog

def show():
    page_header("Indicator Catalog", "Source of Truth for Macro Data")
    
    try:
        data = load_catalog()
    except Exception as e:
        st.error(f"Failed to load catalog: {e}")
        return

    # Metrics
    total = len(data)
    mapped = len([d for d in data if d.get("status") == "MAPPED"])
    coverage = (mapped / total) * 100 if total > 0 else 0
    
    cols = st.columns(4)
    cols[0].metric("Total Indicators", total)
    cols[1].metric("Mapped", mapped)
    cols[2].metric("Coverage", f"{coverage:.1f}%")
    
    st.divider()
    
    # Filter
    cat_filter = st.selectbox("Filter by Category", ["All"] + sorted(list(set(d["category"] for d in data))))
    
    filtered_data = data
    if cat_filter != "All":
        filtered_data = [d for d in data if d["category"] == cat_filter]
        
    # Display
    st.dataframe(
        pd.DataFrame(filtered_data),
        column_order=["key", "display_name", "category", "source", "frequency", "priority", "status"],
        use_container_width=True,
        hide_index=True
    )

show()
