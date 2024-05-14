"""
This page demonstrates backtesting a given contract type, and certain choice of parameters.
"""
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html
from src.runbacktest import run_backtest
from src.model import MS_IN_DAY
from datetime import datetime
import pytz

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                # Two long timeseries plots on the left
                html.P("Rate of Return for each Trade Date"),
                dcc.Graph(
                    id="backtest-all",
                    hoverData={"points": [{"customdata": 0}]},
                ),
                html.P("Cashflow of selected Trade"),
                dcc.Graph(id="backtest-one"),
            ],
            style={"display": "inline-block", "width": "69%"},
        ),
        html.Div(
            [
                # Two small figures on the right (TBC)
            ],
            style={
                "width": "29%",
                "display": "inline-block",
                "padding": "0 20",
            },
        ),
        dcc.Store(id="backtest_stats", storage_type="session"),
    ],
    style={
        "position": "fixed",
        "top": 10,
        "left": "25%",
        "width": "75%",
    },
)


@callback(
    Output("backtest-all", "figure"),
    Output("backtest_stats", "data"),
    Input("contract_inputs", "data"),
)
def update_irr_graph(contract_params):
    """Run the backtest and plot the rate of return for each trade date.
    The hover in this plot triggers the cashflow plot."""

    df, stats = run_backtest(contract_params=contract_params)

    fig = px.scatter(
        x=df["date"],
        y=df["irr"],
        # hover_name=df["date"].strftime("%Y-%m-%d"),
        labels={"x": "Trade Date", "y": "Rate of Return"},
        template="plotly_dark",
    )

    fig.update_traces(customdata=np.arange(len(df)))

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        yaxis={"tickformat": ",.1%"},
    )
    return fig, stats


@callback(
    Output("backtest-one", "figure"),
    Input("backtest-all", "hoverData"),
    Input("backtest_stats", "data"),
)
def update_backtest_cashflow(hoverData, stats):
    """Plot the cashflow of the selected trade date."""

    idx = hoverData["points"][0]["customdata"]

    prc_ts = stats["ts"][idx]
    cf = stats["stats"][idx]
    x = np.array(cf[0]).astype("datetime64[ms]")
    y = np.array(cf[1])

    # TODO: use red/green color for cashflows
    # TODO: consider rounded.
    fig = px.bar(
        x=x,
        y=y,
        labels={"x": "Trade Date", "y": "Cashflows"},
        template="plotly_dark",
    )
    fig.update_layout(height=225, margin={"l": 20, "b": 30, "r": 10, "t": 10})
    fig.update_traces(width=MS_IN_DAY * 2)

    # Annotate the trade and the last cashflow date
    datefmt = "%Y-%m-%d"
    prc_dt = datetime.fromtimestamp(prc_ts // 1000000000, pytz.utc)
    fig.add_annotation(
        x=prc_dt,
        text=f"Trade Date<br><b>{prc_dt.strftime(datefmt)}</b>",
    )
    end_dt = pd.to_datetime(x[-1])
    fig.add_annotation(
        x=end_dt,
        text=f"Last Cashflow Date<br><b>{end_dt.strftime(datefmt)}</b>",
    )
    return fig
