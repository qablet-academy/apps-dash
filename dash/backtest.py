from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# Notes: https://github.com/charlotteamy/Dash-visualisation/blob/main/Dash_blog.py
# https://towardsdatascience.com/3-easy-ways-to-make-your-dash-application-look-better-3e4cfefaf772

# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
load_figure_template("QUARTZ")  # or QUARTZ

app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])  # or SLATE

df = pd.read_csv("https://plotly.github.io/datasets/country_indicators.csv")

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


sidebar = html.Div(
    [
        html.H2("Filters"),
        html.Hr(),
        html.P("A simple sidebar layout with filters", className="lead"),
        dbc.Nav(
            [
                dcc.Dropdown(
                    df["Indicator Name"].unique(),
                    "Fertility rate, total (births per woman)",
                    id="crossfilter-xaxis-column",
                ),
                html.Br(),
                dcc.Dropdown(
                    df["Indicator Name"].unique(),
                    "Life expectancy at birth, total (years)",
                    id="crossfilter-yaxis-column",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

backtest = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="crossfilter-indicator-scatter",
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
                dcc.Graph(id="x-time-series"),
                dcc.Graph(id="y-time-series"),
            ],
            style={"display": "inline-block", "width": "49%"},
        ),
        html.Div(
            dcc.Slider(
                df["Year"].min(),
                df["Year"].max(),
                step=None,
                id="crossfilter-year--slider",
                value=df["Year"].max(),
                marks={str(year): str(year) for year in df["Year"].unique()},
            ),
            style={"width": "49%", "padding": "0px 20px 20px 20px"},
        ),
    ],
    style={
        "position": "fixed",
        "top": 10,
        "left": "25%",
        "width": "75%",
    },
)

app.layout = html.Div([dbc.Row([dbc.Col(sidebar), dbc.Col(backtest)])])


@callback(
    Output("crossfilter-indicator-scatter", "figure"),
    Input("crossfilter-xaxis-column", "value"),
    Input("crossfilter-yaxis-column", "value"),
    Input("crossfilter-year--slider", "value"),
)
def update_graph(xaxis_column_name, yaxis_column_name, year_value):
    dff = df[df["Year"] == year_value]

    fig = px.scatter(
        x=dff[dff["Indicator Name"] == xaxis_column_name]["Value"],
        y=dff[dff["Indicator Name"] == yaxis_column_name]["Value"],
        hover_name=dff[dff["Indicator Name"] == yaxis_column_name][
            "Country Name"
        ],
    )

    fig.update_traces(
        customdata=dff[dff["Indicator Name"] == yaxis_column_name][
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
    Output("x-time-series", "figure"),
    Input("crossfilter-indicator-scatter", "hoverData"),
    Input("crossfilter-xaxis-column", "value"),
)
def update_x_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData["points"][0]["customdata"]
    dff = df[df["Country Name"] == country_name]
    dff = dff[dff["Indicator Name"] == xaxis_column_name]
    title = "<b>{}</b><br>{}".format(country_name, xaxis_column_name)
    return create_time_series(dff, title)


@callback(
    Output("y-time-series", "figure"),
    Input("crossfilter-indicator-scatter", "hoverData"),
    Input("crossfilter-yaxis-column", "value"),
)
def update_y_timeseries(hoverData, yaxis_column_name):
    dff = df[df["Country Name"] == hoverData["points"][0]["customdata"]]
    dff = dff[dff["Indicator Name"] == yaxis_column_name]
    return create_time_series(dff, yaxis_column_name)


if __name__ == "__main__":
    app.run(debug=True)
