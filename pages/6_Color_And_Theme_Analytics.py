import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_engine

st.title("Color and Theme Analytics in Sets")

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

@st.cache_data(ttl=300)
def load_theme_stats():
    query = """
        SELECT
            t.name AS theme,
            COUNT(*) AS num_sets
        FROM personal_set_inv psi
        JOIN sets s 
            ON s.set_num = psi.set_num || '-1'
        JOIN themes t 
            ON t.id = s.theme_id
        GROUP BY t.name
        ORDER BY num_sets DESC;
    """
    return pd.read_sql(query, engine)

color_stats = load_color_stats()

st.subheader("Quantity of Parts by Color in Sets")
fig_color_qty = px.bar(
    color_stats,
    x="color_name",
    y="total_qty",
    title="Total Quantity by Color"
)
st.plotly_chart(fig_color_qty, use_container_width=True)

st.subheader("Total Used Value by Color in Sets")
fig_color_val = px.bar(
    color_stats,
    x="color_name",
    y="total_used_value",
    title="Total Used Value by Color"
)
st.plotly_chart(fig_color_val, use_container_width=True)

color_rarity = load_color_rarity()

st.subheader("Color Rarity Score in Sets")
st.dataframe(color_rarity)

total_colors = color_stats["color_name"].nunique()

max_color_row = color_stats.loc[color_stats["total_qty"].idxmax()]
max_color_name = max_color_row["color_name"]
max_color_qty = max_color_row["total_qty"]

min_color_row = color_stats.loc[color_stats["total_qty"].idxmin()]
min_color_name = min_color_row["color_name"]
min_color_qty = min_color_row["total_qty"]

st.subheader("Set Color Summary Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Number of Colors in Sets",
    f"{total_colors}"
)

col2.metric(
    "Most Common Color in Sets (by Quantity)",
    f"{max_color_name}",
    f"{max_color_qty:,}"
)

col3.metric(
    "Least Common Color in Sets (by Quantity)",
    f"{min_color_name}",
    f"{min_color_qty:,}"
)
themes = load_theme_stats()
total_themes = themes["theme"].nunique()

max_theme_row = themes.loc[themes["num_sets"].idxmax()]
max_theme_name = max_theme_row["theme"]
max_theme_count = max_theme_row["num_sets"]

min_theme_row = themes.loc[themes["num_sets"].idxmin()]
min_theme_name = min_theme_row["theme"]
min_theme_count = min_theme_row["num_sets"]

st.subheader("Theme Summary Metrics")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Number of Themes",
    f"{total_themes}"
)

col2.metric(
    "Theme With Most Sets",
    f"{max_theme_name}",
    f"{max_theme_count}"
)

col3.metric(
    "Theme With Fewest Sets",
    f"{min_theme_name}",
    f"{min_theme_count}"
)
st.subheader("Number of Sets per Theme")

fig = px.bar(
    themes,
    x="theme",
    y="num_sets",
    title="Sets per Theme",
)
st.plotly_chart(fig, use_container_width=True)
