"""
Test the backtest plot without the app.
"""
import sys
from os.path import dirname


if __name__ == "__main__":
    sys.path.append(dirname(dirname(__file__)))

    from plots.backtest_plots import plot_irr, plot_irr_histogram
    from runbacktest import run_backtest

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "AutoCallable",
    }
    df, _ = run_backtest(contract_params)

    # fig = plot_irr(df["date"], df["irr"])
    fig = plot_irr_histogram(df["irr"])

    fig.write_html("scratch/first_figure.html", auto_open=True)
