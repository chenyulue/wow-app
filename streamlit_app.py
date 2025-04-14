import streamlit as st

pages = {
    "": [st.Page("home.py", title="Home", icon="🏠")],
    "Workout Wednesday 2025": [
        st.Page(
            "wow/2025/week_15.py",
            title="Week 15 - Population Pyramid",
            icon="📅",
            url_path="wow25week15",
        )
    ],
}


pg = st.navigation(pages)
pg.run()
