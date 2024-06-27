"""
This module contains utility functions for the demo.
"""
import os

import numpy as np
from scipy.optimize import minimize_scalar

ROOTDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# IRR
def loss_irr(
    ytm: float, payments: np.ndarray, times: np.ndarray, price: float
) -> float:
    df = np.exp(-ytm * times)
    pv = np.dot(payments, df)
    err = pv - price
    return 0.5 * err * err


def compute_return(
    payments: np.ndarray,
    times: np.ndarray,
    price: float,
    annualized: bool = True,
) -> float:
    if not annualized:
        return payments.sum() / price - 1
    try:
        res = minimize_scalar(fun=loss_irr, args=(payments, times, price))
        if res.success:
            return res.x
        else:
            raise ValueError(f"Optimization failed: {res.message}")
    except Exception:
        return None


def base_dataset():
    """Create the base dataset. Asset data and model parameters will be
    added later, specific to each pricing date."""
    return {
        "MC": {
            "PATHS": 10_000,
            "TIMESTEP": 100,  # BSM doesn't need small timesteps
            "SEED": 1,
        },
        "BASE": "USD",
    }


def dataset_assets(spot, params):
    """update assets data with equity forwards (need only one)."""

    ticker = params["ticker"]

    # Rates and divs data
    times = np.array([0.0, 2.0])
    rates = np.array([0.03, 0.03])
    discount_data = ("ZERO_RATES", np.column_stack((times, rates)))
    assets_data = {"USD": discount_data}
    divs = 0.02  # get_divs(basket)

    fwds = spot * np.exp((rates - divs) * times)
    assets_data[ticker] = ("FORWARDS", np.column_stack((times, fwds)))

    return assets_data
