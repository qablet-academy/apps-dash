import sys
from os.path import dirname

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

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
    # "background-color": "#95B9C7",
    # "background-color": "#95B9C7",
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
                    ["SPX", "AAPL", "GOOGL"],
                    "SPX",
                    id="contract-ticker",
                ),
                html.Br(),
                dcc.Dropdown(
                    ["AutoCallable", "Barrier", "Vanilla"],
                    "AutoCallable",
                    id="contract-type",
                ),
                dcc.Store(id="contract_inputs", storage_type="session"),
                   
            ],
            # className="dbc",
            id="contract-params",
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
    Input("contract-ticker", "value"),
    Input("contract-type", "value"),
)
def update_graph(ticker, contract_type):
    contract_params = {
        "ticker": ticker,
        "contract-type": contract_type,
    }
    return contract_params


if __name__ == "__main__":
    app.run_server(debug=True)
