import streamlit as st

def page_header(title: str, subtitle: str | None = None):
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.divider()

def make_grid(cols: int = 3, rows: int = 1):
    grid = []
    for _ in range(rows):
        with st.container():
            grid.append(st.columns(cols))
    return grid
