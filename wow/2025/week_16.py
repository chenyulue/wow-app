import datetime

import streamlit as st
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

# from pages import pg_home

# st.page_link(pg_home, label="Home", icon="🏠")

if "state" not in st.session_state:
    st.session_state.state = "Pennsylvania"
if "bar_state" not in st.session_state:
    st.session_state.bar_state = st.session_state.state


st.title("[#WOW2025 WEEK 16](https://workout-wednesday.com/2025w16tab/)")
st.markdown("#### Visualize the population by age and gender in a population pyramid")

DATA_SOURCE = (
    "https://gitee.com/chenyulue/data_samples/raw/main/wow/Sample-Superstore_Orders.csv"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_SOURCE, parse_dates=["Order Date"], dtype_backend="pyarrow")


@st.cache_data
def transform_data(data_df: pd.DataFrame) -> pd.DataFrame:
    profit_ratio_vs_sales = (
        data_df.loc[:, ["State", "Profit"]]
        .assign(
            Sales=data_df["Sales"]
            .str.replace(r",|\$", "", regex=True)
            .astype(np.float64)
        )
        .groupby("State")
        .sum()
    )

    return profit_ratio_vs_sales.assign(
        Profit_Ratio=profit_ratio_vs_sales["Profit"] / profit_ratio_vs_sales["Sales"]
    )


colors = {
    "selected": "#76797C",
    "not_selected": "#C4C4C4",
    "bar_other": "#C0D3D9",
}

try:
    points = st.session_state.points["selection"]["points"]
    if points:
        st.session_state.state = points[0]["customdata"][0]

    bars = st.session_state.bars["selection"]["points"]
    if bars:
        st.session_state.bar_state = bars[0]["y"]
    else:
        st.session_state.bar_state = st.session_state.state
except AttributeError:
    pass


@st.cache_data
def plot_profit_ratio_vs_sales(
    profit_ratio_vs_sales: pd.DataFrame,
    state: str,
):
    x0 = profit_ratio_vs_sales["Sales"].quantile(0.25)
    x1 = profit_ratio_vs_sales["Sales"].quantile(0.75)
    y0 = profit_ratio_vs_sales["Profit_Ratio"].quantile(0.25)
    y1 = profit_ratio_vs_sales["Profit_Ratio"].quantile(0.75)

    fig = go.Figure()

    fig.add_traces(
        [
            go.Scatter(
                mode="markers",
                x=profit_ratio_vs_sales["Sales"],
                y=profit_ratio_vs_sales["Profit_Ratio"],
                customdata=profit_ratio_vs_sales.reset_index(),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br><br>"
                    "<b>Profit Ratio:</b> %{customdata[3]:.0%}<br>"
                    "<b>Sales:</b> $%{customdata[2]:.3s}<extra></extra>"
                ),
                hoverlabel=dict(
                    bgcolor="white",
                ),
                marker=dict(
                    color=[
                        colors["selected"] if x == state else colors["not_selected"]
                        for x in profit_ratio_vs_sales.index
                    ],
                    line_color=colors["selected"],
                    size=[10 if x == state else 6 for x in profit_ratio_vs_sales.index],
                ),
            )
        ]
    )

    line_style = dict(
        color="#B4B4B4",
        width=1,
        dash="dot",
    )

    fig.add_vline(
        x=profit_ratio_vs_sales["Sales"].median(),
        line=line_style,
    )
    fig.add_hline(
        y=profit_ratio_vs_sales["Profit_Ratio"].median(),
        line=line_style,
    )

    fig.add_shape(
        type="rect",
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        fillcolor="#DEFAFA",
        line_color="rgba(255,255,255,0)",
        layer="below",
    )

    fig.update_layout(
        width=650,
        height=450,
        yaxis=dict(
            range=[-0.4, 0.4],
            tickformat=".0%",
            showgrid=False,
            zerolinecolor="#CBCBCB",
            zerolinewidth=1,
            title=dict(
                text="Profit Ratio",
                font_weight="bold",
            ),
        ),
        xaxis=dict(
            tickformat="$,.0r",
            showgrid=False,
            zerolinecolor="#CBCBCB",
            zerolinewidth=1,
            title=dict(
                text="Sales",
                font_weight="bold",
            ),
        ),
        plot_bgcolor="white",
        title=dict(
            text="Profit Ratio vs Sales by State",
            subtitle=dict(
                text=f"<b>{state}</b> vs Other States<br>Reference box shows 25th & 75th percentiles for each measures."
            ),
            x=0,
            xref="paper",
            xanchor="left",
        ),
    )

    profit_ratio_vs_sales_filtered = profit_ratio_vs_sales.query(
        "Sales>=@x0 and Sales<=@x1 and Profit_Ratio>=@y0 and Profit_Ratio<=@y1"
    )

    return fig, profit_ratio_vs_sales_filtered


