"""
Script to test the plots in the future page without launching the app.
"""
import sys
from os.path import dirname

if __name__ == "__main__":
    sys.path.append(dirname(dirname(dirname(__file__))))
    from src.future_cf import model_cashflows
    from src.plots.future_plots import plot_cf_vs_spot

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    x, y = model_cashflows(contract_params)

    fig = plot_cf_vs_spot(x, y, ticker=contract_params["ticker"])

    fig.write_html("scratch/first_figure.html", auto_open=True)
