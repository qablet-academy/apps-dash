"""
This page shows future returns projected by model.
"""

import dash
import dash_daq as daq
from dash import Input, Output, callback, dcc, html
from src.future_cf import model_cashflows
from src.plots.backtest_plots import blank_figure
from src.plots.future_plots import plot_cf_vs_spot

dash.register_page(__name__)

layout = html.Div(
    [
        html.Div(
            [
                # Contract vs Spots Graph.
                html.P("Model Projected Contract vs Spot Returns"),
                dcc.Graph(
                    id="future-returns",
                    figure=blank_figure(),
                ),
                html.Br(),
                dcc.Markdown(
                    """
                    The cashflow of the **contract** depends on the spot returns.
                    For a vanilla option it relates to the **return at maturity** alone. However,
                    for other contracts, knockouts and calls make the cashflow depend on prices
                    prior to maturity.
                """
                ),
            ],
            # style={"display": "inline-block", "width": "95%"},
            style={
                "position": "fixed",
                "top": 10,
                "left": "25%",  # Sidebar takes the left 25% of the screen.
                "width": "48%",
            },
        ),
        html.Div(
            [
                daq.Knob(
                    id="future-vol",
                    # size=75,
                    label="Volatility",
                    labelPosition="bottom",
                    value=0.3,
                    min=0.0,
                    max=0.8,
                ),
                dcc.Markdown(
                    """
                    A **pricing model** produces the projection of future
                    asset returns. Tweak the **volatility** to see how it affects the
                    projections.
                """
                ),
            ],
            style={
                "position": "fixed",
                "top": 20,
                "left": "75%",  # Sidebar takes the left 25% of the screen.
                "width": "20%",
            },
        ),
    ],
)


@callback(
    Output("future-returns", "figure"),
    Input("ctr-params", "data"),
    Input("future-vol", "value"),
)
def update_future_returns(contract_params, vol):
    """Generate cashflows from model and plot returns."""

    cfsums, spot = model_cashflows(contract_params, vol=vol)

    fig = plot_cf_vs_spot(cfsums, spot, params=contract_params)

    return fig
