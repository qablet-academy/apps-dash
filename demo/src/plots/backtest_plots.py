from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import pytz
from src.model import MS_IN_DAY


def plot_cashflow(x, y, prc_ts):
    # TODO: use red/green color for cashflows
    # TODO: consider rounded.
    # TODO: Net cashflows on same date. either here or in get_cf.
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


def plot_irr(x, y):
    fig = px.scatter(
        x=x,
        y=y,
        labels={"x": "Trade Date", "y": "Rate of Return"},
        template="plotly_dark",
    )

    fig.update_traces(
        customdata=np.arange(len(x)), marker=dict(size=12, opacity=0.7)
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
    )

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        yaxis={"tickformat": ",.1%"},
    )
    return fig
