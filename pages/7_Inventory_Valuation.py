import streamlit as st
import pandas as pd
from utils.db import get_engine

st.title("💰 Inventory Valuation")

engine = get_engine()

@st.cache_data(ttl=300)
def load_inventory():
    query = """
        SELECT 
            set_num,
            name,
            retail_price,
            retail_value,
            quantity,
            num_parts,
            is_sealed
        FROM personal_set_inv
    """
    return pd.read_sql(query, engine)

df = load_inventory()
df["total_retail_price"] = df["retail_price"] * df["quantity"]
df["total_retail_value"] = df["retail_value"] * df["quantity"]

@st.cache_data(ttl=300)
def load_set_value_metrics():
    query = """
        SELECT
            set_num,
            name,
            retail_price,
            retail_value,
            quantity,
            is_sealed,
            CASE 
                WHEN retail_price > 1 THEN (retail_value - retail_price) / retail_price
                ELSE NULL
            END AS appreciation_pct
        FROM personal_set_inv;
    """
    return pd.read_sql(query, engine)

val = load_set_value_metrics()

sealed = val[val["is_sealed"] == True]
open_sets = val[val["is_sealed"] == False]

sealed_best = sealed.sort_values("appreciation_pct", ascending=False).head(1)

sealed_worst = sealed.sort_values("appreciation_pct", ascending=True).head(1)

open_best = open_sets.sort_values("appreciation_pct", ascending=False).head(1)

open_worst = open_sets.sort_values("appreciation_pct", ascending=True).head(1)

avg_retail_value = val["retail_value"].mean()

st.subheader("Portfolio Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total sets", int(df["quantity"].sum()))
col2.metric("Total retail price (paid)", f"${df['total_retail_price'].sum():,.0f}")
col3.metric("Total current value", f"${df['total_retail_value'].sum():,.0f}")

st.subheader("Per‑set valuation")
st.dataframe(
    df[["set_num", "name", "quantity", "retail_price", "retail_value",
        "total_retail_price", "total_retail_value"]].sort_values("total_retail_value", ascending=False)
)
st.subheader("Set Appreciation Metrics")

col1, col2 = st.columns(2)
sealed_best_pct = sealed_best['appreciation_pct'].iloc[0] * 100
sealed_best_name = sealed_best['name'].iloc[0]
col1.metric(
    "Greatest Appreciation (Sealed Sets)",
    sealed_best_name,
    f"{sealed_best_pct:.1f}%"
)
sealed_worst_pct = sealed_worst['appreciation_pct'].iloc[0] * 100
sealed_worst_name = sealed_worst['name'].iloc[0]
col2.metric(
    "Greatest Depreciation (Sealed Sets)",
    sealed_worst_name,
    f"{sealed_worst_pct:.1f}%",
    delta_color="normal"
)

col3, col4 = st.columns(2)
open_best_pct = open_best['appreciation_pct'].iloc[0] * 100
open_best_name = open_best['name'].iloc[0]
col3.metric(
    "Greatest Appreciation (Open Sets)",
    open_best_name,
    f"{open_best_pct:.1f}%"
)
open_worst_pct = open_worst['appreciation_pct'].iloc[0] * 100
open_worst_name = open_worst['name'].iloc[0]
col4.metric(
    "Greatest Depreciation (Open Sets)",
    open_worst_name,
    f"{open_worst_pct:.1f}%",
    delta_color="normal"
)

st.metric(
    "Average Retail Value of My Sets",
    f"${avg_retail_value:,.0f}"
)
