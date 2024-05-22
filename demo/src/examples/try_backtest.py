"""
Script to test the plots in the backtest page without launching the app.
"""
import sys
from os.path import dirname


def main():
    sys.path.append(dirname(dirname(dirname(__file__))))

    plot_type = "Cashflow"  # IRR or Cashflow

    from src.backtest import run_backtest
    from src.plots.backtest_plots import (
        plot_cashflow,
        plot_irr,
    )

    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    df, stats = run_backtest(contract_params, annualized=False)

    if plot_type == "IRR":
        fig = plot_irr(df["date"], df["irr"], ticker=contract_params["ticker"])
    else:
        idx = 30  # Select a trade
        fig = plot_cashflow(
            stats["ts"][idx], stats["stats"][idx], stats["ticker"]
        )

    fig.write_html("scratch/first_figure.html", auto_open=True)


if __name__ == "__main__":
    main()
