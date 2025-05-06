import streamlit as st

from pages import *

st.page_link(pg_home, label="Home", icon="🏠")

st.title(":exploding_head: Workout Wednesday")

st.markdown(
    """
Workout Wednesday is a weekly challenge to re-create a data-driven visualization.
The challenges are designed originally to kick-start personal development in *Tableau* and 
*Power BI*.

In this streamlit app, I try to sharpen my skills in data visualization with *Plotly* (mainly)
and *Stremalit*, replicating the original visualization as closely as possible.
"""
)

st.header(":grinning: WOW 2025", divider="rainbow")

row1 = st.columns(7)
with row1[0]:
    st.page_link(
        pg_wow25week15,
        label="**Week 15**",
        icon="📅",
        help="Open Week 15 challenge",
    )
with row1[1]:
    st.page_link(
        pg_wow25week16,
        label="**Week 16**",
        icon="📅",
        help="Open Week 16 challenge",
    )
