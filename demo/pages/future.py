"""
This page shows future returns projected by model.
"""

import dash
from dash import Input, Output, callback, dcc, html
from demo.src.future_cf import model_cashflows, vol_risk
from demo.src.plots.backtest_plots import blank_figure
from demo.src.plots.future_plots import plot_cf_vs_spot, plot_price_vol

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                # Contract vs Spots Graph.
                html.Div(id="markdown-output", children=[]),
                dcc.Markdown(
                    """
                    To change the volatility, **Click on the orange points** in the plot on the right,
                    and note how the distribution in this plot changes. 
                """
                ),
                dcc.Graph(
                    id="future-returns",
                    figure=blank_figure(),
                ),
                html.Br(),
                dcc.Markdown(
                    """
                    The cashflow of the contract depends on the spot returns.
                    For a vanilla option this plot shows a clear one-to-one relationship because the cashflow depends
                    only on the return at maturity. However, for other contracts, there are knockouts
                    and calls prior to maturity and the plot is not one-to-one.
                """
                ),
            ],
            style={
                "position": "fixed",
                "top": 10,
                "left": "25%",  # Sidebar takes the left 25% of the screen.
                "width": "48%",
            },
        ),
        html.Div(
            [
                html.P("Model Price vs Volatility"),
                dcc.Graph(
                    id="future-vol-plot",
                    figure=blank_figure(),
                ),
            ],
            style={
                "position": "fixed",
                "top": "20%",
                "left": "75%",  # Sidebar takes the left 25% of the screen.
                "width": "20%",
            },
        ),
    ],
)


@callback(
    Output("future-returns", "figure"),
    Output("markdown-output", "children"),
    Input("ctr-params", "data"),
    Input("future-vol-plot", "clickData"),
)
def update_future_returns(contract_params, click_data):
    """Generate cashflows from model and plot returns."""

    if click_data is None:
        vol = 0.2
    else:
        vol = click_data["points"][0]["x"]

    cfsums, spot = model_cashflows(contract_params, vol=vol)
    fig = plot_cf_vs_spot(cfsums, spot, vol, params=contract_params)

    markdown_content = f"Contract Cashflows vs Spot Returns at **{vol * 100:.1f}% volatility.**"
    return fig, dcc.Markdown(markdown_content)


@callback(
    Output("future-vol-plot", "figure"),
    Input("ctr-params", "data"),
)
def update_future_vol(contract_params):
    """Plot Price vs Volatility."""

    vols, prices = vol_risk(contract_params)
    fig = plot_price_vol(vols, prices)

    return fig
