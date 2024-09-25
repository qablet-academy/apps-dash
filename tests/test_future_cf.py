"""
Script to test the plots in the future page without launching the app.
"""

import pytest
from demo.src.future_cf import model_cashflows


def test_future_cf():
    contract_params = {
        "ticker": "SPX",
        "ctr-type": "Reverse Convertible",
    }
    vol = 0.2
    (contract_cfs, spot_cfs), spot = model_cashflows(contract_params, vol=vol)

    assert spot == pytest.approx(3230.78, rel=1e-6)
    assert len(contract_cfs) == 100
    assert len(spot_cfs) == 100


if __name__ == "__main__":
    pytest.main()
