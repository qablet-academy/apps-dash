from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import pytz
from src.model import MS_IN_DAY


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
    if annualized:
        ylabel = "Annualized Rate of Return"
    else:
        ylabel = "Gain/Loss"

    color = np.where(y < 0, "coral", "aquamarine")

    fig = px.scatter(
        x=x,
        y=y,
        labels={"x": "Trade Date", "y": ylabel},
        template="plotly_dark",
    )
    fig.add_hline(
        y=0.0,
    )

    fig.update_traces(
        customdata=np.arange(len(x)),
        marker=dict(size=12, opacity=0.7),
        marker_color=color,
    )

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        yaxis={"tickformat": ",.1%"},
    )
    return fig


def plot_irr_histogram(df):
    fig = px.histogram(
        y=df,
        nbins=20,
        template="plotly_dark",
        color_discrete_sequence=["aquamarine"],
    )

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        yaxis={"tickformat": ",.1%"},
    )
    return fig
