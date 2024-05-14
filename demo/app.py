import sys
from os.path import dirname

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html
from src.timetables import CONTRACT_TYPES

sys.path.append(dirname(__file__))

# Consider these options
# Dark: slate, solar, cyborg, or darkly (with plots using plotly_dark)
# Light: quartz, with plots using plotyl_white or seaborn
app = dash.Dash(
    __name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR]
)
server = app.server

# Other Notes on dbc items:
# Use OffCanvas for extra information.


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
}

contract_editor = html.Div(
    [
        dcc.Dropdown(
            ["SPX", "AAPL", "GOOGL"],
            "SPX",
            id="ctr-ticker",
        ),
        html.Br(),
        dcc.Dropdown(
            CONTRACT_TYPES,
            CONTRACT_TYPES[0],
            id="ctr-type",
        ),
        dcc.Store(id="ctr-params", storage_type="session"),
    ],
    id="contractr-params",
)

report_nav = dbc.Nav(
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
)

sidebar = html.Div(
    [
        html.P("Choose a report type below", className="lead"),
        report_nav,
        html.Br(),
        html.H2("Contract"),
        html.Hr(),
        html.P("Select contract below.", className="lead"),
        contract_editor,
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
    Output("ctr-params", "data"),
    Input("ctr-ticker", "value"),
    Input("ctr-type", "value"),
)
def update_graph(ticker, contract_type):
    contract_params = {
        "ticker": ticker,
        "ctr-type": contract_type,
    }
    return contract_params


if __name__ == "__main__":
    app.run_server(debug=True)