@st.cache_data
def plot_bar_chart(
    profit_ratio_vs_sales: pd.DataFrame,
    profit_ratio_vs_sales_filtered: pd.DataFrame,
    state: str,
):
    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
    )

    sales_df = (
        profit_ratio_vs_sales_filtered["Sales"]
        .sort_values()
        .reset_index()
        .query("State!=@state")
    )
    profit_ratio_df = (
        profit_ratio_vs_sales_filtered["Profit_Ratio"]
        .reset_index()
        .query("State!=@state")
    )

    bar_df = pd.concat(
        [
            sales_df.merge(profit_ratio_df, on="State", how="left"),
            pd.DataFrame(
                [
                    state,
                    profit_ratio_vs_sales.loc[state, "Sales"],
                    profit_ratio_vs_sales.loc[state, "Profit_Ratio"],
                ],
                index=["State", "Sales", "Profit_Ratio"],
            ).T,
        ],
        axis=0,
    )

    bar_colors = [
        colors["bar_other"] if x != state else colors["selected"]
        for x in bar_df["State"]
    ]

    fig.add_trace(
        go.Bar(
            name="Sales",
            x=bar_df["Sales"],
            y=bar_df["State"],
            orientation="h",
            marker=dict(
                color=bar_colors,
            ),
            showlegend=False,
            customdata=bar_df,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "<b>Sales:</b> %{customdata[1]:$,}<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="white",
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            name="Profit Ratio",
            x=bar_df["Profit_Ratio"],
            y=bar_df["State"],
            orientation="h",
            marker=dict(
                color=bar_colors,
            ),
            showlegend=False,
            customdata=bar_df,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "<b>Sales:</b> %{customdata[1]:$,}<br>"
                "<b>Profit Ratio:</b> %{customdata[2]:.0%}<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="white",
            ),
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        width=650,
        height=450,
        xaxis=dict(
            showgrid=False,
            tickformat="$,",
            title=dict(
                text="<b>Sales</b>",
            ),
        ),
        xaxis2=dict(
            showgrid=False, tickformat=".0%", title=dict(text="<b>Profit Ratio</b>")
        ),
        plot_bgcolor="white",
        title=dict(
            text="Sales & Profit Ratio Comparison",
            x=0,
            xref="paper",
            xanchor="left",
        ),
        margin=dict(
            t=40,
            b=40,
        ),
    )

    return fig, bar_df


@st.cache_data
def plot_profit_ratio_vs_sales_year(data_df, bar_df, state):
    profit_ratio_vs_sales_year = (
        data_df.loc[:, ["State", "Profit"]]
        .assign(
            Sales=data_df["Sales"]
            .str.replace(r",|\$", "", regex=True)
            .astype(np.float64),
            Order_Month=data_df["Order Date"]
            .dt.to_period("M")
            .apply(lambda x: x.to_timestamp()),
        )
        .groupby(["State", "Order_Month"])
        .sum()
    )

    profit_ratio_vs_sales_year = profit_ratio_vs_sales_year.assign(
        Profit_Ratio=profit_ratio_vs_sales_year["Profit"]
        / profit_ratio_vs_sales_year["Sales"]
    )

    profit_ratio_vs_sales_year = profit_ratio_vs_sales_year.reset_index()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    sales_line = []
    profit_ratio_line = []
    for x in bar_df["State"]:
        if x == state:
            color = colors["selected"]
            line_width = 3
            zorder = 5
        else:
            color = colors["bar_other"]
            line_width = 1
            zorder = 0
        if x == st.session_state.state:
            line_width = 3

        filtered_df = profit_ratio_vs_sales_year.query("State==@x")

        sales_line.append(
            go.Scatter(
                name=x,
                meta=[x],
                x=filtered_df["Order_Month"],
                y=filtered_df["Sales"],
                mode="lines",
                line=dict(
                    color=color,
                    width=line_width,
                ),
                showlegend=False,
                zorder=zorder,
                hovertemplate="<b>%{meta[0]}</b><br><b>%{x|%B %Y}</b><br>Sales: <b>%{y:$,}</b><extra></extra>",
                hoverlabel=dict(
                    bgcolor="white",
                ),
            )
        )

        profit_ratio_line.append(
            go.Scatter(
                name=x,
                meta=[x],
                x=filtered_df["Order_Month"],
                y=filtered_df["Profit_Ratio"],
                mode="lines",
                line=dict(
                    color=color,
                    width=line_width,
                ),
                showlegend=False,
                zorder=zorder,
                hovertemplate="<b>%{meta[0]}</b><br><b>%{x|%B %Y}</b><br>Sales: <b>%{y:.0%}</b><extra></extra>",
                hoverlabel=dict(
                    bgcolor="white",
                ),
            )
        )

    fig.add_traces(sales_line, rows=1, cols=1)
    fig.add_traces(profit_ratio_line, rows=2, cols=1)

    fig.update_layout(
        width=650,
        height=450,
        yaxis=dict(
            tickformat="$,",
            title=dict(
                text="Sales",
                font_weight="bold",
            ),
            showgrid=False,
            zerolinecolor="#CBCBCB",
            zerolinewidth=1,
        ),
        yaxis2=dict(
            tickformat=".0%",
            title=dict(
                text="Profit Ratio",
                font_weight="bold",
            ),
            showgrid=False,
            zerolinecolor="#CBCBCB",
            zerolinewidth=1,
        ),
        xaxis=dict(
            showgrid=False,
        ),
        xaxis2=dict(
            showgrid=False,
        ),
        plot_bgcolor="white",
        title=dict(
            text="Sales & Profit Ratio by Month",
            x=0,
            xref="paper",
            xanchor="left",
        ),
        margin=dict(
            t=30,
            b=20,
        ),
    )

    return fig


