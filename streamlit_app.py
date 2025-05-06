import streamlit as st

from pages import *

pages = {
    "": [pg_home],
    "Workout Wednesday 2025": [
        pg_wow25week15,
        pg_wow25week16,
    ],
}

pg = st.navigation(pages)
pg.run()
