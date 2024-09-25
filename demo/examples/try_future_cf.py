"""
Script to test the plots in the future page without launching the app.
"""

from demo.src.future_cf import model_cashflows
from demo.src.plots.future_plots import plot_cf_vs_spot


if __name__ == "__main__":
    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    vol = 0.2
    cfsums, spot = model_cashflows(contract_params, vol=vol)
    fig = plot_cf_vs_spot(cfsums, spot, vol, params=contract_params)

    fig.write_html("scratch/first_figure.html", auto_open=True)
