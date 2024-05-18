"""
This page demonstrates backtesting a given contract type, and show IRR and cashflow.
"""

import dash
from dash import Input, Output, callback, dcc, html
from src.backtest import run_backtest
from src.plots.backtest_plots import (
    plot_cashflow,
    plot_irr,
)

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                # IRR graph on the top, and cashflow graph below.
                html.P("Returns for each Trade Date"),
                dcc.Graph(
                    id="past-irr",
                    hoverData={"points": [{"customdata": 0}]},
                ),
                html.Br(),
                html.P(
                    "Cashflow of selected Trade. Hover on plot above to select trade."
                ),
                dcc.Graph(id="past-cf"),
            ],
            style={"display": "inline-block", "width": "95%"},
        ),
        dcc.Store(id="past-data", storage_type="session"),
    ],
    style={
        "position": "fixed",
        "top": 10,
        "left": "25%",  # Sidebar takes the left 25% of the screen.
        "width": "75%",
    },
)


@callback(
    Output("past-irr", "figure"),
    Output("past-data", "data"),
    Input("ctr-params", "data"),
)
def update_irr_graph(contract_params):
    """Run the backtest and plot the returns for each trade date.
    The hover in this plot triggers the cashflow plot."""

    annualized = contract_params["ctr-type"] in ["AutoCallable"]

    df, stats = run_backtest(
        contract_params=contract_params, annualized=annualized
    )

    fig1 = plot_irr(
        df["date"],
        df["irr"],
        annualized=annualized,
        ticker=contract_params["ticker"],
    )

    return fig1, stats


@callback(
    Output("past-cf", "figure"),
    Input("past-irr", "hoverData"),
    Input("past-data", "data"),
)
def update_backtest_cashflow(hoverData, stats):
    """Plot the cashflow of the selected trade date."""

    idx = hoverData["points"][0]["customdata"]
    return plot_cashflow(
        stats["ts"][idx], stats["stats"][idx], stats["ticker"]
    )
