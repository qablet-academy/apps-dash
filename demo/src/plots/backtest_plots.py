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

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.6, 0.4],
        shared_xaxes=True,
        vertical_spacing=0.0,
    )

    # TODO: Net cashflows on same date. either here or in get_cf.
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            width=MS_IN_DAY * 2,
            marker_color=color,
        ),
        row=1,
        col=1,
    )

    # Annotate the trade and the last cashflow date
    datefmt = "%Y-%m-%d"
    prc_dt = datetime.fromtimestamp(prc_ts // 1000000000, pytz.utc)
    end_dt = datetime.fromtimestamp(end_ts, pytz.utc)
    fig.add_annotation(
        x=prc_dt,
        text=f"Trade Date<br><b>{prc_dt.strftime(datefmt)}</b>",
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
            line=dict(color="dimgrey", width=1),
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        height=250,
        margin={"l": 40, "b": 40, "t": 10, "r": 0},
        template="plotly_dark",
        showlegend=False,
    )
    fig.update_yaxes(
        title_text="Cashflow",
        side="left",
        color="aquamarine",
        row=1,
        col=1,
    )
    start_spot = tickerdf[ticker][0]

    fig.update_yaxes(
        title_text=ticker,
        side="right",
        color="dimgrey",
        showticklabels=False,
        tickvals=[start_spot],
        row=2,
        col=1,
    )
    fig.add_annotation(
        x=prc_dt,
        y=start_spot,
        text=f"{start_spot}",
        showarrow=False,
        xanchor="right",
        font=dict(color="dimgrey"),
        row=2,
        col=1,
    )
    end_spot = tickerdf[ticker][-1]
    fig.add_annotation(
        x=end_dt,
        y=end_spot,
        text=f"{end_spot}",
        showarrow=False,
        xanchor="left",
        font=dict(color="dimgrey"),
        row=2,
        col=1,
    )
    return fig


def plot_irr(x, y, annualized=True, ticker="SPX"):
    """Plot a IRR scatter plot on the left, and histogram on the right."""

    if annualized:
        ylabel = "Annualized Return"
    else:
        ylabel = "Gain/Loss %"
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
