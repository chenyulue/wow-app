import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objects as go

import inspect

st.title("#WOW2025 WEEK 15")
st.markdown("#### Visualize the population by age and gender in a population pyramid")

DATA_SOURCE = "https://gitee.com/chenyulue/data_samples/raw/main/wow/EU27_population_2015-2024.CSV"


@st.cache_data
def load_data(data_source):
    data_df = pd.read_csv(data_source, dtype_backend="pyarrow")

    ages = data_df["Age"].str.extract(r"(?P<age>\d+)").astype(int)
    age_rank = np.where(
        ages < 15, "Young", np.where(ages < 65, "Active population", "Elders")
    )

    population_total = (
        data_df.loc[:, ["Country", "Year", "Male", "Female"]]
        .groupby(["Country", "Year"])
        .sum()
        .sum(axis=1)
        .reset_index()
        .reset_index()
        .rename(columns={0: "Total"})
    )

    data_df_total = data_df.merge(population_total, on=["Country", "Year"])
    data_df_total = data_df_total.assign(
        Age_Rank=age_rank,
        Male_Ratio=data_df_total["Male"] / data_df_total["Total"],
        Female_Ratio=data_df_total["Female"] / data_df_total["Total"],
    )
    return data_df_total

@st.cache_data
def filter_data(data_df, country1, year1, country2, year2):
    data_filtered = data_df.query("Country == @country1 and Year == @year1")
    data_filtered_ref = data_df.query("Country == @country2 and Year == @year2")
    return data_filtered, data_filtered_ref

