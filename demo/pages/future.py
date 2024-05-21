"""
This page demonstrates backtesting a given contract type, and show IRR and cashflow.
"""

import dash
from dash import Input, Output, callback, dcc, html
from src.plots.future_plots import plot_cf_vs_spot
from src.future_cf import model_cashflows

dash.register_page(__name__)

layout = html.Div(
    [
        html.Div(
            [
                # Contract vs Spots Graph.
                html.P("Contract vs Spot Returns"),
                dcc.Graph(id="future-about"),
                html.Br(),
                dcc.Markdown(
                    """
                    The cashflow of the **contract** depends on the spot returns.
                    For a vanilla option it relates to the **return at maturity** alone. However,
                    for other contracts, knockouts and calls make the cashflow depend on prices
                    prior to maturity.
                    In the plot above, a **pricing model** produced the projection of future
                    asset returns.
                """
                ),
            ],
            style={"display": "inline-block", "width": "95%"},
        ),
    ],
    style={
        "position": "fixed",
        "top": 10,
        "left": "25%",  # Sidebar takes the left 25% of the screen.
        "width": "50%",
    },
)


@callback(
    Output("future-about", "figure"),
    Input("ctr-params", "data"),
)
def update_about(contract_params):
    """Run the backtest and plot the returns for each trade date.
    The hover in this plot triggers the cashflow plot."""

    x, y = model_cashflows(contract_params)

    fig = plot_cf_vs_spot(x, y, ticker=contract_params["ticker"])

    return fig
