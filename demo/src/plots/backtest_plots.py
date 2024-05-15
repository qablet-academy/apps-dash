from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import pytz
from src.model import MS_IN_DAY
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_cashflow(prc_ts, cf):
    x = np.insert(cf[0], 0, prc_ts // 1000000)
    x = np.array(x).astype("datetime64[ms]")
    y = np.array(cf[1])
    y = np.insert(y, 0, -cf[2])

    color = np.where(y < 0, "coral", "aquamarine")

    # TODO: Net cashflows on same date. either here or in get_cf.
    fig = px.bar(
        x=x,
        y=y,
        labels={"x": "Trade Date", "y": "Cashflows"},
        template="plotly_dark",
    )

    fig.update_layout(height=225, margin={"l": 20, "b": 30, "r": 10, "t": 10})
    fig.update_traces(width=MS_IN_DAY * 2, marker_color=color)

    # Annotate the trade and the last cashflow date
    datefmt = "%Y-%m-%d"
    prc_dt = datetime.fromtimestamp(prc_ts // 1000000000, pytz.utc)
    fig.add_annotation(
        x=prc_dt,
        text=f"Paid on Trade Date<br><b>{prc_dt.strftime(datefmt)}</b>",
    )
    end_dt = pd.to_datetime(x[-1])
    fig.add_annotation(
        x=end_dt,
        text=f"Last Cashflow Date<br><b>{end_dt.strftime(datefmt)}</b>",
    )
    return fig


def plot_irr(x, y, annualized=True):
    """Plot a IRR scatter plot on the left, and histogram on the right."""

    if annualized:
        ylabel = "Annualized Return by Trade Date"
    else:
        ylabel = "Gain/Loss by Trade Date"
    color = np.where(y < 0, "coral", "aquamarine")

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.8, 0.2],
        shared_yaxes=True,
        horizontal_spacing=0.0,
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            customdata=np.arange(len(x)),
            marker=dict(color=color, size=12, opacity=0.7),
        ),
        row=1,
        col=1,
    )

    # Vertical Histogram, sharing y axis with the scatter plot
    fig.add_trace(
        go.Histogram(
            y=y,
            nbinsy=20,
            marker_color="aquamarine",
        ),
        row=1,
        col=2,
    )
    # Add a horizontal line at 0
    fig.add_hline(y=0.0)

    fig.update_yaxes(title_text="Distribution", side="right", row=1, col=2)

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        yaxis={"tickformat": ",.1%"},
        template="plotly_dark",
        yaxis_title=ylabel,
        showlegend=False,
    )
    return fig
