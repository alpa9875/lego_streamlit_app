import streamlit as st
import pandas as pd
from utils.db import get_engine

st.set_page_config(
    page_title="LEGO Room Analytics",
    page_icon="🧱",
    layout="wide"
)

st.title("🧱 LEGO Data Analytics Platform")
st.write("""
Welcome to Alicia's LEGO Analytics Platform.
Use the sidebar to navigate between:
- **Home Dashboard** - high-level metrics and visualizations
- **Set Analytics** - correlations, trends and value modeling""")