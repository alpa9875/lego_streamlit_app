import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine
import plotly.graph_objects as go

st.title(" Planogram (Drawer Visualization)")

engine = get_engine()

@st.cache_data(ttl=300)
def load_drawer_coords():
  query = """
    SELECT
      drawer_id,
      x,
      y,
      width,
      height
    FROM drawer_ids
    ORDER BY drawer_id;
  """
  return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_inventory():
  query = """
    SELECT
      drawer_id,
      part_num,
      total_qty,
      avg_new_price,
      avg_used_price
    FROM price_qty_drawer_inv
    ORDER BY drawer_id, part_num;
  """
  return pd.read_sql(query, engine)

drawers = load_drawer_coords()
inv = load_inventory()

inv["price"] = inv["avg_used_price"].fillna(inv["avg_new_price"]).fillna(0.01)
inv["value"] = inv["total_qty"] * inv["price"]

drawer_values = (
  inv.groupby("drawer_id")["value"]
    .sum()
    .reset_index()
    .rename(columns={"value": "drawer_value"})
)

drawers = drawers.merge(drawer_values, on="drawer_id", how="left")
drawers["drawer_value"] = drawers["drawer_value"].fillna(0.01)

fig = go.Figure()

for _, row in drawers.iterrows():

  parts_in_drawer = inv[inv["drawer_id"] == row["drawer_id"]]

  parts_list = (
    parts_in_drawer
    .apply(lambda r: f"{r['part_num']} x {r['total_qty']} (${r['value']:.2f})", axis=1)
    .tolist()
  )
  parts_html = "<br>".join(parts_list)

  fig.add_shape(
    type="rect",
    x0=row["x"],
    y0=row["y"],
    x1=row["x"] + row["width"],
    y1=row["y"] + row["height"],
    line=dict(color="black", width=1),
    fillcolor="rgba(0, 150, 255, 0.3)"
  )

  fig.add_trace(go.Scatter(
    x=[row["x"] + row["width"] / 2],
    y=[row["y"] + row["height"] / 2],
    mode="markers",
    marker=dict(size=1, color="rgba(0,0,0,0)"),
    hovertemplate=(
      f"<b>Drawer:</b> {row['drawer_id']}<br>"
      f"<b>Total Value:</b> ${row['drawer_value']:.2f}<br>"
      f"<b>Contents:</b><br>{parts_html}<br>"
      "<extra></extra>"
    )
  ))
for x in [94, 194]:
  fig.add_shape(
    type="line",
    x0=x, y0=0,
    x1=x, y1=drawers["y"].max() + 10,
    line=dict(color="gray", dash="dot")
  )

fig.update_layout(
  title="LEGO ROOM Planogram",
  xaxis=dict(
    title="Inches (X)",
    range=[0, drawers["x"].max() +20],
    scaleanchor="y",
    scaleratio=1
  ),
  yaxis=dict(
    title="Inches (Y)",
    range=[0, 100],
    autorange=False,
    autorangeoptions=None
  ),
  width=1400,
  height=900,
  showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
      
