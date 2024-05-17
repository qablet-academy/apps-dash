"""
Script to test the backtest page without launching the app.
"""
import sys
from os.path import dirname

if __name__ == "__main__":
    sys.path.append(dirname(dirname(dirname(__file__))))

    plot_type = "IRR"  # IRR or Cashflow

    from src.backtest import run_backtest
    from src.plots.backtest_plots import (
        plot_cashflow,
        plot_irr,
    )

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "VanillaOption",
    }
    df, stats = run_backtest(contract_params, annualized=False)

    if plot_type == "IRR":
        fig = plot_irr(df["date"], df["irr"], ticker=contract_params["ticker"])
    else:
        idx = 3  # Select a trade
        fig = plot_cashflow(stats["ts"][idx], stats["stats"][idx])

    fig.write_html("scratch/first_figure.html", auto_open=True)
