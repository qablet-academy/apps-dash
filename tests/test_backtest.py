"""
Script to test the plots in the backtest page without launching the app.
"""

import pytest
from demo.src.backtest import run_backtest


def test_backtest():
    contract_params = {
        "ticker": "EUR",
        "ctr-type": "Reverse Convertible",
    }
    df, stats = run_backtest(contract_params, annualized=False)
    print(df)
    print(stats)

    # Assert the mean
    assert df["irr"].mean() == pytest.approx(0.0832365500, rel=1e-6)


if __name__ == "__main__":
    pytest.main()
