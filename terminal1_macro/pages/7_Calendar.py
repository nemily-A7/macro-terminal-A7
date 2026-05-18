import streamlit as st
from terminal1_macro.components.layout import page_header

def show():
    page_header("Economic Calendar", "Upcoming Events")
    st.dataframe({"Date": ["2026-02-04", "2026-02-06"], "Event": ["FOMC Minutes", "NFP"]})

show()
