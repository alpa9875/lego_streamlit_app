import streamlit as st
import pandas as pd
from utils.db import get_engine

st.title("🔍 Set Explorer")

engine = get_engine()

@st.cache_data(ttl=300)
def load_sets():
    query = """
        SELECT 
            set_num,
            name,
            retail_price,
            retail_value,
            num_parts,
            quantity,
            is_sealed,
            is_built
        FROM personal_set_inv
    """
    return pd.read_sql(query, engine)

df = load_sets()

search = st.text_input("Search by set number or name")
filtered = df.copy()
if search:
    s = search.lower()
    filtered = df[df["set_num"].str.contains(s, case=False) | df["name"].str.lower().str.contains(s)]

st.subheader("Results")
st.dataframe(filtered)

if not filtered.empty:
    sel = st.selectbox("Select a set", filtered["set_num"])
    row = filtered[filtered["set_num"] == sel].iloc[0]
    st.markdown(f"**Name:** {row['name']}")
    st.markdown(f"**Retail price:** ${row['retail_price']:.2f}")
    st.markdown(f"**Retail value:** ${row['retail_value']:.2f}")
    st.markdown(f"**Parts:** {int(row['num_parts'])}")
    st.markdown(f"**Quantity owned:** {int(row['quantity'])}")
    st.markdown(f"**Sealed:** {row['is_sealed']}")
    st.markdown(f"**Built:** {row['is_built']}")
