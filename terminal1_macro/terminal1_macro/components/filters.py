import streamlit as st
from datetime import date, timedelta

def render_sidebar():
    with st.sidebar:
        st.header("Parameters")
        
        # Date Range
        today = date.today()
        start = today - timedelta(days=365*5)
        st.date_input("Date Range", value=(start, today), key="date_range")
        
        # Region
        st.selectbox("Region", ["Global", "US", "EU", "China"], index=1, key="region")
        
        # Frequency
        st.radio("Frequency", ["Daily", "Weekly", "Monthly"], index=2, key="freq")
        
        st.divider()
        st.caption("Macro Terminal v2.0")