@st.cache_data
def plot_subcategory_sales(data_df, bar_df, state, year=None, month=None):
    data_state = data_df.loc[data_df["State"].isin(bar_df["State"]), :]
    if year is not None:
        data_state = data_state.loc[
            (data_state["Order Date"].dt.year == year)
            & (data_state["Order Date"].dt.month == month),
            :,
        ]

    data_subcategory = (
        data_state.loc[:, ["State", "Profit", "Sub-Category"]]
        .assign(
            Sales=data_state["Sales"]
            .str.replace(r",|\$", "", regex=True)
            .astype(np.float64)
        )
        .groupby(["State", "Sub-Category"])
        .sum()
    )

    data_subcategory = data_subcategory.assign(
        Profit_Ratio=data_subcategory["Profit"] / data_subcategory["Sales"]
    )

    max_profit_ratio, min_profit_ratio = (
        data_subcategory["Profit_Ratio"].max(),
        data_subcategory["Profit_Ratio"].min(),
    )

    data_subcategory = (
        data_subcategory.loc[(state,), :].sort_values(by="Sales").reset_index()
    )

    fig = go.Figure()

    fig.add_traces(
        [
            go.Bar(
                x=data_subcategory["Sales"],
                y=data_subcategory["Sub-Category"],
                orientation="h",
                marker=dict(
                    color=data_subcategory["Profit_Ratio"],
                    colorscale="Earth",
                    showscale=True,
                    cmax=max_profit_ratio,
                    cmin=min_profit_ratio,
                    cmid=(max_profit_ratio + min_profit_ratio) / 2,
                    colorbar=dict(
                        title=dict(
                            text="Profit Ratio",
                            side="top",
                        ),
                        len=0.5,
                        x=1,
                        xref="paper",
                        xanchor="left",
                        y=1,
                        yref="paper",
                        yanchor="top",
                        tickformat=".1%",
                    ),
                ),
                hovertemplate="Sub-Category: <b>%{y}</b><br>Sales: <b>%{x:$,}</b><br>Profit Ratio: <b>%{marker.color:.1%}</b><extra></extra>",
                hoverlabel=dict(
                    bgcolor="white",
                ),
            )
        ]
    )

    sub_title = f"<b>{state}</b>"
    if year is not None and month is not None:
        sub_title = f"<b>{state}</b> | <b>{datetime.datetime(year, month, 1).strftime('%B %Y')}</b>"
    fig.update_layout(
        width=650,
        height=450,
        title=dict(
            text="Sales & Profit Ratio by Subcategory",
            subtitle=dict(
                text=sub_title,
            ),
            x=0,
            xref="paper",
            xanchor="left",
        ),
        margin=dict(
            t=70,
            b=20,
        ),
        xaxis=dict(
            tickformat="$,",
            showgrid=False,
        ),
        plot_bgcolor="white",
    )

    return fig


data_df = load_data()
profit_ratio_vs_sales = transform_data(data_df)
fig_1, profit_ratio_vs_sales_filtered = plot_profit_ratio_vs_sales(
    profit_ratio_vs_sales, st.session_state.state
)
fig_2, bar_df = plot_bar_chart(
    profit_ratio_vs_sales, profit_ratio_vs_sales_filtered, st.session_state.state
)
fig_3 = plot_profit_ratio_vs_sales_year(data_df, bar_df, st.session_state.bar_state)
fig_4 = plot_subcategory_sales(data_df, bar_df, st.session_state.bar_state)


col1, col2 = st.columns([1, 1])

with col1:
    st.plotly_chart(
        fig_1, theme=None, key="points", on_select="rerun", selection_mode="points"
    )
    st.plotly_chart(
        fig_2, theme=None, key="bars", on_select="rerun", selection_mode="points"
    )

with col2:
    st.plotly_chart(
        fig_3, theme=None, key="lines", on_select="rerun", selection_mode="points"
    )
    st.plotly_chart(fig_4, theme=None)

print(st.session_state.lines)
