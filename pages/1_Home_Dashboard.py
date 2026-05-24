import streamlit as st
import pandas as pd
from utils.db import get_engine
import plotly.express as px

st.title("Home Dashboard")

engine = get_engine()

@st.cache_data(ttl=300)
def load_inventory_summary():
    query = """
        SELECT
            (SELECT COUNT(*) FROM personal_set_inv) AS total_sets,
            (SELECT SUM(retail_price * quantity) FROM personal_set_inv) AS total_retail_price,
            (SELECT SUM(retail_value * quantity) FROM personal_set_inv) AS total_aftermarket_value,
            (SELECT SUM(grand_total_qty) FROM set_parts_inventory) AS total_parts
        FROM (SELECT 1) AS dummy;
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_theme_distribution():
    query = """
        SELECT t.name AS theme, COUNT(*) AS num_sets
        FROM personal_set_inv psi
        JOIN sets s ON s.set_num = psi.set_num || '-1'
        JOIN themes t ON t.id = s.theme_id
        GROUP BY t.name
        ORDER BY num_sets DESC
        LIMIT 25;
    """
    return pd.read_sql(query, engine)

summary = load_inventory_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sets", int(summary["total_sets"][0]))
col2.metric("Total Retail Price", f"${summary['total_retail_price'][0]:,.0f}")
col3.metric("Total Aftermarket Value", f"${summary['total_aftermarket_value'][0]:,.0f}")
col4.metric("Total Parts", f"{summary['total_parts'][0]:,}")

st.subheader("Top Themes in My Collection")
themes = load_theme_distribution()
fig = px.bar(themes, x="theme", y="num_sets", title="Top Themes by Set Count")
st.plotly_chart(fig, use_container_width=True)
