"""
Project Future Cashflows for a given contract.
"""
from datetime import datetime

import pandas as pd
from qablet.base.flags import Stats
from qablet.black_scholes.mc import LVMCModel

from src.model import DataModel
from src.timetables import (
    create_forward_timetable,
    create_timetable,
    extend_timetable,
)
from src.utils import ROOTDIR, base_dataset, update_dataset


def model_cashflows(contract_params: dict, trial=0, vol=0.3):
    # Create the models
    filename = ROOTDIR + "/data/spots.csv"
    csvdata = DataModel(filename)
    model = LVMCModel()

    # prepare dataset, and turn on cashflow flag
    dataset = base_dataset()
    dataset["MC"]["FLAGS"] = Stats.CASHFLOW
    dataset["MC"]["PATHS"] = 100  # Too many dots otherwise

    monthend_dates = pd.bdate_range(
        datetime(2019, 12, 31), datetime(2024, 4, 30), freq="1BME"
    )
    pricing_ts = monthend_dates[trial]

    spot = csvdata.get_value(contract_params["ticker"], pricing_ts)
    update_dataset(pricing_ts, dataset, spot, contract_params)
    dataset["LV"]["VOL"] = vol

    # create timetable for contract
    timetable = create_timetable(
        pricing_ts, monthend_dates, spot, trial, contract_params
    ).timetable()

    # create forward timetable
    end_dt = timetable["events"]["time"][-1].as_py()
    fwd_timetable = create_forward_timetable(end_dt, contract_params)

    extend_timetable(timetable, fwd_timetable)

    _, stats = model.price(timetable, dataset)

    # Compute net cashflows for original timetable, and the forward timetable
    sums = []
    for i in range(2):
        sum = 0
        for v in stats["CASHFLOW"][i].values():
            sum = sum + v
        sums.append(sum)

    return sums, spot
