"""
This page demonstrates backtesting a given contract type, and certain choice of parameters.
"""

import dash
import numpy as np

from dash import Input, Output, callback, dcc, html

from src.runbacktest import run_backtest
from src.plots.backtest_plots import (
    plot_cashflow,
    plot_irr,
    plot_irr_histogram,
)

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
                html.Br(),
                html.P(
                    "Cashflow of selected Trade. Hover on plot above to select trade."
                ),
                dcc.Graph(id="backtest-one"),
            ],
            style={"display": "inline-block", "width": "69%"},
        ),
        html.Div(
            [
                # Two small figures on the right : histogram and trade details
                html.P("Rate of Returns Histogram"),
                dcc.Graph(id="backtest-hist"),
                html.Br(),
                html.P("Trade Details"),
                # dcc.Graph(id="backtest-one"),
            ],
            style={
                "width": "29%",
                "display": "inline-block",
            },
        ),
        dcc.Store(id="backtest-stats", storage_type="session"),
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
    Output("backtest-hist", "figure"),
    Output("backtest-stats", "data"),
    Input("ctr-params", "data"),
)
def update_irr_graph(contract_params):
    """Run the backtest and plot the rate of return for each trade date.
    The hover in this plot triggers the cashflow plot."""

    df, stats = run_backtest(contract_params=contract_params)

    fig1 = plot_irr(df["date"], df["irr"])
    fig2 = plot_irr_histogram(df["irr"])

    return fig1, fig2, stats


@callback(
    Output("backtest-one", "figure"),
    Input("backtest-all", "hoverData"),
    Input("backtest-stats", "data"),
)
def update_backtest_cashflow(hoverData, stats):
    """Plot the cashflow of the selected trade date."""

    idx = hoverData["points"][0]["customdata"]

    prc_ts = stats["ts"][idx]
    cf = stats["stats"][idx]
    x = np.array(cf[0]).astype("datetime64[ms]")
    y = np.array(cf[1])

    return plot_cashflow(x, y, prc_ts)
