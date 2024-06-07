"""
Project Future Cashflows for a given contract.
"""

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

    monthend_datetimes = csvdata.monthend_datetimes(contract_params["ticker"])

    pricing_datetime = monthend_datetimes[trial]
    pricing_ts = int(pricing_datetime.timestamp() * 1000)

    spot = csvdata.get_value(contract_params["ticker"], pricing_datetime)
    update_dataset(pricing_ts, dataset, spot, contract_params)
    dataset["LV"]["VOL"] = vol

    # create timetable for contract
    timetable = create_timetable(
        monthend_datetimes, spot, trial, contract_params
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
