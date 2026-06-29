import streamlit as st
import pandas as pd
from utils.db import get_engine
import plotly.express as px
from PIL import Image, ImageOps

st.title("Home Dashboard")

engine = get_engine()

@st.cache_data(ttl=300)
def load_inventory_summary():
    query = """
        SELECT
            (SELECT COUNT(*) FROM personal_set_inv) AS total_sets,
            (SELECT SUM(retail_price * quantity) FROM personal_set_inv) AS total_retail_price,
            (SELECT SUM(retail_value * quantity) FROM personal_set_inv) AS total_aftermarket_value,
            (SELECT SUM(grand_total_qty) FROM set_part_inventory) AS total_parts
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

image1 = ImageOps.exif_transpose(Image.open("images/20260628_181631.jpg"))
st.image(image1, caption = "Displayed Sets on Bookcase", use_column_width=True)

image2 = ImageOps.exif_transpose(Image.open("images/20260628_181724.jpg"))
st.image(image2, caption = "Displayed Sets on High Shelf", use_column_width=True)

image3 = ImageOps.exif_transpose(Image.open("images/20260628_181905.jpg"))
st.image(image3, caption = "Displayed Sets on Wire Shelf", use_column_width=True)

image4 = ImageOps.exif_transpose(Image.open("images/20260628_181951.jpg"))
st.image(image4, caption="Lego Room Angle 1", use_column_width=True)

image5 = ImageOps.exif_transpose(Image.open("images/20260628_182019.jpg"))
st.image(image5, caption="Lego Room Angle 2", use_column_width=True)