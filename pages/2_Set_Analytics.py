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
            psi.name,
            psi.retail_price,
            psi.retail_value AS aftermarket_value,
            psi.is_sealed,
            psi.quantity,
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

sealed = df[df["is_sealed"] == True]
open_sets = df[df["is_sealed"] == False]

sealed_value = (sealed["aftermarket_value"] * sealed["quantity"]).sum()
sealed_price = (sealed["retail_price"] * sealed["quantity"]).sum()
sealed_ratio = sealed_value / sealed_price if sealed_price > 0 else 0
open_value = (open_sets["aftermarket_value"] * open_sets["quantity"]).sum()
open_price = (open_sets["retail_price"] * open_sets["quantity"]).sum()
open_ratio = open_value / open_price if open_price > 0 else 0
avg_parts = df["num_parts"].mean()

st.subheader("Set Value Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Aftermarket Value (Sealed Sets)", f"${sealed_value:,.0f}")
col2.metric("Total Retail Price (Sealed Sets)", f"${sealed_price:,.0f}")
col3.metric("Average Sealed Set Value / Retail Price", f"{sealed_ratio:.2f}x")

col4, col5, col6 = st.columns(3)
col4.metric("Total Aftermarket Value (Open Sets)", f"${open_value:,.0f}")
col5.metric("Total Retail Price (Open Sets)", f"${open_price:,.0f}")
col6.metric("Average Open Set Value / Retail Price", f"{open_ratio:.2f}x")

st.metric("Average Parts per Set", f"{avg_parts:,.0f}")

st.subheader("Correlation Explorer")

x_axis = st.selectbox(" X-axis", ["num_parts", "year", "retail_price"])
y_axis = st.selectbox("Y-axis", ["aftermarket_value", "retail_price"])

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

st.subheader("Theme-Level Value Trends")
theme_avg = df.groupby("theme")[["retail_price", "aftermarket_value"]].mean().reset_index()

fig2 = px.bar(
    theme_avg.sort_values("aftermarket_value", ascending=False).head(20),
    x="theme",
    y="aftermarket_value",
    title="Top Themes by Avg Aftermarket Value"
)

st.plotly_chart(fig2, use_container_width=True)
