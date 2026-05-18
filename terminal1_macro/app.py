import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Macro Terminal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Hide the main App page entry in the sidebar nav */
    [data-testid="stSidebarNav"] li:first-child { display: none; }

    /* Clean professional styling */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #212529;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #212529;
        font-size: 1.5rem;
    }
    
    /* Remove default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    
    .stButton>button:hover {
        background-color: #34495e;
    }
</style>
""", unsafe_allow_html=True)

st.title("Macro Terminal")
st.caption("Professional Macro Data Dashboard")
st.divider()

st.markdown("""
### Welcome

Access macro indicators across regions and categories.

**Navigation:**
- **Overview** - Regional snapshots (US, EU, Asia)
- **Thematic Pages** - Inflation, Rates, Labor, Growth, etc.
- **Global Overview** - Cross-region macro dashboard
- **Catalog** - All available indicators

Select a page from the sidebar to begin.
""")
