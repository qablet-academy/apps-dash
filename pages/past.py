"""
This page demonstrates backtesting a given contract type, and show IRR and cashflow.
"""

import dash
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

from demo.src.backtest import run_backtest
from demo.src.plots.backtest_plots import blank_figure, plot_cashflow, plot_irr

dash.register_page(__name__)


layout = html.Div(
    [
        html.Div(
            [
                # IRR graph on the top, and cashflow graph below.
                html.P(
                    "Historical Returns for Trade Dates between Dec'19-Apr'24."
                ),
                dcc.Graph(
                    id="past-irr",
                    figure=blank_figure(),
                ),
                html.Br(),
                html.P(
                    "Cashflow of selected Trade. Hover on the points above to select a trade."
                ),
                dcc.Graph(id="past-cf", figure=blank_figure()),
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
def update_past_irr(contract_params):
    """Run the backtest and plot the returns for each trade date.
    The hover in this plot triggers the cashflow plot."""

    annualized = contract_params["ctr-type"] in [
        "Discount Certificate",
        "Reverse Convertible",
    ]

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
def update_past_cashflow(hoverData, stats):
    """Plot the cashflow of the selected trade date."""

    if hoverData is None or stats is None:
        raise PreventUpdate
    point = hoverData["points"][0]
    # curveNumber 0 is the scatter trace; 1 is the histogram — ignore histogram hovers
    if point.get("curveNumber") != 0:
        raise PreventUpdate
    idx = point["pointIndex"]
    return plot_cashflow(
        stats["ts"][idx], stats["stats"][idx], stats["ticker"]
    )
