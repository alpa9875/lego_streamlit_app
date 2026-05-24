import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("🎨 Color Analytics")

engine = get_engine()

@st.cache_data(ttl=300)
def load_color_parts():
    query = """
        SELECT 
            color_name,
            SUM(quantity) AS total_qty
        FROM parts_drawers
        GROUP BY color_name
    """
    return pd.read_sql(query, engine)

colors = load_color_parts().sort_values("total_qty", ascending=False)

st.subheader("Top Colors by Quantity")
st.dataframe(colors)

fig = px.bar(
    colors.head(30),
    x="color_name",
    y="total_qty",
    title="Top 30 Colors by Quantity"
)
st.plotly_chart(fig, use_container_width=True)
