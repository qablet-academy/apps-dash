"""
Run backtest for a given contract. The backtest is run on a historical dataset.
Return the a dataframe with IRR for each trade date,
and a dict with the cashflow for each trade date.
"""
import os
from datetime import datetime

import numpy as np
import pandas as pd
from qablet.black_scholes.mc import LVMCModel

from src.model import CFModelPyCSV, DataModel, get_cf
from src.timetables import create_timetable
from src.utils import compute_return

ROOTDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


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


def update_dataset(pricing_ts, dataset, spot, params):
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

    # update dataset
    dataset["PRICING_TS"] = int(pricing_ts.value / 1e6)  # ns to ms timestamp
    dataset["ASSETS"] = assets_data
    dataset["LV"] = {
        "ASSET": ticker,
        "VOL": 0.3,  # hardcoded vol (use vix perhaps?)
    }
    return spot


def run_backtest(contract_params: dict, annualized: bool = True):
    # Create the models
    filename = ROOTDIR + "/data/spots.csv"
    csvdata = DataModel(filename)
    model = LVMCModel()
    bk_model = CFModelPyCSV(filename=filename, base="USD")

    # Use current divs and risk free for historical pricings
    dataset = base_dataset()

    results = []
    all_stats = []
    all_ts = []
    monthend_dates = pd.bdate_range(
        datetime(2019, 12, 31), datetime(2024, 4, 30), freq="1BME"
    )
    m_exp = 12
    num_trials = len(monthend_dates) - m_exp
    for i in range(num_trials):
        pricing_ts = monthend_dates[i]  # timestamp of trading date

        spot = csvdata.get_value(contract_params["ticker"], pricing_ts)

        update_dataset(pricing_ts, dataset, spot, contract_params)

        timetable = create_timetable(
            pricing_ts, monthend_dates, spot, i, contract_params
        ).timetable()

        # Compute prices of 0 and unit coupon
        px, _ = model.price(timetable, dataset)

        # Compute backtest stats and irr
        stats = bk_model.cashflow(timetable)
        yrs_vec, cf_vec, ts_vec = get_cf(pricing_ts, timetable, stats)
        irr = compute_return(cf_vec, yrs_vec, px, annualized=annualized)

        results.append((pricing_ts, irr))
        all_stats.append(
            (ts_vec.astype("uint64").tolist(), cf_vec.tolist(), px)
        )
        all_ts.append(pricing_ts.value)

    df = pd.DataFrame(
        results,
        columns=["date", "irr"],
    )
    return df, {"stats": all_stats, "ts": all_ts}
