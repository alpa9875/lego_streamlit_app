import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("🎨 Color Analytics")

engine = get_engine()

@st.cache_data(ttl=300)
def load_color_stats():
    query = """
        WITH user_inventories AS (
            SELECT 
                psi.set_num,
                psi.quantity,
                inv.id AS inventory_id
            FROM personal_set_inv psi
            JOIN inventories inv 
                ON inv.set_num = psi.set_num || '-1'
        ),

        user_parts AS (
            SELECT
                ui.inventory_id,
                ip.part_num,
                ip.color_id,
                ip.quantity * ui.quantity AS total_qty
            FROM user_inventories ui
            JOIN inventory_parts ip 
                ON ip.inventory_id = ui.inventory_id
        )

        SELECT
            c.name AS color_name,
            SUM(up.total_qty) AS total_qty,
            SUM(up.total_qty * COALESCE(pp.avg_used_price, 0)) AS total_used_value
        FROM user_parts up
        JOIN colors c ON c.id = up.color_id
        LEFT JOIN part_prices pp ON pp.part_num = up.part_num
        GROUP BY c.name
        ORDER BY total_qty DESC;
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_color_rarity():
    query = """
        WITH user_inventories AS (
            SELECT 
                psi.set_num,
                psi.quantity,
                inv.id AS inventory_id
            FROM personal_set_inv psi
            JOIN inventories inv 
                ON inv.set_num = psi.set_num || '-1'
        ),

        user_parts AS (
            SELECT
                ui.inventory_id,
                ip.part_num,
                ip.color_id
            FROM user_inventories ui
            JOIN inventory_parts ip 
                ON ip.inventory_id = ui.inventory_id
        ),

        color_appearance AS (
            SELECT 
                color_id,
                COUNT(DISTINCT inventory_id) AS set_count
            FROM user_parts
            GROUP BY color_id
        )

        SELECT
            c.name AS color_name,
            ca.set_count,
            1.0 / ca.set_count AS rarity_score
        FROM color_appearance ca
        JOIN colors c ON c.id = ca.color_id
        ORDER BY rarity_score DESC;
    """
    return pd.read_sql(query, engine)

color_stats = load_color_stats()

st.subheader("Quantity of Parts by Color")
fig_color_qty = px.bar(
    color_stats,
    x="color_name",
    y="total_qty",
    title="Total Quantity by Color"
)
st.plotly_chart(fig_color_qty, use_container_width=True)

st.subheader("Total Used Value by Color")
fig_color_val = px.bar(
    color_stats,
    x="color_name",
    y="total_used_value",
    title="Total Used Value by Color"
)
st.plotly_chart(fig_color_val, use_container_width=True)

color_rarity = load_color_rarity()

st.subheader("Color Rarity Score")
st.dataframe(color_rarity)
