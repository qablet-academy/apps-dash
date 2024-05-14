import dash
import numpy as np
import plotly.express as px
from dash import Input, Output, callback, dcc, html
from src.acn import backtest_acn
import bisect


dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="backtest-scatter",
                    #hoverData={"points": [{"customdata": "Japan"}]},
                )
            ],
            style={
                "width": "49%",
                "display": "inline-block",
                "padding": "0 20",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="backtest-one-trade"),
            ],
            style={"display": "inline-block", "width": "49%"},
        ),
        dcc.Store(id="backtest_stats", storage_type="session"),
    ],
    style={
        "position": "fixed",
        "top": 10,
        "left": "25%",
        "width": "75%",
    },
)


@callback(
    Output("backtest-scatter", "figure"),
    Output("backtest_stats", "data"),
    Input("contract_inputs", "data"),
)
def update_graph(data):

    df, stats = backtest_acn()

    fig = px.scatter(
        x=df["date"],
        y=df["irr"],
        # hover_name=df["date"].strftime("%Y-%m-%d"),
        labels={'x': 'Trade Date', 'y':'Rate of Return'}
    )

    # TODO save range of index in customdata

    # fig.update_traces(
    #     customdata=df[df["Indicator Name"] == yaxis_column_name][
    #         "Country Name"
    #     ]
    # )

    fig.update_layout(
        margin={"l": 40, "b": 40, "t": 10, "r": 0}, hovermode="closest"
    )


    return fig, stats


def create_time_series(data, title):
    # fig = px.scatter(dff, x="Year", y="Value")

    # fig.update_traces(mode="lines+markers")

    # fig.update_xaxes(showgrid=False)

    # fig.add_annotation(
    #     x=0,
    #     y=0.85,
    #     xanchor="left",
    #     yanchor="bottom",
    #     xref="paper",
    #     yref="paper",
    #     showarrow=False,
    #     align="left",
    #     text=title,
    # )
    x = np.array(data[0]).astype("datetime64[ms]")
    y = np.array(data[1])

    fig = px.bar(
        x=x,
        y=y,
        # hover_name=df["date"],
    )
    fig.update_layout(height=225, margin={"l": 20, "b": 30, "r": 10, "t": 10})

    return fig


@callback(
    Output("backtest-one-trade", "figure"),
    Input("backtest-scatter", "hoverData"),
    Input("contract_inputs", "data"),
    Input("backtest_stats", "data"),
)
def update_backtest_cashflow(hoverData, data, stats):
    xaxis_column_name, _ = data

    if hoverData is None:
        prc_ts = stats['ts'][0]
        cf = stats['stats'][0]
    else:
        prc_ts = hoverData["points"][0]["date"]
        idx = bisect.bisect_left(stats['ts'], prc_ts)
        cf = stats['stats'][idx]

    title = "<b>{}</b><br>{}".format(prc_ts, prc_ts)
    return create_time_series(cf, title)

