"""
Methods to crete figures for the future page.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_cf_vs_spot(cfsums, spot, vol, params):
    if params["ctr-type"] in [
        "Knockout Option",
        "Vanilla Option",
    ]:
        y = cfsums[0] / spot
        title = "Contract Cashflow (% of Spot)"
    else:
        y = cfsums[0] / 100
        title = "Contract Cashflow (% of Notional)"

    x = cfsums[1] * 1.0305 / spot - 1
    ticker = params["ticker"]

    color = np.where(y < 0, "coral", "aquamarine")

    fig = make_subplots(
        rows=2,
        cols=2,
        column_widths=[0.9, 0.1],
        row_heights=[0.1, 0.9],
        shared_yaxes=True,
        shared_xaxes=True,
        horizontal_spacing=0.0,
        vertical_spacing=0.0,
    )

    # Main plot (bottom left): Scatter plot of contract cashflow vs ticker returns
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color=color, size=12, opacity=0.4),
        ),
        row=2,
        col=1,
    )

    # Vertical Histogram of contract cashflows, right of main plot
    fig.add_trace(
        go.Histogram(
            y=y,
            nbinsy=20,
            marker_color="aquamarine",
        ),
        row=2,
        col=2,
    )
    # Add a horizontal line at 0
    fig.add_hline(y=0.0)

    # Histogram of spot returns, above the main plot
    fig.add_trace(
        go.Histogram(
            x=x,
            nbinsy=20,
            marker_color="dimgrey",
        ),
        row=1,
        col=1,
    )
    # Add a vertical line at 0
    fig.add_vline(x=0.0)

    # Update ticker returns to have percentage y axis
    fig.update_xaxes(
        title_text=f"{ticker} return at maturity",
        row=2,
        col=1,
        color="grey",
        tickformat=",.1%",
        range=[-0.60, 0.60],
    )
    fig.update_yaxes(
        title_text=title,
        row=2,
        col=1,
        color="aquamarine",
        tickformat=",.1%",
        range=[0.0, 1.25],
    )

    fig.update_xaxes(visible=False, row=2, col=2)
    fig.update_yaxes(visible=False, row=1, col=1)

    fig.update_layout(
        height=500,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        template="plotly_dark",
        showlegend=False,
    )
    return fig


def plot_price_vol(vols, prices):
    """Plot Price vs Vol."""

    fig = go.Figure(
        go.Scatter(
            x=vols,
            y=prices,
            marker=dict(color="coral", size=20, opacity=0.7),
        )
    )
    fig.update_xaxes(tickformat=",.0%", title_text="Model Volatility")
    fig.update_yaxes(tickformat=",.2f")
    fig.update_layout(
        height=350,
        width=350,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        template="plotly_dark",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
