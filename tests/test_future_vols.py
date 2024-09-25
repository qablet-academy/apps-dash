"""
Script to test the vol risk in the future page without launching the app.
"""

import pytest
from demo.src.future_cf import vol_risk


def test_vols():
    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    vols, prices = vol_risk(contract_params)

    move = prices[-1] - prices[0]

    assert move == pytest.approx(-5.1480718, rel=1e-6)


if __name__ == "__main__":
    pytest.main()
