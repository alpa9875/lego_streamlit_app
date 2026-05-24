import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("Set Analytics")

engine = get_engine()

@st.cache_data(ttl=300)
def load_set_data():
    query = """
        SELECT
            psi.set_num,
            psi.retail_price,
            psi.retail_value,
            s.num_parts,
            s.year,
            t.name AS theme
        FROM personal_set_inv psi
        JOIN sets s ON s.set_num = psi.set_num || '-1'
        JOIN themes t ON t.id = s.theme_id
        WHERE psi.retail_price > 0
            AND psi.retail_value IS NOT NULL
            AND s.num_parts IS NOT NULL
            AND s.year IS NOT NULL;
    """
    return pd.read_sql(query, engine)

df = load_set_data()

st.subheader("Correlation Explorer")

x_axis = st.selectbox(" X-axis", ["num_parts", "year", "retail_price"])
y_axis = st.selectbox("Y-axis", ["retail_value", "retail_price"])

fig = px.scatter(
    df,
    x=x_axis,
    y=y_axis,
    color="theme",
    hover_data=["set_num"],
    trendline="ols",
    title=f"{y_axis} vs {x_axis}"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Them-Level Value Trends")
theme_avg = df.groupby("theme")[["retail_price", "retail_value"]].mean().reset_index()

fig2 = px.bar(
    theme_avg.sort_values("retail_value", ascending=False).head(20),
    x="Theme",
    y="Aftermarket_value",
    title="Top Themes by Avg Aftermarket Value"
)

st.plotly_chart(fig2, use_container_width=True)
