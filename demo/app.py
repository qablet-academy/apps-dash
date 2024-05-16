import sys
from os.path import dirname

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, State
from src.timetables import CONTRACT_TYPES

sys.path.append(dirname(__file__))

app = dash.Dash(
    __name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR]
)
server = app.server


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
}

# Nav to select the page
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

# Contract editor
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
        html.Br(),
        dbc.Button("About this Contract", id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas(
            html.P("Description about this instrument (TBD)."),
            id="offcanvas",
            title="About this Contract",
            is_open=False,
        ),
    ],
    id="contractr-params",
)

# Sidebar has the Pages Nav (Top), and Contract Editor (Below).
sidebar = html.Div(
    [
        html.Img(src="assets/logo.png", width="25%"),
        html.P("What would you explore?", className="lead"),
        report_nav,
        html.Br(),
        html.H2("Contract"),
        html.Hr(),
        contract_editor,
    ],
    style=SIDEBAR_STYLE,
)

# The app has sidebar on left, the pages are on the right.
# The pages area is populated by one of the scripts in the /pages folder.
app.layout = dbc.Container(
    [
        sidebar,
        dash.page_container,
    ],
)


# Collect parameters from the contract editor and store them in a dict.
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


# Toggle the offcanvas to show the contract description.
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
