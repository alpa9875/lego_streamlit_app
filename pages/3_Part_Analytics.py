import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("Part Analytics")

engine = get_engine()

@st.cache_data(ttl=300)
def load_parts()
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
