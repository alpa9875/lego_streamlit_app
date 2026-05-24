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