@st.cache_data
def plot(data_filtered, data_filtered_ref):
    female_colors = {
        "Elders": "#c46487",
        "Active population": "#D18EB0",
        "Young": "#DBB5D3",
    }
    male_colors = {
        "Elders": "#27aab0",
        "Active population": "#60BEBC",
        "Young": "#96D0C7",
    }
    line_color = "#632538"
    grid_color = "#F2F2F2"

    x_range = np.arange(-1, 1.1, 0.1) / 100

    data_custom = pd.concat(
        [
            data_filtered.reset_index(drop=True),
            data_filtered_ref.reset_index(drop=True).rename(columns=lambda x: f"{x}2"),
        ],
        axis=1,
    )

    hover_template = (
        "%{customdata[2]} <br>"
        "(%{customdata[7]})<br><br>"
        "<span style='fontsize:12px;font-weight:bold'>%{customdata[0]} - %{customdata[1]}</span><br>"
        "<span style='color:#c46487'>Female</span>: %{customdata[4]:,}<br>"
        "%{customdata[9]:.1%} of total population<br>"
        "<span style='color:#27aab0'>Male</span>: %{customdata[3]:,}<br>"
        "%{customdata[8]:.1%} of total population<br><br>"
        "<span style='fontsize:12px;font-weight:bold'>%{customdata[10]} - %{customdata[11]}</span><br>"
        "<span style='color:#c46487'>Female</span>: %{customdata[14]:,}<br>"
        "%{customdata[19]:.1%} of total population<br>"
        "<span style='color:#27aab0'>Male</span>: %{customdata[13]:,}<br>"
        "%{customdata[18]:.1%} of total population<br><br>"
        "<extra></extra>"
    )

    fig = go.Figure()
    fig.add_traces(
        [
            go.Bar(
                name="Female",
                x=data_filtered["Female_Ratio"],
                y=data_filtered["Age"],
                orientation="h",
                marker=dict(
                    color=[female_colors[age] for age in data_filtered["Age_Rank"]],
                ),
                showlegend=False,
                customdata=data_custom,
                hovertemplate=hover_template,
                hoverlabel=dict(
                    bgcolor="white",
                ),
            ),
            go.Bar(
                name="Male",
                x=-data_filtered["Male_Ratio"],
                y=data_filtered["Age"],
                orientation="h",
                marker=dict(
                    color=[male_colors[age] for age in data_filtered["Age_Rank"]],
                ),
                showlegend=False,
                customdata=data_custom,
                hovertemplate=hover_template,
                hoverlabel=dict(
                    bgcolor="white",
                ),
            ),
            go.Scatter(
                x=data_filtered_ref["Female_Ratio"],
                y=data_filtered_ref["Age"],
                mode="lines",
                line=dict(
                    color=line_color,
                ),
                showlegend=False,
                customdata=data_custom,
                hovertemplate=hover_template,
                hoverlabel=dict(
                    bgcolor="white",
                ),
            ),
            go.Scatter(
                x=-data_filtered_ref["Male_Ratio"],
                y=data_filtered_ref["Age"],
                mode="lines",
                line=dict(
                    color=line_color,
                ),
                showlegend=False,
                customdata=data_custom,
                hovertemplate=hover_template,
                hoverlabel=dict(
                    bgcolor="white",
                ),
            ),
        ]
    )

    fig.update_layout(
        width=1000,
        height=1000,
        barmode="relative",
        plot_bgcolor="white",
        xaxis=dict(
            range=[-1.01 / 100, 1.01 / 100],
            tickmode="array",
            tickvals=x_range,
            ticktext=[f"{abs(x):.1%}" if abs(x) >= 0.0001 else "" for x in x_range],
            ticks="",
            gridcolor=grid_color,
        ),
        yaxis=dict(
            ticks="",
            showticklabels=False,
            range=[-1, len(data_filtered)],
        ),
        margin=dict(
            t=120,
            b=80,
            l=4,
            r=4,
        ),
    )

    fig.add_annotation(
        text="Male",
        showarrow=False,
        xref="x domain",
        x=0.25,
        xanchor="center",
        yref="y domain",
        y=0,
        yanchor="top",
        yshift=-20,
        font_weight="bold",
    )

    fig.add_annotation(
        text="Female",
        showarrow=False,
        xref="x domain",
        x=0.75,
        xanchor="center",
        yref="y domain",
        y=0,
        yanchor="top",
        yshift=-20,
        font_weight="bold",
    )

    fig.add_annotation(
        text=(
            "Challenged by <span style='color:#27aab0'>Chenyu Lue</span> | "
            "Week 15 <span style='color:#27aab0'>#WorkoutWednesday</span> | "
            "Data: <span style='color:#27aab0'>EUROSTAT</span>"
        ),
        showarrow=False,
        xref="x domain",
        x=0.5,
        xanchor="center",
        yref="y domain",
        y=0,
        yanchor="top",
        yshift=-50,
    )

    ann_width = 165
    ann_height = 80

    fig.add_annotation(
        text=(
            "<b>Male</b><br>"
            f"<b>{data_filtered['Country'].iloc[0]}-{data_filtered['Year'].iloc[0]}</b>  "
            f"<span style='color:{male_colors['Elders']}'>■</span> Elders<br>"
            f"<span style='color:{male_colors['Active population']}'>■</span> Active population "
            f"<span style='color:{male_colors['Young']}'>■</span> Young<br>"
            f"<b>{data_filtered_ref['Country'].iloc[0]}-{data_filtered_ref['Year'].iloc[0]}</b> "
            f"<span style='color:{line_color}'>─</span>"
        ),
        xref="x domain",
        x=0.25,
        xanchor="right",
        yref="y domain",
        y=1,
        yanchor="bottom",
        yshift=10,
        showarrow=False,
        align="center",
        bgcolor="#F5F5F5",
        width=ann_width,
        height=ann_height,
    )
    fig.add_annotation(
        text=(
            "<b>Female</b><br>"
            f"<b>{data_filtered['Country'].iloc[0]}-{data_filtered['Year'].iloc[0]}</b>  "
            f"<span style='color:{female_colors['Elders']}'>■</span> Elders<br>"
            f"<span style='color:{female_colors['Active population']}'>■</span> Active population "
            f"<span style='color:{female_colors['Young']}'>■</span> Young<br>"
            f"<b>{data_filtered_ref['Country'].iloc[0]}-{data_filtered_ref['Year'].iloc[0]}</b> "
            f"<span style='color:{line_color}'>─</span>"
        ),
        xref="x domain",
        x=1,
        xanchor="right",
        yref="y domain",
        y=1,
        yanchor="bottom",
        yshift=10,
        showarrow=False,
        align="center",
        bgcolor="#F5F5F5",
        width=ann_width,
        height=ann_height,
    )

    fig.add_annotation(
        text=(
            "Total Population<br>"
            f"<b>{data_filtered['Country'].iloc[0]}-{data_filtered['Year'].iloc[0]}</b>:<br><br>"
            f"<span style='font-size:18px'>{data_filtered['Total'].iloc[0]:,.0f}</span>"
        ),
        xref="x domain",
        x=0.5,
        xanchor="right",
        yref="y domain",
        y=1,
        yanchor="bottom",
        yshift=10,
        showarrow=False,
        align="center",
        bgcolor="#F5F5F5",
        width=ann_width,
        height=ann_height,
    )
    fig.add_annotation(
        text=(
            "Total Population<br>"
            f"<b>{data_filtered_ref['Country'].iloc[0]}-{data_filtered_ref['Year'].iloc[0]}</b>:<br><br>"
            f"<span style='font-size:18px'>{data_filtered_ref['Total'].iloc[0]:,.0f}</span>"
        ),
        xref="x domain",
        x=0.75,
        xanchor="right",
        yref="y domain",
        y=1,
        yanchor="bottom",
        yshift=10,
        showarrow=False,
        align="center",
        bgcolor="#F5F5F5",
        width=ann_width,
        height=ann_height,
    )
    return fig

data_df_total = load_data(DATA_SOURCE)

countries = np.sort(data_df_total["Country"].unique())
years = np.sort(data_df_total["Year"].unique())

cols = st.columns(4)
with cols[0]:
    Country1 = st.selectbox("**Country1**", countries, index=14)
with cols[1]:
    Year1 = st.selectbox("**Year1**", years, index=len(years) - 1)
with cols[2]:
    Country2 = st.selectbox("**Country2**", countries)
with cols[3]:
    Year2 = st.selectbox("**Year2**", years, index=len(years) - 1)

data_filtered, data_filtered_ref = filter_data(
    data_df_total, Country1, Year1, Country2, Year2
)

fig = plot(data_filtered, data_filtered_ref)
st.plotly_chart(fig, theme=None, use_container_width=True)

with st.expander("See the plot code"):
    st.code(inspect.getsource(plot))