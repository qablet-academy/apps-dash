"""
Script to test the vol risk in the future page without launching the app.
"""

import sys
from os.path import dirname

if __name__ == "__main__":
    sys.path.append(dirname(dirname(dirname(__file__))))
    from src.future_cf import vol_risk
    from src.plots.future_plots import plot_price_vol

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    vols, prices = vol_risk(contract_params)

    fig = plot_price_vol(vols, prices)

    fig.write_html("scratch/first_figure.html", auto_open=True)
