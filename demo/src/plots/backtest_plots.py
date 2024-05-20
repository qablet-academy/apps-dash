"""
Methods to crete figures for the backtest page.
"""
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import pytz
from plotly.subplots import make_subplots
from src.model import MS_IN_DAY, DataModel
from src.utils import ROOTDIR


def plot_cashflow(ts_data, cf, ticker):
    prc_ts, end_ts = ts_data
    trade_price = cf[2]
    x = np.insert(cf[0], 0, prc_ts // 1000000)
    x = np.array(x).astype("datetime64[ms]")
    y = np.array(cf[1])
    y = np.insert(y, 0, -trade_price)

    color = np.where(y < 0, "coral", "aquamarine")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # TODO: Net cashflows on same date. either here or in get_cf.
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            width=MS_IN_DAY * 2,
            marker_color=color,
        ),
        secondary_y=False,
    )

    # Annotate the trade and the last cashflow date
    datefmt = "%Y-%m-%d"
    prc_dt = datetime.fromtimestamp(prc_ts // 1000000000, pytz.utc)
    end_dt = datetime.fromtimestamp(end_ts, pytz.utc)
    fig.add_annotation(
        x=prc_dt,
        text=f"Trade Date<br><b>{prc_dt.strftime(datefmt)}</b>",
        # f"<br>Trade Price<br><b>{trade_price:.2f}</b>",
    )
    fig.add_annotation(
        x=end_dt,
        text=f"Maturity<br><b>{end_dt.strftime(datefmt)}</b>",
    )

    # A plot for the ticker on the bottom sharing x axis with the scatter plot
    filename = ROOTDIR + "/data/spots.csv"
    csvdata = DataModel(filename)
    tickerdf = csvdata.get_curve(prc_dt, end_dt)
    fig.add_trace(
        go.Scatter(
            x=tickerdf["date"],
            y=tickerdf[ticker],
            line=dict(color="grey", width=1),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        height=225,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        template="plotly_dark",
        showlegend=False,
    )
    fig.update_yaxes(
        title_text="Cashflow",
        side="right",
        color="aquamarine",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text=ticker, side="left", color="grey", secondary_y=True
    )
    return fig


def plot_irr(x, y, annualized=True, ticker="SPX"):
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

    # IRR Scatter plot at left
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

    # Update IRR plot to have percentage y axis
    fig.update_yaxes(
        title_text=ylabel,
        side="left",
        row=1,
        col=1,
        color="aquamarine",
        tickformat=",.1%",
    )

    fig.update_layout(
        height=300,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        hovermode="closest",
        template="plotly_dark",
        showlegend=False,
    )
    return fig
