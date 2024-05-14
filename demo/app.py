import sys
from os.path import dirname

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, callback, dcc, html

sys.path.append(dirname(__file__))

app = dash.Dash(
    __name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE]
)
server = app.server


df2 = pd.read_csv("https://plotly.github.io/datasets/country_indicators.csv")

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
        html.P("Choose a report type below", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink(
                    html.Div(page["name"], className="ms-2"),
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),
        html.H2("Contract"),
        html.Hr(),
        html.P("Choose properties for contract below.", className="lead"),
        html.Div(
            [
                dcc.Dropdown(
                    df2["Indicator Name"].unique(),
                    "Fertility rate, total (births per woman)",
                    id="crossfilter-xaxis-column",
                ),
                html.Br(),
                dcc.Dropdown(
                    df2["Indicator Name"].unique(),
                    "Life expectancy at birth, total (years)",
                    id="crossfilter-yaxis-column",
                ),
                dcc.Store(id="contract_inputs", storage_type="session"),
            ],
            id="crossfilter-everything",
        ),
    ],
    style=SIDEBAR_STYLE,
)


app.layout = dbc.Container(
    [
        sidebar,
        dash.page_container,
    ],
)


@callback(
    Output("contract_inputs", "data"),
    Input("crossfilter-xaxis-column", "value"),
    Input("crossfilter-yaxis-column", "value"),
)
def update_graph(xaxis_column_name, yaxis_column_name):
    data = (xaxis_column_name, yaxis_column_name)
    return data


if __name__ == "__main__":
    app.run_server(debug=True)
