import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("Part Analytics")

engine = get_engine()

@st.cache_data(ttl=300)
def load_parts():
  query = """
    SELECT
      spi.part_num,
      p.name,
      pc.name AS category,
      spi.grand_total_qty AS total_quantity
    FROM set_part_inventory spi
    JOIN parts p
      ON spi.part_num = p.part_num
    JOIN part_categories pc
      ON p.part_cat_id = pc.id
  """
  return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_category_stats():
    query = """
        SELECT 
            pc.name AS category,
            SUM(spi.grand_total_qty) AS total_qty,
            SUM(spi.grand_total_qty * COALESCE(pp.avg_used_price, 0)) AS total_used_value
        FROM set_part_inventory spi
        JOIN parts p ON p.part_num = spi.part_num
        JOIN part_categories pc ON pc.id = p.part_cat_id
        LEFT JOIN part_prices pp ON pp.part_num = spi.part_num
        GROUP BY pc.name
        ORDER BY total_qty DESC;
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_total_parts_value():
    query = """
        SELECT 
            SUM(spi.grand_total_qty * COALESCE(pp.avg_used_price, 0)) AS total_used_value
        FROM set_part_inventory spi
        LEFT JOIN part_prices pp 
            ON pp.part_num = spi.part_num;
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_rarity_data():
    query = """
        SELECT
          spi.part_num,
          spi.grand_total_qty AS total_qty,
          COALESCE(pp.avg_used_price, 0) AS avg_used_price,
          COALESCE(sa.appearance_count, 1) AS appearance_count
        FROM set_part_inventory spi
        LEFT JOIN part_prices pp 
          ON pp.part_num = spi.part_num
        LEFT JOIN (
            SELECT 
              part_num, 
              COUNT(DISTINCT inventory_id) AS appearance_count
            FROM inventory_parts
            GROUP BY part_num
        ) sa ON sa.part_num = spi.part_num;
    """
    return pd.read_sql(query, engine)

cat_stats = load_category_stats()

st.subheader("Quantity of Parts per Category")
fig_cat_qty = px.bar(
    cat_stats,
    x="category",
    y="total_qty",
    title="Total Quantity per Category"
)
st.plotly_chart(fig_cat_qty, use_container_width=True)

st.subheader("Total Used Value per Category")
fig_cat_val = px.bar(
    cat_stats,
    x="category",
    y="total_used_value",
    title="Total Used Value per Category"
)
st.plotly_chart(fig_cat_val, use_container_width=True)

parts = load_parts()
parts["rarity_index"] = 1 / (parts["total_quantity"] +1)

st.subheader("Rarest Parts (by quantity on hand)")
top_rare = parts.sort_values("rarity_index", ascending=False).head(50)
st.dataframe(top_rare)

st.subheader("Rarity vs Quantity")
fig = px.scatter(
  parts,
  x="total_quantity",
  y="rarity_index",
  hover_data=["part_num", "category"],
  title="Rarity Index vs Quantity"
)
st.plotly_chart(fig, use_container_width=True)

rar = load_rarity_data()

rar["appearance_rarity"] = 1 / rar["appearance_count"]

rar["value_weighted_rarity"] = (
    (rar["avg_used_price"] / rar["avg_used_price"].max()) *
    (1 / rar["appearance_count"])
)

rar["composite_rarity"] = (
    0.4 * rar["appearance_rarity"] +
    0.3 * (1 / rar["total_qty"]) +
    0.3 * rar["value_weighted_rarity"]
)

st.subheader("Top 50 Rarest Parts (Composite Score)")
st.dataframe(
    rar.sort_values("composite_rarity", ascending=False).head(50)
)

fig_rar = px.scatter(
    rar,
    x="total_qty",
    y="composite_rarity",
    hover_data=["part_num"],
    title="Composite Rarity vs Quantity"
)
st.plotly_chart(fig_rar, use_container_width=True)

st.subheader("Total Value of All Parts (Used Prices)")

total_val_df = load_total_parts_value()
total_val = total_val_df["total_used_value"][0]

st.metric("Total Average Used Price of All Parts", f"${total_val:,.2f}")

