from datetime import datetime
import pandas as pd
from qablet.black_scholes.mc import LVMCModel

from src.model import CFModelPyCSV, DataModel, get_cf
from src.timetables import create_timetable
from src.utils import ROOTDIR, base_dataset, compute_return, update_dataset

def run_backtest(contract_params: dict, annualized: bool = True):
    """
    Run backtest for a given contract. The backtest is run on a historical dataset.
    Return the a dataframe with IRR for each trade date,
    and a dict with the cashflow for each trade date.
    """
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

    # Fetch adjusted month-end dates using the monthend_dates method
    monthend_dates = csvdata.monthend_dates(contract_params["ticker"])

    m_exp = 12
    num_trials = len(monthend_dates) - m_exp
    for i in range(num_trials):
        pricing_ts = monthend_dates[i]  # datetime object of trading date

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
        end_dt = timetable["events"]["time"][-1].as_py().timestamp()

        all_ts.append((pricing_ts.timestamp(), end_dt))

    df = pd.DataFrame(
        results,
        columns=["date", "irr"],
    )
    return df, {
        "stats": all_stats,
        "ts": all_ts,
        "ticker": contract_params["ticker"],
    }
