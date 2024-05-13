import dash
from dash import Dash, html, dcc, Input, Output, callback, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


df = pd.read_csv("https://plotly.github.io/datasets/country_indicators.csv")

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="backtest-scatter",
                    hoverData={"points": [{"customdata": "Japan"}]},
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
                dcc.Graph(id="backtest-other-trade"),
            ],
            style={"display": "inline-block", "width": "49%"},
        ),
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
    Input("contract_inputs", "data"),
)
def update_graph(data):
    xaxis_column_name, yaxis_column_name = data

    fig = px.scatter(
        x=df[df["Indicator Name"] == xaxis_column_name]["Value"],
        y=df[df["Indicator Name"] == yaxis_column_name]["Value"],
        hover_name=df[df["Indicator Name"] == yaxis_column_name][
            "Country Name"
        ],
    )

    fig.update_traces(
        customdata=df[df["Indicator Name"] == yaxis_column_name][
            "Country Name"
        ]
    )

    fig.update_layout(
        margin={"l": 40, "b": 40, "t": 10, "r": 0}, hovermode="closest"
    )

    return fig


def create_time_series(dff, title):
    fig = px.scatter(dff, x="Year", y="Value")

    fig.update_traces(mode="lines+markers")

    fig.update_xaxes(showgrid=False)

    fig.add_annotation(
        x=0,
        y=0.85,
        xanchor="left",
        yanchor="bottom",
        xref="paper",
        yref="paper",
        showarrow=False,
        align="left",
        text=title,
    )

    fig.update_layout(height=225, margin={"l": 20, "b": 30, "r": 10, "t": 10})

    return fig


@callback(
    Output("backtest-one-trade", "figure"),
    Input("backtest-scatter", "hoverData"),
    Input("contract_inputs", "data"),
)
def update_x_timeseries(hoverData, data):
    xaxis_column_name, _ = data

    country_name = hoverData["points"][0]["customdata"]
    dff = df[df["Country Name"] == country_name]
    dff = dff[dff["Indicator Name"] == xaxis_column_name]
    title = "<b>{}</b><br>{}".format(country_name, xaxis_column_name)
    return create_time_series(dff, title)


@callback(
    Output("backtest-other-trade", "figure"),
    Input("backtest-scatter", "hoverData"),
    Input("contract_inputs", "data"),
)
def update_y_timeseries(hoverData, data):
    _, yaxis_column_name = data

    dff = df[df["Country Name"] == hoverData["points"][0]["customdata"]]
    dff = dff[dff["Indicator Name"] == yaxis_column_name]
    return create_time_series(dff, yaxis_column_name)
