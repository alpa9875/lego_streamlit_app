import streamlit as st
import pandas as pd
from utils.db import get_engine

st.title("LEGO Analytics Dashboard")

engine = get_engine()

df = pd.read_sql("SELECT * FROM personal_set_inv LIMIT 20;", engine)

st.write("Sample of your data:")
st.dataframe(df)
